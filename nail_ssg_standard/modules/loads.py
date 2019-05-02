import copy

from nail_config import Config
from nail_config.common import dict_glue
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

    def __init__(self, config: Config):
        super().__init__(config)
        self.config.load_list = []

    def process_file(self, file_info, rules, data):
        if '$load' in data:
            self.config.load_list += [data]

    def modify_data(self):
        for data in self.config.load_list:
            load_list = data.get('$load', [])
            if not load_list:
                continue
            result = {}
            for load in load_list:
                d = copy.deepcopy(self.config.get_data(load))
                if '$computed' in d:
                    del d['$computed']
                if '$global' in d and 'abstract' in d['$global']:
                    del d['$global']['abstract']
                result = dict_glue(result, d)
            result = dict_glue(data, result)
            data.update(result)
            del data['$load']
        del self.config.load_list

    def build(self):
        pass


def create(config):
    return Loads(config)
