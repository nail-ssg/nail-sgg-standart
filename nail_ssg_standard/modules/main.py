import os
import types
import ruamel.yaml as yaml
from nail_ssg_base.modules.baseplugin import BasePlugin
from nail_ssg_base.check_rules import check_rule


def _extract_yaml_data(filename: str):
    striped_line = ''
    with open(filename, 'r', encoding='utf-8') as f:
        yaml_lines = []
        checked_yaml = False
        for line in f.readlines():
            striped_line = line.strip()
            if not checked_yaml and (striped_line != '---'):
                break
            checked_yaml = True
            yaml_lines += [line]
            if striped_line == '...':
                break
    if striped_line != '...':
        return {}
    yaml_str = ''.join(yaml_lines)
    result = yaml.load(yaml_str, Loader=yaml.Loader)
    if not result:
        result = {}
    return result


def _get_data(self, path):
    print(self)
    if 'data' not in self.data:
        return {}
    if path in self.data['data']:
        return self.data['data'][path]
    return {}  # todo: Здесь должен быть перебор модулей которые умееют работать с путями


class SsgMain(BasePlugin):
    _default_config = {
        'core': {
            'modules': {
                "nail_ssg_standard.static": True,
                "nail_ssg_standard.collections": True,
                "nail_ssg_standard.alias": True,
                "nail_ssg_standard.pages": True,
                "nail_ssg_standard.mixin": True,
            },
        },
    }
    _config_comments = {}
    name = 'main'

    def __init__(self, config):
        super().__init__(config)
        if not config:
            return

    def modify_data(self):
        super().modify_data()

    def build(self):
        super().build()

    def process_file(self, fileinfo, rules, data):
        super().process_file(fileinfo, rules, data)
        # todo: определить к какому правилу относится файл
        # print('*'*20)
        extract_data = False
        for type_name in self.types:
            file_type = self.types[type_name]
            folder = os.path.relpath(fileinfo['folder'], self.config.full_src_path)
            folder = folder.split(os.sep, 1)[0]
            fileinfo['root'] = folder
            fld = file_type.get('folder', '*')
            data_ext = {
                '$computed': {
                    'file': fileinfo['full_path']
                }
            }
            data.update(data_ext)
            if not (fld != '*' and folder != fld):
                for rule in file_type['rules']:
                    validation = check_rule(rule, fileinfo['name'])
                    if validation:
                        # print(validation, fileinfo['name'])
                        if type_name not in rules:
                            rules[type_name] = []
                        rules[type_name] += [rule]
                        extract_data = extract_data or file_type['extractData']
        if extract_data:
            filename = fileinfo['full_path']
            data.update(_extract_yaml_data(filename))

    def init(self):
        self.types = self.config('scan/types', [])
        self.config.get_data = types.MethodType(_get_data, self.config)


def create(config):
    return SsgMain(config)
