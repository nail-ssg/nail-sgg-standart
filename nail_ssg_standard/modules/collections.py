# from nail_ssg_base.prints import *
from nail_ssg_base.modules.baseplugin import BasePlugin
from functools import cmp_to_key
from locale import strcoll


def i(col_name):
    def x(item):
        return str(item.get(col_name, ''))
    return x


def multikeysort(items, columns):
    columns = [
        col[1:].strip() if col.startswith('+') else col.strip()
        for col in columns
    ]
    comparers = [
        ((i(col[1:]), -1) if col.startswith('-') else (i(col), 1))
        for col in columns
    ]

    def comparer(left, right):
        comparer_iter = (
            strcoll(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    return sorted(items, key=cmp_to_key(comparer))


class Collections(BasePlugin):
    _default_config = {
        '30. modify': {
            'order': ['nail_ssg_standard.collections']
        }
    }
    _config_comments = {}    # dict

    def init(self):
        pass

    def modify_data(self):
        data_dict = self.config.data
        self.collections = {}
        for key in data_dict:
            data = data_dict[key]
            is_abstract = data.get('$global', {'abstract': False}).get('abstract', False)
            if is_abstract:
                continue
            coll_names = data.get('$global', {'collections': []}).get('collections', [])
            for collection in coll_names:
                if collection not in self.collections:
                    self.collections[collection] = []
                self.collections[collection] += [data]
        for key in data_dict:
            data = data_dict[key]
            self.local_modify(data)

    def local_modify(self, data):
        collections = data.get('$local', {'collections': None}).get('collections', None)
        collections = self.collections if collections is None else collections
        uses = data.get('$local', {'use': {}}).get('use', {})
        for use_key in uses:
            use = uses[use_key]
            if use is None:
                continue
            for param in ['from', 'sort']:
                if param not in use:
                    raise AttributeError('For option "use" need param "{}"'.format(param))
            collection = collections.get(use.get('from', ''), [])
            sort_keys = use.get('sort', [])
            coll = multikeysort(collection, sort_keys)
            data[use_key] = coll

    def build(self):
        pass


def create(config):
    return Collections(config)
