import pdb
# noinspection PyUnresolvedReferences
import posix1e
import os
import base64
from jupyterhub.apihandlers import APIHandler
from notebook.services.contents.filemanager import FileContentsManager
from notebook.services.contents.handlers import ContentsHandler
from notebook.services.contents.handlers import CheckpointsHandler
from notebook.services.contents.handlers import ModifyCheckpointsHandler
from tornado import gen, web
from tornado.log import app_log

# FIXME read from settings
BASE_ROOT = '/tmp/notebooks/'


# FIXME trash support
class DBNotebookManager(FileContentsManager):
    user = None

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    @property
    def user_name(self):
        return self.user.name if self.user else 'anonymous'

    # FIXME get group names
    @property
    def group_names(self):
        return ['fixme']

    @property
    def root_dir(self):
        return BASE_ROOT

    @property
    def home_dir(self):
        return f'{BASE_ROOT}/{self.user.name}/'

    # FIXME chown on file
    def set_ownership(self, os_path):
        pass

    # noinspection PyMethodMayBeStatic
    def get_acl(self, os_path):
        acl = posix1e.ACL(file=os_path)
        acl_str = acl.to_any_text(separator=b';').decode('utf-8')
        return list(map(lambda a: a.split(':'), acl_str.split(';')))

    # FIXME ids to names
    # noinspection PyMethodMayBeStatic
    def get_path_owner(self, os_path):
        statinfo = os.stat(os_path)
        uid = statinfo.st_uid
        gid = statinfo.st_gid
        return [uid, gid]

    def is_path_in_root(self, os_path):
        abs_path = os.path.abspath(os_path)
        return os.path.commonprefix([self.root_dir, abs_path]) == self.root_dir

    def is_path_in_home(self, os_path):
        abs_path = os.path.abspath(os_path)
        return os.path.commonprefix([self.home_dir, abs_path]) == self.home_dir

    def get_path_permissions(self, os_path):
        user_name = self.user_name
        user_groups = self.group_names
        owner_user, owner_group = self.get_path_owner(os_path)
        acls = self.get_acl(os_path)

        result = '---'
        for acl in acls:
            acl_type, acl_object, acl_permissions = acl
            if acl_object == '' and acl_type == 'user' and user_name == owner_user:
                result = acl_permissions
                break
            if acl_object == '' and acl_type == 'group' and (owner_group in user_groups):
                result = acl_permissions
                break
            if acl_type == 'user' and user_name == acl_object:
                result = acl_permissions
                break
            if acl_type == 'group' and (acl_object in user_groups):
                result = acl_permissions
                break
            if acl_type == 'other':
                result = acl_permissions
                break

        return {
            'r': result[0] == 'r',
            'w': result[1] == 'w',
            'x': result[2] == 'x',
        }

    def is_path_accessible_for(self, os_path, access_type):
        if not self.is_path_in_root(os_path):
            return False

        permissions = self.get_path_permissions(os_path)
        return permissions[access_type]

    def is_path_accessible_for_read(self, os_path):
        return self.is_path_accessible_for(os_path, 'r')

    def is_path_accessible_for_write(self, os_path):
        return self.is_path_accessible_for(os_path, 'w')

    def is_path_accessible_for_execute(self, os_path):
        return self.is_path_accessible_for(os_path, 'x')

    # FIXME, add/change acl
    def share(self, path, user, rights='r--'):
        pass

    # FIXME, remove acl
    def unshare(self, path, user):
        pass

    # FIXME check user rights
    def get_raw(self, path):
        path = path.strip('/')
        os_path = self._get_os_path(path)
        if not os.path.isfile(os_path):
            raise web.HTTPError(400, "Cannot read non-file %s" % os_path)
        with self.open(os_path, 'rb') as f:
            content = f.read()
        # return content.decode('utf8'), 'text'
        return content

    # FIXME check user rights
    def save_raw(self, path, content):
        path = path.strip('/')
        os_path = self._get_os_path(path)
        # FIXME mkdir`s
        with self.atomic_writing(os_path, text=False) as f:
            f.write(content)

    def _read_notebook(self, os_path, as_version=4):
        if not self.is_path_accessible_for_read(os_path):
            raise web.HTTPError(403, 'Permission denied')
        return super()._read_notebook(os_path, as_version)

    def _read_file(self, os_path, format):
        if not self.is_path_accessible_for_read(os_path):
            raise web.HTTPError(403, 'Permission denied')
        return super()._read_file(os_path, format)

    # FIXME if exists then check for write, if not then check for write on dir
    def _save_notebook(self, os_path, nb):
        if not self.is_path_accessible_for_write(os_path):
            raise web.HTTPError(403, 'Permission denied')
        return super()._save_notebook(os_path, nb)

    # FIXME if exists then check for write, if not then check for write on dir
    def _save_file(self, os_path, content, format):
        if not self.is_path_accessible_for_write(os_path):
            raise web.HTTPError(403, 'Permission denied')
        return super()._save_file(os_path, content, format)

    # FIXME if exists then check for write, if not then check for write on dir
    def _copy(self, src, dest):
        if not self.is_path_accessible_for_read(src):
            raise web.HTTPError(403, 'Permission denied')
        if not self.is_path_accessible_for_write(dest):
            raise web.HTTPError(403, 'Permission denied')
        return super()._copy(src, dest)

    # FIXME
    def _save_directory(self, os_path, model, path=''):
        pass

    # FIXME
    def delete_file(self, path):
        pass

    # FIXME
    def rename_file(self, old_path, new_path):
        pass

    # FIXME + param to not raise 403 but return None or use _base_model
    def _notebook_model(self, path, content=True):
        pass

    # FIXME + param to not raise 403 but return None or use _base_model
    def _file_model(self, path, content=True, format=None):
        pass

    # FIXME + param to not raise 403 but return None or use _base_model
    def _dir_model(self, path, content=True):
        pass

    # FIXME + param to not raise 403 but return None or use _TYPE_model
    def _base_model(self, path):
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
