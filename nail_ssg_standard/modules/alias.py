from nail_ssg_base.modules.baseplugin import BasePlugin


class Alias(BasePlugin):
    _default_config = {}     # dict
    _config_comments = {}    # dict
    pass


def create(config):
    return Alias(config)
