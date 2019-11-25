import os
import base64
from jupyterhub.apihandlers import APIHandler
from notebook.services.contents.filemanager import FileContentsManager
from notebook.services.contents.handlers import ContentsHandler
from notebook.services.contents.handlers import CheckpointsHandler
from notebook.services.contents.handlers import ModifyCheckpointsHandler
from tornado import gen, web

# FIXME read from settings
BASE_ROOT = '/tmp/notebooks/'


class DBNotebookManager(FileContentsManager):
    user = None

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    @property
    def root_dir(self):
        return f'{BASE_ROOT}/{self.user.name}/'

    # FIXME, rwsx
    def share(self, path, user, rights='r'):
        pass

    # FIXME
    def unshare(self, path, user):
        pass

    #FIXME check user rights
    def get_raw(self, path):
        path = path.strip('/')
        os_path = self._get_os_path(path)
        if not os.path.isfile(os_path):
            raise web.HTTPError(400, "Cannot read non-file %s" % os_path)
        with self.open(os_path, 'rb') as f:
            content = f.read()
        # return content.decode('utf8'), 'text'
        return content

    #FIXME check user rights
    def save_raw(self, path, content):
        path = path.strip('/')
        os_path = self._get_os_path(path)
        #FIXME mkdir`s
        with self.atomic_writing(os_path, text=False) as f:
            f.write(content)


# noinspection PyAbstractClass
class NotebooksAPIHandler(APIHandler, ContentsHandler):
    db_nm = None

    @property
    def contents_manager(self):
        user = self.current_user
        if user is None:
            user = 'anonymous'
        if self.db_nm is None or (
                self.db_nm.user and self.db_nm.user != 'anonymous' and
                user != 'anonymous' and self.db_nm.user.name != user.name
        ):
            self.db_nm = DBNotebookManager(user=user)
        return self.db_nm


# noinspection PyAbstractClass
class RawDataHandler(APIHandler, ContentsHandler):
    db_nm = None

    @property
    def contents_manager(self):
        user = self.current_user
        if user is None:
            user = 'anonymous'
        if self.db_nm is None or (
                self.db_nm.user and self.db_nm.user != 'anonymous' and
                user != 'anonymous' and self.db_nm.user.name != user.name
        ):
            self.db_nm = DBNotebookManager(user=user)
        return self.db_nm

    @web.authenticated
    @gen.coroutine
    def get(self, path=''):
        path = path or ''
        data = self.contents_manager.get_raw(path)
        self.finish(data)

    @web.authenticated
    @gen.coroutine
    def post(self, path=''):
        path = path or ''
        content = self.request.body
        # content = content.encode('utf8')
        content = base64.b64decode(content)
        self.contents_manager.save_raw(path, content)
        # self.finish(data)


# noinspection PyAbstractClass
class CheckpointsAPIHandler(APIHandler, CheckpointsHandler):
    db_nm = None

    @property
    def contents_manager(self):
        user = self.current_user
        if user is None:
            user = 'anonymous'
        if self.db_nm is None or (
                self.db_nm.user and self.db_nm.user != 'anonymous' and
                user != 'anonymous' and self.db_nm.user.name != user.name
        ):
            self.db_nm = DBNotebookManager(user=user)
        return self.db_nm


# noinspection PyAbstractClass
class ModifyCheckpointsAPIHandler(APIHandler, ModifyCheckpointsHandler):
    db_nm = None

    @property
    def contents_manager(self):
        user = self.current_user
        if user is None:
            user = 'anonymous'
        if self.db_nm is None or (
                self.db_nm.user and self.db_nm.user != 'anonymous' and
                user != 'anonymous' and self.db_nm.user.name != user.name
        ):
            self.db_nm = DBNotebookManager(user=user)
        return self.db_nm
