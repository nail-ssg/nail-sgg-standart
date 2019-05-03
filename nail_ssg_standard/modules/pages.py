import os
import re
from copy import deepcopy

from blinker import signal
from nail_config.common import dict_update
from nail_ssg_base.modules.baseplugin import BasePlugin


class Pages(BasePlugin):
    """docstring for Pages"""
    _default_config = {
        '10. scan': {
            'order': ['nail_ssg_standard.pages'],
            'types': {
                'page': {
                    'directory': 'pages',
                    'extractData': True,
                    'rules': {
                        'fileMask = *.html': True,
                        r'regexp = \.page\.': True, },
                    'rename': {
                        r'=(.*)\.page(\..*)=\1\2=': True,
                        r'~(.*)\.html~\1/~': True
                    },
                    'norename': {
                        r'(^|/)index.html$': True
                    }
                },
                'template': {
                    'directory': '*',
                    'extractData': True,
                    'rules': [
                        'fileMask = *.html'
                    ],
                }
            }
        },
        '40. build': {'order': ['nail_ssg_standard.pages']},
        # 'modify': {'order': ['nail_ssg_standard.pages']},
    }
    _config_comments = {
        '10. scan/types/page/rename': 'First char is delimiter'
    }

    def _inset(self, sender, inset_name='', context=None):
        return self.render_file(inset_name, context)

    def __init__(self, config):
        super(Pages, self).__init__(config)
        signal('inset').connect(self._inset)
        self.config.pages = []
        self.folder = ''

    def init(self):
        folder = self.config('10. scan/types/page/directory')
        self.folder = os.path.join(self.config.full_src_path, folder)
        self.config.pages = []

    # def modify_data(self):
    #     super().modify_data()

    def process_file(self, file_info, rules, data):
        super(Pages, self).process_file(file_info, rules, data)
        if 'page' in rules:
            rel_path = os.path.relpath(file_info['full_path'], self.folder)
            # todo: rename and norename

            url = data.get('$global', {}).get('url', None)
            if url is None:
                url = rel_path.replace(os.sep, '/')
            norename = False
            norename_conditions = self.config('10. scan/types/page/norename')
            for norename_condition in norename_conditions:
                norename = norename or re.search(norename_condition, url) is not None
            if not norename:
                rename_conditions = self.config('10. scan/types/page/rename')
                for rename_condition in rename_conditions:
                    separator = rename_condition[0]
                    assert separator == rename_condition[-1]
                    repl_from, repl_to = rename_condition[1:-1].split(separator)
                    new_url = re.sub(repl_from, repl_to, url)
                    if new_url != url:
                        url = new_url
                        break

            data_ext = {'$computed': {'url': url}}
            dict_update(data, data_ext)
            self.config.pages += [data]
        return data

    def build(self):
        super(Pages, self).build()
        pages = self.config.pages
        for page in pages:
            url = page['$computed']['url']
            if url[-1] == '/':
                url += 'index.html'
            new_path = os.path.join(self.config.full_dst_path, url.replace('/', os.sep))
            s = self.render_page(page)
            directory = os.path.split(new_path)[0]
            os.makedirs(directory, exist_ok=True)
            with open(new_path, 'w+', encoding='utf-8') as f:
                f.write(s)

    def render_page(self, page: dict) -> str:
        if page is None or page == {}:
            return ''
        if '$computed' not in page:
            return ''
        context = deepcopy(page)
        external_context = context['$computed']
        external_context['all'] = self.config.data
        external_context['collections'] = {}
        loc_coll = {}  # Локальные коллекции
        if '$global' in context:
            dict_update(external_context['collections'], loc_coll, False)

        if '$local' in context:
            local_context = context['$local']
            if 'collections' not in local_context:
                local_context['collections'] = {}
            dict_update(loc_coll, local_context['collections'], False)
            if 'use' in local_context:
                for var_name in local_context['use']:
                    var_options = local_context['use'][var_name]
                    coll_name = var_options['from'] if 'from' in var_options else var_name
                    if coll_name in loc_coll:
                        coll = external_context['collections'][coll_name].copy()
                    elif coll_name in local_context:
                        coll = local_context[coll_name].copy()
                    else:
                        coll = None
                    if coll is not None:
                        if 'sort' in var_options:
                            sort = var_options['sort']
                            reverse = False
                            if sort[0] in '+-':
                                key = sort[1:]
                                reverse = sort[0] == '-'
                            else:
                                key = sort
                            coll.sort(key=lambda row: row[key], reverse=reverse)
                        offset = (var_options['offset']) if 'offset' in var_options else 0
                        count = (var_options['count']) if 'count' in var_options else None
                        end = offset + count if count is not None else None
                        context[var_name] = coll[offset:end]
            if 'renders' not in local_context:
                local_context['renders'] = [
                    # По умолчанию страницы без рендера содержат простой текст
                    {'type': 'plain', 'name': None, 'layout': None}
                ]
            if 'load' in local_context:
                for var in local_context['load']:
                    other_page_path = local_context['load'][var]
                    context[var] = self.render_file(other_page_path, context)
        else:
            local_context = {'renders': []}
        if '$text' in local_context:
            text = local_context['$text']
        else:
            text = self.get_text(external_context['file'])
        for render_options in local_context['renders']:
            if 'data' in render_options:
                dict_update(context, render_options['data'], False)
            render_type = render_options['type']
            render_module = self.config.get_module('nail_ssg_standard.modules.' + render_type + '_render')
            if render_module is None:
                render_module = self.config.get_module('plain_render')
            if render_module is None:
                return text
            text = render_module.render(text, context, render_options)
            if 'extend' in render_options:
                if 'blockName' in render_options:
                    block_name = render_options['blockName']
                else:
                    block_name = '$content'
                context[block_name] = text
                text = self.render_file(render_options['extend'], context)
        return text

    def get_text(self, path: str) -> str:
        start_lines = []
        lines = []
        for line in open(path, 'r', encoding='utf-8').readlines():
            if line[-3:] == '---':
                start_lines = lines
                lines = []
            elif line[:3] == '...':
                lines = []
            else:
                lines += [line]
        result = ''.join(start_lines + lines)
        return result

    def render_file(self, path, context):
        short_contex = deepcopy(context)
        del short_contex['$computed']
        del short_contex['$local']['renders']
        if 'load' in short_contex['$local']:
            del short_contex['$local']['load']
        data = deepcopy(self.config.get_data(path))
        dict_update(data, short_contex, False)
        return self.render_page(data)


def create(config):
    return Pages(config)
