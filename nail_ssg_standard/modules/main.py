import os
import warnings
import ruamel.yaml as yaml
from types import MethodType
from nail_ssg_base.prints import *
from nail_ssg_base.modules.baseplugin import BasePlugin
from nail_ssg_base.check_rules import check_rule


def _extract_yaml_data(filename: str):
    striped_line = ''
    with open(filename, 'r', encoding='utf-8') as f:
        yaml_lines = []
        checked_yaml = False
        for index, line in enumerate(f.readlines()):
            striped_line = line.split('#', 1)[0].strip()
            if not checked_yaml and striped_line[-3:] != '---':
                if index < 5:
                    continue
                else:
                    break
            if striped_line[:3] == '...' and checked_yaml:
                break
            if checked_yaml:
                yaml_lines += [line]
            checked_yaml = True
    if striped_line[:3] != '...':
        return {}
    yaml_str = ''.join(yaml_lines)
    result = yaml.load(yaml_str, Loader=yaml.Loader)
    if not result:
        result = {}
    return result


modified_step = False


def _set_data(self, path, value):
    self.data[path] = value


def _get_data(self, path):
    if not modified_step:
        warnings.warn('No recommended use get_data before "modified" step', stacklevel=2)
    # print(self)
    result = self.main_module.old_get_data(path)
    modules = self('20. getData/order')
    if result is None:
        for module in self.modules:
            result = module.get_data()
        return result if result is not None else {}
    # todo: Здесь должен быть перебор модулей которые умееют работать с путями
    return self.data.get(path, {})


def _read(self, size=None):
    if self.closed:
        return ''
    s = self.old_read(size)
    lines = s.splitlines()
    i = 1
    for line in lines:
        if '...' == line[:3]:
            s = '\n'.join(lines[:i])
            self.close()
            break
        i += 1
    return s


def read_data(filename, data, as_yaml=True):
    if as_yaml:
        with open(filename, 'r', encoding='utf-8') as f:
            f.old_read = f.read
            f.read = MethodType(_read, f)
            d = yaml.load(f, Loader=yaml.Loader)
            d = d if d else {}
            data.update(d)
    else:
        data.update(_extract_yaml_data(filename))


class SsgMain(BasePlugin):
    _default_config = {
        '00. core': {
            'modules': {
                "nail_ssg_standard.static": True,
                "nail_ssg_standard.collections": True,
                "nail_ssg_standard.alias": True,
                "nail_ssg_standard.pages": True,
                "nail_ssg_standard.loads": True,
            }
        },
        '10. scan': {
            'types': {
                'data': {
                    'extractData': True,
                    'rules': [
                        'fileMask = *.yml'
                    ]
                }
            }
        },
        '20. getData': {
            'order': []
        }
    }
    _config_comments = {}
    name = 'main'

    def __init__(self, config):
        super().__init__(config)
        if not config:
            return

    def modify_data(self):
        global modified_step
        modified_step = True
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
            folder = os.path.relpath(fileinfo['directory'], self.config.full_src_path)
            folder = folder.split(os.sep, 1)[0]
            fileinfo['root'] = folder
            fld = file_type.get('directory', '*')
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
                        if type_name not in rules:
                            rules[type_name] = []
                        rules[type_name] += [rule]
                        extract_data = extract_data or file_type['extractData']
        data['$computed']['rules'] = rules
        if extract_data:
            filename = fileinfo['full_path']
            read_data(filename, data, 'data' in rules)

    def init(self):
        self.types = self.config('10. scan/types', [])
        self.old_get_data = self.config.get_data
        self.config.get_data = MethodType(_get_data, self.config)
        self.config.set_data = MethodType(_set_data, self.config)


def create(config):
    return SsgMain(config)


__all__ = [SsgMain, create]
