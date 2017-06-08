import os
import copy
from nail_ssg_base.prints import *
from nail_ssg_base.modules.baseplugin import BasePlugin
from nail_config.common import dict_enrich, dict_concat
from blinker import signal


class Pages(BasePlugin):

    """docstring for Pages"""
    _default_config = {
        'scan': {
            'order': ['nail_ssg_standard.pages'],
            'types': {
                'page': {
                    'folder': 'pages',
                    'extractData': True,
                    'rules': [
                        'fileMask = *.html',
                        'regexp = \.page\.',
                    ],
                    'rename': [
                        r'=(.*)\.page(\..*)=\1\2=',
                        r'~((.*)\.html)~\1/index.html~'
                    ],
                    'norename': [
                        r'^index.html$',
                    ]
                },
                'template': {
                    'folder': '*',
                    'extractData': True,
                    'rules': [
                        'fileMask = *.html'
                    ],
                }
            }
        },
        'build': {'order': ['nail_ssg_standard.pages']},
        # 'modify': {'order': ['nail_ssg_standard.pages']},
    }
    _config_comments = {
        'scan.types.page.rename': 'First char is delimiter'
    }

    def _inset(self, sender, inset_name='', context=None):
        # print(inset_name, context)
        return self.render_file(inset_name, context)

    def _inset2(sender, *a, **k):
        print(a, k)
        return None

    def __init__(self, config):
        super(Pages, self).__init__(config)
        signal('inset').connect(self._inset)

    def init(self):
        folder = self.config('scan/types/page/folder')
        self.folder = os.path.join(self.config.full_src_path, folder)
        self.config.pages = []

    def modify_data(self):
        super().modify_data()

    def process_file(self, fileinfo, rules, data):
        super().process_file(fileinfo, rules, data)
        if 'page' in rules:
            rel_path = os.path.relpath(fileinfo['full_path'], self.folder)
            # todo: rename and norename
            data_ext = {'$global': {'url': rel_path.replace(os.sep, '/')}}
            data.update(dict_enrich(data, data_ext))
            self.config.pages += [data]
        return data

    def build(self):
        super().build()
        pages = self.config.pages
        for page in pages:
            url = page['$global']['url']
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
        context = copy.deepcopy(page)
        external_context = context['$computed']
        external_context['all'] = self.config.data
        external_context['collections'] = {}
        loc_coll = {}  # Локальные коллекции
        if '$global' in context:
            dict_concat(external_context['collections'], loc_coll)

        if '$local' in context:
            local_context = context['$local']
            if 'collections' not in local_context:
                local_context['collections'] = {}
            dict_concat(loc_coll, local_context['collections'])
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
                dict_concat(context, render_options['data'])
            render_type = render_options['type']
            render_module = self.config.get_module('nail_ssg_standard.modules.'+render_type+'_render')
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
        lines = []
        for line in open(path, 'r', encoding='utf-8').readlines():
            if line[0:3] != '...':
                lines += [line]
            else:
                lines = []
        result = ''.join(lines)
        return result

    def render_file(self, path, context):
        short_contex = copy.deepcopy(context)
        del short_contex['$computed']
        del short_contex['$local']['renders']
        if 'load' in short_contex['$local']:
            del short_contex['$local']['load']
        data = copy.deepcopy(self.config.get_data(path))
        dict_concat(data, short_contex)
        return self.render_page(data)


def create(config):
    return Pages(config)

