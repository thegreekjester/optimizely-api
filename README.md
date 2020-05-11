# Optimizely API 

This Python package gives an easy way to interface with Optimizely's REST and Event API's. **NOT OFFICIALLY SUPPORTED BY OPTIMIZELY**

## Getting Started

These instructions will get you up and running using this package in your local environment:

### Prerequisites

- [Python 3.0+](https://www.python.org/downloads/)
- [Optimizely Project Bearer Token](https://help.optimizely.com/Integrate_Other_Platforms/Generate_a_personal_access_token_in_Optimizely_X_Web) for REST API use
- [Optimizely Asset ID's](https://help.optimizely.com/Troubleshoot_Problems/API_Names%3A_Find_masked_IDs_for_troubleshooting) for EVENT API use


### Installing

Pip Install the package (Make sure you are using Python 3.0+)

```
pip install optimizelyAPI 
```


## Usage

### Import and Initialize OptlyAPI


```python
from optimizelyAPI import OptlyAPI

"""
Parameters:
    -----------
    accountId: int
        The Account ID you are wishing to access
    projectId: int
        The Project ID you are wishing to access
    token: str (optional)
        The Bearer token used for REST API authentication
        reference here: https://help.optimizely.com/Integrate_Other_Platforms/Generate_a_personal_access_token_in_Optimizely_X_Web
    swaggerURL: str (optional)
        URL for swagger file to help build API client via bravado
        Defaults to https://api.optimizely.com/v2/swagger.json
        https://bravado.readthedocs.io/en/stable/quickstart.html#usage

    """

optly = OptlyAPI(projectId=232235234, accountId=23266677, token='your_bearer_token_here')
```


### REST API 

**TOKEN REQUIRED**

Get Requests (Get assets in a project) via the Optimizely REST API

List of available assets that can be requested: 

- Experiments ('experiments')
- Audiences ('audiences')
- Events ('events')
- Pages ('pages')
- Features ('features')
- Campaigns ('campaigns')


```python

"""
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

    *** Each get request returns an instance of the Response class, 
    you can access the return by using its ".result" attribute ** 
"""

optly.get(['name_of_asset']).result

# e.g optly.get(['events']) or optly.get(['experiments'])
# You can also request multiple asset types at once e.g optly.get(['experiments', 'campaigns'])
```

Filtering Responses:

```python
# Returns a filtered list on any key that is available in the asset payload (e.g "status", "metrics", "id" etc.)

tests = optly.get(['experiments', 'campaigns'], all_asset_data=True)

# All running tests
running_tests = tests.filter({"status":"running"}).result

# All running tests with event ID 124124
tests_with_event124124 = tests.filter({"metrics":"124124"}).result

```

Grab Unique ID's:

```python
# Returns a list of asset ID's that are included in the provided key 

experiments = optly.get(['experiments'], all_asset_data=True)

running_exps = experiments.filter({"status":"running"})

# Grab all audiences used by running experiments
running_exps_audiences = running_exps.list_ids('audience_conditions').result

# Grab all events used by running experiments
running_exps_audiences = running_exps.list_ids('metrics').result

```



### EVENT API

**No Bearer Token Required** 

Will construct and/or send an event payload that follows the Optimizely EVENT API schema 

Assumes the following: 

- Easy Event Tracking (i.e no need for campaign, experiment, or variation ID's)
- Any Tags information is a valid JSON object (i.e not stringified) 
- Any Attributes information is an array of valid JSON objects (i.e not stringified)
- https://optimizely.github.io/docs/api/event/v1/

Ingest CSV/TSV data 

```python

# Read customer data in 
# delimeter either ',' or '\t' 

costumer_data = optly.read_csv('filepath.csv', delimeter=',')

```

Construct Optimizely JSON payload 

```python

"""
Ref: construct_payload method

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

# The column mapping attr is static mapping of column headers from customer data --> optimizely id names
# The keys are optimizely approved, the values are customer specific 
# ** NOTE ** If you don't provide a column mapping, it is assumed you have these exact column names:
# ['visitor_id', 'tags', 'entity_id', 'type', 'timestamp', 'revenue', 'value', 'uuid', 'attributes']
# You can provide less column names (i.e not have revenue, tags, attributes etc shown below)
# Only entity_id, timestamp, and visitor_id columns are required to send events 

column_mapping={'visitor_id':'OPTIMIZELY_ID', 'uuid':'UUID', 
'entity_id': 'ENTITY_ID', 'timestamp':'ENTITY_TS', 'value': 'ENTITY_VALUE'}

# Return the JSON payload
customer_data.construct_payload(column_mapping=column_mapping)

# To send the payload, set the send_events parameter to True in the constuct_payload method
customer_data.construct_payload(column_mapping=column_mapping, send_events=True)

# Convert datetimes into timestamps in milliseconds (if user timestamp data is of datetime type)
customer_data.construct_payload(column_mapping=column_mapping, convert_to_timestamps=True)

# Generate uuids for each event in the payload
customer_data.construct_payload(column_mapping=column_mapping, generate_uuids=True)


```


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


