# import pdb
import json
from os import environ
from tornado import gen, web
from jupyter_client.jsonutil import date_default
from notebook.utils import url_path_join, maybe_future
from notebook.base.handlers import APIHandler, path_regex


# noinspection PyAbstractClass
class ProxyHandler(APIHandler):
    # FIXME
    @gen.coroutine
    def proxy(self):
        request = self.request
        body = request.body
        # pdb.set_trace()
        print({'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz, request': request, 'method': request.method, 'body': body})

        hub_auth = self.application.settings['hub_auth']
        hub_api_url = environ.get('JUPYTERHUB_API_URL')
        url = url_path_join(hub_api_url, 'notebooks/'+request.uri.split('contents/')[1])
        print({'qqqqqqqqqqqqqqqqqqqqqqqqq': url})

        statuses = {
            "POST": 201,
            "PUT": 201,
            "DELETE": 204,
            "GET": 200,
        }
        print('ESHKERE',hub_auth)

        #print('ESHKERE', hub_auth._api_request(method=request.method, url=url, data=body))
        # noinspection PyProtectedMember
        if request.method == "GET":
            model = yield maybe_future(hub_auth._api_request(method=request.method, url=url))
        else:
            model = yield maybe_future(hub_auth._api_request(method=request.method, url=url, data=body))

        #print('_______MODEL',  model)
        self.set_status(statuses[request.method])
        self.finish(json.dumps(model, default=date_default))


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
        print('CheckpointsHandler__________________________', path)
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
