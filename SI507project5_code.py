## import statements
import json
import webbrowser
import requests_oauthlib
import secret_data
from datetime import datetime
import csv

## CACHING SETUP
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
CACHE_FNAME = 'cache_contents.json'
CREDS_CACHE_FILE = 'creds.json'


try:
    with open(CACHE_FNAME,'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}


try:
    with open(CREDS_CACHE_FILE,'r') as creds_file:
        cache_creds = creds_file.read()
        CREDS_DICTION = json.loads(cache_creds)
except:
    CREDS_DICTION = {}

## Cache functions
def has_expired(timestamp_str, expire_in_days = float('inf')):
    now = datetime.now()
    cache_timestamp = datetime.strptime(timestamp_str,DATETIME_FORMAT)
    delta = now - cache_timestamp
    delta_in_days = delta.days
    if delta_in_days > expire_in_days:
        return True
    else:
        return False

def get_from_cache(identifier,dictionary):
    identifier = identifier.upper()

    if identifier in dictionary:
        data_assoc_dict = dictionary[identifier]
        if has_expired(data_assoc_dict['timestamp'],data_assoc_dict['expire_in_days']):
            del dictionary[identifier]
            data = None
        else:
            data = dictionary[identifier]['values']
    else:
        data = None

    return data

def set_in_data_cache(identifier,data,expire_in_days = float('inf')):
    identifier = identifier.upper()
    CACHE_DICTION[identifier] = {
    'values':data,
    'timestamp':datetime.now().strftime(DATETIME_FORMAT),
    'expire_in_days':expire_in_days
    }

    with open(CACHE_FNAME,'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)

def set_in_creds_cache(identifier,data,expire_in_days = float('inf')):
    identifier = identifier.upper()
    CREDS_DICTION[identifier] = {
    'values':data,
    'timestamp':datetime.now().strftime(DATETIME_FORMAT),
    'expire_in_days':expire_in_days
    }

    with open(CREDS_CACHE_FILE,'w') as cache_file:
        cache_json = json.dumps(CREDS_DICTION)
        cache_file.write(cache_json)

## ADDITIONAL CODE for program should go here...
## Perhaps authentication setup, functions to get and process data, a class definition... etc.
###Private data
CLIENT_KEY = secret_data.client_key
CLIENT_SECRET = secret_data.client_secret

###Specific to APII URLs
REQUEST_TOKEN_URL = 'https://www.tumblr.com/oauth/request_token'
AUTHORIZE_URL = 'https://www.tumblr.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://www.tumblr.com/oauth/access_token'
def get_tokens(client_key = CLIENT_KEY,client_secret = CLIENT_SECRET,request_token_url =REQUEST_TOKEN_URL, base_authorization_url = AUTHORIZE_URL, access_token_url = ACCESS_TOKEN_URL, verifier_auto = False):
    ## go to the ruequest_rul to get an unauthorized token
    oauth_inst = requests_oauthlib.OAuth1Session(client_key,client_secret)
    
    fetch_response = oauth_inst.fetch_request_token(request_token_url)

    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    ## generate an authentication token
    auth_url = oauth_inst.authorization_url(base_authorization_url)

    webbrowser.open(auth_url)

    ## Uses authorizes the reuquest
    if verifier_auto:
        verifier = input('Please input the verifier: ')
    else:
        redirect_result = input('Paste the full redirect URL here: ')
        oauth_resp = oauth_inst.parse_authorization_response(redirect_result)
        verifier = oauth_resp.get('oauth_verifier')

    ## generate an authorized token
    oauth_inst = requests_oauthlib.OAuth1Session(client_key, client_secret=client_secret, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret, verifier=verifier)

    oauth_tokens = oauth_inst.fetch_access_token(access_token_url)

    resource_owner_key, resource_owner_secret = oauth_tokens.get('oauth_token'), oauth_tokens.get('oauth_token_secret')
    
    ## return the authorized token information
    return client_key, client_secret, resource_owner_key, resource_owner_secret, verifier

def get_tokens_from_service(service_name_ident,expire_in_days = float('inf')):
    creds_data = get_from_cache(service_name_ident,CREDS_DICTION)
    if creds_data:
        pass
    else:
        creds_data = get_tokens()
        set_in_creds_cache(service_name_ident,creds_data,expire_in_days = expire_in_days)
    return creds_data

def create_request_identifier(url, params_diction):
    sorted_params = sorted(params_diction.items(),key = lambda x:x[0])
    params_str = '_'.join([str(e) for l in sorted_params for e in l])
    total_ident = url + '?' + params_str
    return total_ident.upper()

def get_data_from_api(request_url, service_ident, params_diction, expire_in_days = float('inf')):
    ident = create_request_identifier(request_url, params_diction)
    data = get_from_cache(ident,CACHE_DICTION)
    if data:
        pass
    else:
        client_key, client_secret, resource_owner_key, resource_owner_secret, verifier = get_tokens_from_service(service_ident)
        oauth_inst = requests_oauthlib.OAuth1Session(client_key, client_secret=client_secret,resource_owner_key=resource_owner_key,resource_owner_secret=resource_owner_secret)

        resp = oauth_inst.get(request_url,params=params_diction)

        data_str = resp.text
        data = json.loads(data_str)
        set_in_data_cache(ident, data, expire_in_days)
    return data

def writer_csv_file(tumblr_results,file_name,parameters = ('post_url','type','date','tags','note_count')):
    with open(file_name,'w',encoding = 'utf-8',newline ='') as csvfile:
        csv_file = csv.writer(csvfile,delimiter =',')
        csv_file.writerow(parameters)
        for item in tumblr_results['response']['posts']:
            csv_file.writerow([item[parameter] for parameter in parameters])





# Make sure to run your code and write CSV files by the end of the program.

if __name__ == '__main__':
    NASA_blog_baseurl = 'https://api.tumblr.com/v2/blog/'+'nasa.tumblr.com/posts'
    elriz_blog_baseurl = 'https://api.tumblr.com/v2/blog/'+'elriz.tumblr.com/posts'
    tumblr_params = {'api_key':CLIENT_KEY,'limit':50}
    
    NASA_result = get_data_from_api(NASA_blog_baseurl,'Tumblr',tumblr_params)
    elriz_result = get_data_from_api(elriz_blog_baseurl,'Tumblr',tumblr_params)

    writer_csv_file(NASA_result,'NASA.csv')
    writer_csv_file(elriz_result,'elriz.csv')
    print(len(NASA_result['response']['posts']))
    print(len(elriz_result['response']['posts']))
    # A = create_request_identifier(tumblr_blog_baseurl, tumblr_blog_params)
