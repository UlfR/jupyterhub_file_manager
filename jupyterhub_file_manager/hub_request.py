import io
from os import environ
import requests
from notebook.utils import url_path_join
import pandas as pd
import base64


def _raw_response(filename, method='GET', data=None):
    hub_api_url = environ.get('JUPYTERHUB_API_URL')
    hub_api_tkn = environ.get('JUPYTERHUB_API_TOKEN')
    url = url_path_join(hub_api_url, 'rawdata/' + filename)
    headers = {
        'Authorization': 'token %s' % hub_api_tkn,
        'Content-Type': 'application/octet-stream'
    }
    try:
        if method == "GET":
            return requests.get(url, headers=headers)
        else:
            return requests.post(url, headers=headers, data=base64.b64encode(data))
    except requests.ConnectionError as e:
        print("Error connecting to %s" % url)
        print(e)
        raise requests.HTTPError(500, e)


def read_binary_data(filename):
    return _raw_response(filename).content


def read_text_data(filename):
    return _raw_response(filename).text


def write_text_data(filename, content, encoding='utf-8'):
    return _raw_response(filename, 'POST', bytes(content, encoding)).text


def write_binary_data(filename, content):
    return _raw_response(filename, 'POST', content).text


def csv_to_pandas_df(filename, **kwargs):
    buf = None
    rdf = None
    try:
        # rsp = _raw_response(filename)
        # csv = rsp.read()
        # buf = io.BytesIO(csv)
        # csv = buf.decode('utf-8')
        raw = read_text_data(filename)
        buf = io.StringIO(raw)
        rdf = pd.read_csv(buf, **kwargs)
    finally:
        if buf:
            try:
                buf.close()
            except:
                pass
    return rdf
