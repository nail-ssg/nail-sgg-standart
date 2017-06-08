from nail_ssg_base.prints import *
from pystache import Renderer
from nail_ssg_base.modules.baserender import BaseRender
from nail_config.common import dict_enrich, dict_concat
import blinker

class Mustache(BaseRender):

    """docstring for Mustache"""

    def __init__(self, config):
        super().__init__(config)

    def render(self, text, context, render_options):
        # print(render_options)
        # print(text)
        # yprint(context)
        partials = {}
        if 'data' in render_options:
            context = context.copy()
            dict_concat(context, render_options['data'])
        if 'partials' in render_options:
            for partial_name in render_options['partials']:
                partial_path = render_options['partials'][partial_name]
                partials[partial_name] = ''
                # partials[partial_name] = site_builder.renderFile(partial_path, context)
                inset_signal = blinker.signal('inset')
                signal_result = inset_signal.send(self, inset_name=partial_path, context=context)
                if len(signal_result) > 0:
                    partials[partial_name] = signal_result[0][1]
        renderer = Renderer(partials=partials)
        s = renderer.render(text, context)
        return s


def create(config):
    return Mustache(config)
