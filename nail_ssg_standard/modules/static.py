import os
from nail_ssg_base.prints import *
from nail_ssg_base.modules.baseplugin import BasePlugin
from shutil import copyfile


class Static(BasePlugin):
    _default_config = {
        '10. scan': {
            'order': [
                'nail_ssg_standard.static'
            ],
            'types': {
                'static': {
                    'extractData': False,
                    'directories': ['static', 'pages', ],
                    'rules': [
                        'fileMask = *.css',
                        'fileMask = *.js',
                        'fileMask = *.jpg',
                        'fileMask = *.jpeg',
                        'fileMask = *.png',
                        'fileMask = *.gif',
                        'fileMask = *.pdf',
                    ]
                }
            }
        },
        '40. build': {
            'order': [
                'nail_ssg_standard.static'
            ],
        }
    }
    _config_comments = {
        '10. scan/types/static/directories': 'Directories with static content. The priority of folder increases',
    }

    def __init__(self, config):
        super().__init__(config)
        self.folders = []

    def init(self):
        self.folders = self.config('10. scan/types/static/directories')
        self.config.static = {}
        for folder in self.folders:
            self.config.static[folder] = {}

    def process_file(self, fileinfo, rules, data):
        folder = fileinfo['root']
        if folder in self.folders and 'static' in rules:
            rel_path = os.path.relpath(fileinfo['full_path'], self.config.full_src_path).split(os.sep, 1)[1]
            data_ext = {'$global': {'url': rel_path.replace(os.sep, '/')}}
            data.update(dict_enrich(data, data_ext))
            self.config.static[folder][rel_path] = data
        return data

    def modify_data(self):
        pass

    def build(self):
        result = {}
        static = self.config.static
        for folder in self.folders:
            result.update(static[folder])
        for rel_path in result:
            dst = os.path.join(self.config.full_dst_path, rel_path)
            directory = os.path.dirname(dst)
            src = result[rel_path]['$computed']['file']
            os.makedirs(directory, exist_ok=True)
            copyfile(src, dst)


def create(config):
    return Static(config)
