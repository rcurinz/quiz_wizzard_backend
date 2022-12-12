from flask import json, current_app
from hashids import Hashids
from . import db


class Model(db.Model):
    __abstract__ = True

    def __init__(self, **kwargs):
        kwargs['_force'] = True
        self._set_columns(**kwargs)

    def update(self, included=None, omitted=None, **kwargs):
        if included:
            kwargs['_included'] = included
        if omitted:
            kwargs['_omitted'] = omitted
        self._set_columns(**kwargs)

    def _set_columns(self, **kwargs):
        force = kwargs.get('_force')
        readonly = []

        id_key = getattr(self, '_primary', 'id')
        if hasattr(self, 'hidden_fields'):
            readonly += self.hidden_fields
        if hasattr(self, 'read_fields'):
            readonly += self.read_fields

        included = kwargs.get('_included', [])
        for inc in included:
            readonly.remove(inc)

        omitted = kwargs.get('_omitted', [])
        for om in omitted:
            readonly.append(om)

        readonly += [id_key, 'created_at', 'updated_at']

        columns = self.__table__.columns.keys()
        properties = dir(self)

        for key in columns:
            allowed = True if force or key not in readonly else False
            exists = True if key in kwargs else False
            if allowed and exists:
                val = getattr(self, key)
                if val != kwargs[key]:
                    setattr(self, key, kwargs[key])

        for key in list(set(properties) - set(columns)):
            if key.startswith('_'):
                continue
            allowed = True if force or key not in readonly else False
            exists = True if key in kwargs else False
            if allowed and exists:
                try:
                    val = getattr(self, key)
                    if isinstance(getattr(self, key), property) and val != kwargs[key]:
                        setattr(self, key, kwargs[key])
                except AttributeError:
                    setattr(self, key, kwargs[key])
                except:
                    pass

    def __repr__(self):
        ret_data = {}

        hidden = []
        if hasattr(self, 'hidden_fields'):
            hidden = self.hidden_fields

        for key in self.__table__.columns.keys():
            if key not in hidden:
                ret_data[key] = getattr(self, key)

        ret_string = ', '.join(['%s: %s' % (key, value) for (key, value) in ret_data.items()])
        return "<%s: %s>" % (self.__class__.__name__, ret_string)

    def to_dict(self, show=None, hide=None, path=None, show_all=None):
        if not show:
            show = []
        if not hide:
            hide = []

        id_key = getattr(self, '_primary', 'id')
        hidden = []
        if hasattr(self, 'hidden_fields'):
            hidden = self.hidden_fields

        default = []
        if hasattr(self, 'default_fields'):
            default = self.default_fields

        own = ['query', 'hidden_fields', 'default_fields', 'read_fields']

        ret_data = {}
        _classname = self.__class__.__name__.lower()

        if not path:
            path = _classname

            def prepend_path(item):
                # item = item.lower()
                if item.split('.', 1)[0] == path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != '.':
                    item = '.%s' % item
                    item = '%s%s' % (path, item)
                    return item

            show[:] = [prepend_path(x) for x in show]
            hide[:] = [prepend_path(x) for x in hide]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        for key in columns:
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or key is id_key or check in show or key in default:
                ret_data[key] = getattr(self, key)

        if not _classname in hide:
            hide.append(_classname)
        hide[:0] = hidden

        for key in relationships:
            rec_hide = list(hide)
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden or key in hide:
                continue
            if not key in hide:
                rec_hide.append(key)
            if show_all or check in show or key in default:
                if self.__mapper__.relationships[key].uselist:
                    ret_data[key] = []
                    for item in getattr(self, key):
                        ret_data[key].append(item.to_dict(show=show, hide=rec_hide, \
                                                          path=('%s.%s' % (path, key.lower())), \
                                                          show_all=show_all))
                else:
                    if self.__mapper__.relationships[key].query_class is not None:
                        if getattr(self, key) is not None:
                            ret_data[key] = getattr(self, key).to_dict(show=show, hide=rec_hide, \
                                                                       path=('%s.%s' % (path, key.lower())), \
                                                                       show_all=show_all)
                    else:
                        ret_data[key] = getattr(self, key)
            rec_hide = []

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith('_'):
                continue
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden or key in own:
                continue
            if show_all or check in show or key in default:
                val = getattr(self, key)
                try:
                    ret_data[key] = json.loads(json.dumps(val))
                except:
                    pass

        return ret_data


class Hashable(object):
    def _hashed_id(self):
        h = Hashids(min_length=6, alphabet=current_app.config['HASHID_ALPHABET'],
                    salt=current_app.config['HASHID_SECRET_KEY'])
        return h.encode(self.id)

    @staticmethod
    def unhash_code(code):
        h = Hashids(min_length=6, alphabet=current_app.config['HASHID_ALPHABET'],
                    salt=current_app.config['HASHID_SECRET_KEY'])
        return h.decode(code)


class BaseConstant(object):
    _messages = dict()
    _constants = dict()

    def __init__(self, model, messages=dict(), constants=dict()):
        self._classname = model
        if isinstance(messages, dict):
            self._messages = messages
        if isinstance(constants, dict):
            self._constants = constants

    @property
    def FORBIDDEN(self):
        return "Sin permisos suficientes"

    @property
    def NONEXISTING(self):
        return "No existe " + self._classname

    @property
    def EXISTING(self):
        return "Ya existe " + self._classname

    @property
    def CREATED(self):
        return self._classname + " creado correctamente"

    @property
    def EDITED(self):
        return self._classname + " editado correctamente"

    @property
    def DELETED(self):
        return self._classname + " eliminado correctamente"

    @property
    def GENERIC_ERROR(self):
        return "[" + self._classname + "] Error Interno"

    @property
    def MISSING_PARAMS(self):
        return "Faltan Parametros"

    def __getattr__(self, name):
        if name in self._messages:
            try:
                return self._messages[name] % {'classname': self._classname}
            except KeyError as exc:
                # TODO: LOG ERROR
                return self._messages[name]
        elif name in self._constants:
            return self._constants[name]
        else:
            return object.__getattribute__(self, name)