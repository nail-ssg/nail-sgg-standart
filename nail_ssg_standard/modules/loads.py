import copy
from nail_config.common import dict_enrich, dict_concat
from nail_ssg_base.modules.baseplugin import BasePlugin
# from nail_ssg_base.prints import *


class Loads(BasePlugin):
    _default_config = {
        '10. scan': {
            'order': ['nail_ssg_standard.loads']
        },
        '20. modify': {
            'order': ['nail_ssg_standard.loads']
        }
    }
    _config_comments = {}

    def init(self):
        self.config.loads = []

    def process_file(self, fileinfo, rules, data):
        if '$load' in data:
            self.config.loads += [data]
        pass

    def modify_data(self):
        for data in self.config.loads:
            loads = data.get('$load', [])
            if loads == []:
                continue
            result = {}
            for load in loads:
                d = copy.deepcopy(self.config.get_data(load))
                del d['$computed']
                if 'abstract' in d['$global']:
                    del d['$global']['abstract']
                result = dict_enrich(result, d)
            result = dict_enrich(data, result)
            data.update(result)
            del data['$load']
        del self.config.loads

    def build(self):
        pass


def create(config):
    return load(config)
