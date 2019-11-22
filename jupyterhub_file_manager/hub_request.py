# noinspection PyUnresolvedReferences
import pdb
import json
from os import environ

import requests
from jupyter_client.jsonutil import date_default
from notebook.utils import url_path_join, maybe_future
from tornado import gen


# @gen.coroutine
def get_file_from_hub(filename):
    # pdb.set_trace()
    hub_api_url = environ.get('JUPYTERHUB_API_URL')
    url = url_path_join(hub_api_url, 'notebooks/' + filename)  # + type etc
    model = (_api_request(method='GET', url=url))
    print(model)
    # print(json.dumps(model['data'], default=date_default))
    return model


# @gen.coroutine
def _api_request(method, url):
    hub_api_tkn = environ.get('JUPYTERHUB_API_TOKEN')
    headers = {'Authorization': 'token %s' % hub_api_tkn}
    try:
        response = requests.request(method, url, headers=headers)
    except requests.ConnectionError as e:
        print("Error connecting to %s" % url)
        print(e)
        raise requests.HTTPError(500, e)

    print(response)
    data = response.json()
    return data
