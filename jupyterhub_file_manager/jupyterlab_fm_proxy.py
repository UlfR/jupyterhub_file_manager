from os import environ
from tornado import gen, web
from tornado.log import app_log
from tornado.web import HTTPError
from notebook.utils import url_path_join, maybe_future
from notebook.base.handlers import APIHandler, path_regex
import requests


# noinspection PyAbstractClass
class ProxyHandler(APIHandler):
    @gen.coroutine
    def proxy(self):
        request = self.request
        body = request.body
        hub_api_url = environ.get('JUPYTERHUB_API_URL')
        url = url_path_join(hub_api_url, 'notebooks/'+request.uri.split('contents/')[1])
        if request.method == "GET":
            response = yield maybe_future(self._api_request(method=request.method, url=url))
        else:
            response = yield maybe_future(self._api_request(method=request.method, url=url, data=body))
        self.set_status(response.status_code)
        self.finish(response.text)

    @gen.coroutine
    def _api_request(self, method, url, **kwargs):
        hub_auth = self.application.settings['hub_auth']
        headers = kwargs.setdefault('headers', {})
        headers.setdefault('Authorization', 'token %s' % hub_auth.api_token)
        if "cert" not in kwargs and hub_auth.certfile and hub_auth.keyfile:
            kwargs["cert"] = (hub_auth.certfile, hub_auth.keyfile)
            if hub_auth.client_ca:
                kwargs["verify"] = hub_auth.client_ca
        try:
            r = requests.request(method, url, **kwargs)
        except requests.ConnectionError as e:
            app_log.error("Error connecting to %s: %s", hub_auth.api_url, e)
            msg = "Failed to connect to Hub API at %r." % hub_auth.api_url
            raise HTTPError(500, msg)
        return r


# noinspection PyAbstractClass
class ContentsHandler(ProxyHandler):
    @web.authenticated
    @gen.coroutine
    def get(self, path=''):
        return self.proxy()

    @web.authenticated
    @gen.coroutine
    def patch(self, path=''):
        return self.proxy()

    @web.authenticated
    @gen.coroutine
    def post(self, path=''):
        return self.proxy()

    @web.authenticated
    @gen.coroutine
    def put(self, path=''):
        return self.proxy()

    @web.authenticated
    @gen.coroutine
    def delete(self, path=''):
        return self.proxy()


# noinspection PyAbstractClass
class CheckpointsHandler(ProxyHandler):
    @web.authenticated
    @gen.coroutine
    def get(self, path=''):
        return self.proxy()

    @web.authenticated
    @gen.coroutine
    def post(self, path=''):
        return self.proxy()


# noinspection PyAbstractClass
class ModifyCheckpointsHandler(ProxyHandler):
    @web.authenticated
    @gen.coroutine
    def post(self, path, checkpoint_id):
        return self.proxy()

    @web.authenticated
    @gen.coroutine
    def delete(self, path, checkpoint_id):
        return self.proxy()


# noinspection PyAbstractClass
class NotebooksRedirectHandler(ProxyHandler):
    SUPPORTED_METHODS = ('GET', 'PUT', 'PATCH', 'POST', 'DELETE')

    def get(self, path):
        return self.proxy()

    put = patch = post = delete = get


# noinspection PyAbstractClass
class TrustNotebooksHandler(ProxyHandler):
    @web.authenticated
    @gen.coroutine
    def post(self, path=''):
        return self.proxy()


_checkpoint_id_regex = r"(?P<checkpoint_id>[\w-]+)"
default_handlers = [
    (r"/api/contents%s/checkpoints" % path_regex, CheckpointsHandler),
    (r"/api/contents%s/checkpoints/%s" % (path_regex, _checkpoint_id_regex), ModifyCheckpointsHandler),
    (r"/api/contents%s/trust" % path_regex, TrustNotebooksHandler),
    (r"/api/contents%s" % path_regex, ContentsHandler),
    (r"/api/notebooks/?(.*)", NotebooksRedirectHandler),
]
