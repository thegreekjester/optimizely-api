# Conda environment is optlyAPI

from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
import warnings
from .responses import Response
from pandas import read_csv 
import requests

class OptlyAPI:

    """
    The OptlyAPI class gives an accesible wrapper to interact with Optimizely Rest & Event APIs

    Parameters:
    -----------
    accountId: int
        The Account ID you are wishing to access

    projectId: int
        The Project ID you are wishing to access

    token: str (optional)
        The Bearer token used for REST API authentication
        reference here: https://help.optimizely.com/Integrate_Other_Platforms/Generate_a_personal_access_token_in_Optimizely_X_Web

    swaggerURL: str
        URL for swagger file to help build API client via bravado
        https://bravado.readthedocs.io/en/stable/quickstart.html#usage
    """

    def __init__(self, accountId, projectId, token=False, swaggerURL='https://api.optimizely.com/v2/swagger.json'):

        """
        Please refer to help(OptlyAPI) for more information
        """
        
        warnings.simplefilter("ignore") # not log schema validation warnings

        self.accountId = accountId
        self.projectId = projectId
        self.swaggerURL = swaggerURL
        self.config = {'use_models': False, 'validate_responses': False, 'validate_requests':False}
        self.token = token
        if token:
            # applying authentication to all future requests for REST API
            self.http_client = RequestsClient()
            self.http_client.set_api_key(
                'api.optimizely.com', token,
                param_name='Authorization', param_in='header'
                        )
            self.client = SwaggerClient.from_url(swaggerURL, http_client=self.http_client, config=self.config) # creating bravado client from swagger.json
        else:
            self.client = SwaggerClient.from_url(swaggerURL, config=self.config) # creating bravado client from swagger.json if no token provided


    def read_csv(self, file_path, delimiter=','):
        """
        The read_csv method wraps the pandas read_csv method and makes it possible to read in csv/tsv. This method returns an instance
        of the Response class.

        Parameters:
        -----------

        file_path: str 
            CSV/TSV data filepath

        delimiter: str
            The delimiter between data columns, denotes CSV (,) or TSV (\t)
        """
        df = read_csv(file_path, delimiter=delimiter) # read in the csv/tsv data 
        response = Response(df, self.accountId)

        return response

    def get(self, type_list, all_asset_data=False, include_archived=False):
        """
        Fetch Optimizely assets using via REST API

        Parameters:
        -----------

        type_list: list
            List of strings denoting what kind of assets to fetch 

        all_asset_data: bool
            Denote whether or not to fetch the full asset data payload or just the trimmed versioning (search api)
            (Default): True 

        include_archived:bool
            Denote whether to include archived assets 
            (Default): False
        """
        # Initial variables 
        response = []
        headers = {'Authorization': self.token}
        page=1
        per_page= 100
        r_done = False 
        r2_done = not include_archived

        # constructing base URL and all the types you want to query for
        url = 'https://api.optimizely.com/v2/search?&project_id={}&per_page={}&query'.format(self.projectId,per_page)
        for t in type_list:
            url += '&type={}'.format(t[:-1]) 

        # dictionary of swagger defined methods to fetch assets by id 
        id_dict = {

                            "audience": (getattr(self.client.Audiences, 'get_audience'), 'audience_id'),
                            "campaign": (getattr(self.client.Campaigns, 'get_campaign'), 'campaign_id'),
                            "event": (getattr(self.client.Events, 'get_event'), 'event_id'),
                            "experiment": (getattr(self.client.Experiments, 'get_experiment'), 'experiment_id'),
                            "feature": (getattr(self.client.Features, 'get_feature'), 'feature_id'),
                            "page": (getattr(self.client.Pages, 'get_page'), 'page_id')

                        }        
  
        while True:

            r_total_json=[]

            if not r_done: #grabbing non archived assets here
                r = requests.get(url + '&page={}'.format(page), headers=headers)
                r_total_json += r.json()
                r_done = 'Link' not in r.headers or 'rel=last' not in r.headers['Link']

            if not r2_done: # grabbing the archived assets here (if necessary)
                r2 = requests.get(url + '&archived=True&page={}'.format(page), headers=headers)
                r_total_json += r2.json()
                r2_done = 'Link' not in r2.headers or 'rel=last' not in r2.headers['Link']

            if all_asset_data: # We want full asset payload 
                asset_list = [(int(x['id']), x['type']) for x in r_total_json]

                # had to use a for loop here because in sub Python 3.8 you can't assign a local variable within list comprehension
                for asset in asset_list:
                    params = {id_dict[asset[1]][1]:asset[0]}
                    response.append(id_dict[asset[1]][0](**params).response().result)

            else: # Just want search_api response types
                response += r_total_json
            

            if r_done and r2_done: # when both archived and non-archived have reached final page, exit while loop
                break

            page +=1 # get next page if no break
        
        response = Response(response) # convert list of dicts to Response class instance 

        return response