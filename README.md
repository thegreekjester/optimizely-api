# OptlyAPI

This Python package gives an easy way to interface with Optimizely's REST and Event API's. **NOT OFFICIALLY SUPPORTED BY OPTIMIZELY**

## Getting Started

These instructions will get you up and running using this package in your local environment:

### Prerequisites

- [Python 3.0+](https://www.python.org/downloads/)
- [Optimizely Project Bearer Token](https://help.optimizely.com/Integrate_Other_Platforms/Generate_a_personal_access_token_in_Optimizely_X_Web)
- [Optimizely Asset ID's](https://help.optimizely.com/Troubleshoot_Problems/API_Names%3A_Find_masked_IDs_for_troubleshooting)


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
tests = optly.get(['experiments', 'campaigns'])

# All running tests
running_exps_everyone = tests.filter({"status":"running"}).result

# All running tests with event ID 124124
experiments_with_event124124 = experiments.filter({"metrics":"124124"}).result

```

Grab Unique ID's:

```python
experiments = optly.get(['experiments'])

running_exps = experiments.filter({"status":"running"})

# Grab all audiences used by running experiments
running_exps_audiences = running_exps.list_ids('audience_conditions').result

# Grab all events used by running experiments
running_exps_audiences = running_exps.list_ids('metrics').result

```



### EVENT API

Ingest CSV/TSV data 

```python
"""
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
# Read customer data in 

optly.read_csv('filepath.csv', delimeter=',')
```

Construct Optimizely JSON payload 

```python
# construct the Optimizely approved JSON payload

customer_data = optly.read_csv('filepath.csv', delimeter=',')

# The column mapping gives a static mapping of column headers from customer data --> Optimizely
# The keys are Optimizely approved, the values are customer specific 

column_mapping={'visitor_id':'OPTIMIZELY_ID', 'uuid':'UUID', 
'entity_id': 'ENTITY_ID', 'timestamp':'ENTITY_TS', 'value': 'ENTITY_VALUE'}

# Return the JSON payload
customer_data.construct_payload(column_mapping=column_mapping)

# To send the payload, set the send_events parameter to True in the constuct_payload method
customer_data.construct_payload(column_mapping=column_mapping, send_events=True)

# Convert datetimes into timestamps in milliseconds (if customer times are of datetime type)
customer_data.construct_payload(column_mapping=column_mapping, convert_to_timestamps=True)

# Generate uuids for each event in the payload
customer_data.construct_payload(column_mapping=column_mapping, generate_uuids=True)


```


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


