from nail_ssg_base.modules.baseplugin import BasePlugin


class Collections(BasePlugin):
    _default_config = {}     # dict
    _config_comments = {}    # dict

    def init(self):
        self.config.collections = {}
        pass

    def process_file(self, fileinfo, rules, data):
        coll_names = data.get('$global', {'collections': []}).get('collections', [])
        collections = self.config.collections
        for collection in coll_names:
            if collection not in collections:
                collections[collection] = []
            self.config.collections[collection] += [data]
        return data

    def modify_data(self):
        pass

    def build(self):
        pass


def create(config):
    return Collections(config)
