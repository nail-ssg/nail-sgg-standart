from nail_ssg_base.modules.baseplugin import BasePlugin


class Alias(BasePlugin):
    _default_config = {
        'getData': {
            'order': ['nail_ssg_standard.alias']
        }
    }     # dict
    _config_comments = {}    # dict
    pass


def create(config):
    return Alias(config)
