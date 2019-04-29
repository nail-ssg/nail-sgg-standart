import copy
from nail_config.common import dict_update, dict_glue
from nail_ssg_base.modules.baseplugin import BasePlugin


# from nail_ssg_base.prints import *


class Loads(BasePlugin):
    _default_config = {
        '10. scan': {
            'order': ['nail_ssg_standard.loads']
        },
        '30. modify': {
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
                if '$computed' in d:
                    del d['$computed']
                if '$global' in d and 'abstract' in d['$global']:
                    del d['$global']['abstract']
                result = dict_glue(result, d)
            result = dict_glue(data, result)
            data.update(result)
            del data['$load']
        del self.config.loads

    def build(self):
        pass


def create(config):
    return Loads(config)
