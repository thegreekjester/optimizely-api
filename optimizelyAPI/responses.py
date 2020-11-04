import pandas as pd
import numpy as np
import json
import requests
import re
import math 
import uuid

class Response:
    """
    The Response class holds the response payload from an OptlyAPI class instance request

    Parameters:
    -----------
    response: obj
        Response of a request from a instance of the OptlyAPI class

    accountId: int (optional)
        Optimizely account ID, used for sending events via the Event API

    """
    def __init__(self, response, accountId=False):
        """
        Please refer to help(Response) for more infomration
        """
        self.result = response 
        self.accountId = accountId

    def filter(self, filter_dict):
        """
        The filter method filters the response from the client based on the filter_dict

        Parameters:
        -----------
        filter_dict: (dict
            Dictionary to filter API response
            example: {'audience_conditions': 'everyone', 'status':'paused'} --> grab only experiments with these conditions
        """
        self.result = [x for x in self.result if all(str(x[y]) == z or (hasattr(x[y], "__iter__") and (z in str(x[y]) or any(z in str(d.values) for d in x[y] if isinstance(d, dict)))) for y,z in filter_dict.items())] 

        return self


    def construct_payload(self, column_mapping={}, client_name='optly_api', client_version='0.1', enrich_decisions=True, send_events=False, convert_to_timestamps=False, generate_uuids=False):
        """
        The construct_payload method takes user event data and constructs a JSON object that follows the Optimizely Event API schema
        https://optimizely.github.io/docs/api/event/v1/

        Parameters:
        -----------

        column_mapping: dict
            Dictionary of column mappings that correspond to the predefined Event API schema (see above reference)

        client_name: str (default value: 'optly_api')
            Name of client that sends off the events via the Event API
            
        client_version: str (default value: '0.1')
            Version of client 

        send_events: bool (default value: False)
            Flag to denote whether to send off the json payload returned by this method to Optimizely's events endpoint

        convert_to_timestamps: bool (default value: False)
            Flag to denote whether to convert timestamp column of type datetime to timestamps of milliseconds

        generate_uuids: bool (default value: False)
            Flag to denote whether to generate uuids for each event sent

        """

        values = ['visitor_id', 'tags', 'entity_id', 'type', 'timestamp', 'revenue', 'value', 'uuid', 'attributes']

        # Convert the columns of the ingested CSV/TSV to Optimizely recognized headers
        if column_mapping:
            initial_mapping = dict(zip(values, values))
            for i,j in column_mapping.items():
                initial_mapping[i] = j
            final_mapping = {v: k for k, v in initial_mapping.items()}
            self.result = self.result.rename(columns=final_mapping)
        
        if convert_to_timestamps: # Convert datetime to timestamps in milleseconds
            self.result['timestamp'] = pd.to_datetime(self.result['timestamp']).values.astype(np.int64) / 1000

        # Constructing event payload
        event_payload = {
                            "account_id": str(self.accountId),
                            "visitors":[],
                            "anonymize_ip": True, 
                            "client_name": str(client_name), 
                            "client_version": str(client_version), 
                            "enrich_decisions": enrich_decisions
                        }

        if 'attributes' in self.result.columns and not self.result['attributes'].isnull().all():
            tuples_list = list(zip(self.result['visitor_id'], self.result['attributes']))
            unique_tuples = [t for t in (set(tuple(i) for i in tuples_list))] # unique tuples of visitor_id and attribute value
            for x in unique_tuples:
                event_payload['visitors'].append(self._construct_visitor_obj(x[0], self.result.loc[(self.result['visitor_id'] == x[0]) & (self.result['attributes'] == x[1])], attributes=x[1], generate_uuids=generate_uuids))
        else:
            unique_visitors = self.result['visitor_id'].unique() # unique Optimizely visitor ID's 

            for x in unique_visitors:
                event_payload['visitors'].append(self._construct_visitor_obj(x, self.result.loc[self.result['visitor_id'] == x], generate_uuids=generate_uuids))

        json_payload = json.dumps(event_payload)

        status_code = "Payload not sent"

        if send_events:
            r = requests.post('https://logx.optimizely.com/v1/events', data = json_payload)
            status_code = "Status Code: {}".format(r.status_code)
            
        return (status_code,json_payload)


    def list_ids (self, key):

        """
        This method returns a Response instance that contains a list of unique Optimizely ID's that are found in an array of Optimizely assets

        Parameters:
        -----------

        key: str 
        The key in the Optimizely asset object to find unique ids (e.g page_ids, audience_conditions etc.)
        """

        list_of_key_values = [str(x[key]) for x in self.result]

        self.result = list(dict.fromkeys([re.findall(r'\b\d+\b', x)[0] for x in list_of_key_values if len(re.findall(r'\b\d+\b', x)) !=0]))

        return self 
        


    def _construct_visitor_obj(self, visitor_id, df_slice, generate_uuids=False, attributes=False):

        """
        Internal method, only to be used by the class itself. NOT FOR PUBLIC USE
        """
    
        visitor_obj = {"visitor_id":visitor_id, "attributes":json.loads(attributes)} if attributes else {"visitor_id":visitor_id}
        
        events_array = []
        sig_types = ['revenue', 'value', 'tags', 'entity_id', 'timestamp']

        for _, row in df_slice.iterrows():
            args = {}
            for s in sig_types:
                val = False
                if s in row and not pd.isnull(row[s]):
                    val = row[s]
                args[s] = val
            if generate_uuids:
                args['uuid'] = uuid.uuid1()
            else:
                args['uuid'] = row['uuid']
            events_array.append(getattr(self, '_construct_event_obj')(**args))
                

        visitor_obj["snapshots"] = [{"decisions":[], "events":events_array}]

        return visitor_obj

    
    def _construct_event_obj(self,entity_id, timestamp, uuid, value, tags, revenue):

        """
        Internal method, only to be used by the class itself. NOT FOR PUBLIC USE
        """

        event_obj = {
                        "entity_id": str(entity_id), 
                        "timestamp": int(timestamp), 
                        "uuid": str(uuid), 
                    }
        if revenue is not False: 
            event_obj['revenue'] = int(revenue) 
        if value is not False: 
            event_obj['value'] = float(value)
        if tags is not False:
            event_obj['tags'] = json.loads(tags)
        
        return event_obj