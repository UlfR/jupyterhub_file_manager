from jupyterhub.apihandlers import APIHandler
from notebook.services.contents.filemanager import FileContentsManager
from notebook.services.contents.filecheckpoints import FileCheckpoints
from notebook.services.contents.handlers import ContentsHandler
from notebook.services.contents.handlers import CheckpointsHandler
from notebook.services.contents.handlers import ModifyCheckpointsHandler

# FIXME move to settings
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
