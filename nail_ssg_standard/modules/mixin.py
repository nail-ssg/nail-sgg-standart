from nail_config.common import dict_enrich, dict_concat
from nail_ssg_base.modules.baseplugin import BasePlugin
from nail_ssg_base.prints import *


class Mixin(BasePlugin):
    _default_config = {
        'scan': {
            'order': ['nail_ssg_standard.mixin']
        },
        'modify': {
            'order': ['nail_ssg_standard.mixin']
        }
    }
    _config_comments = {}

    def init(self):
        self.config.mixins = []


    def process_file(self, fileinfo, rules, data):
        if '$mixin' in data:
            self.config.mixins += [data]
        pass

    def modify_data(self):
        for data in self.config.mixins:
            mixins = data.get('$mixin', [])
            if mixins == []:
                continue
            result = {}
            for mixin in mixins:
                d = self.config.get_data(mixin)
                result = dict_enrich(result, d)
            result = dict_enrich(result, data)
            data.update(result)
            del data['$mixin']
        del self.config.mixins
        yprint(self.config.data)

    def build(self):
        pass


def create(config):
    return Mixin(config)
