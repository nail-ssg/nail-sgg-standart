import markdown
from nail_ssg_base.prints import *
from nail_ssg_base.modules.baserender import BaseRender


class Markdown(BaseRender):

    def __init__(self, config):
        super().__init__(config)

    def render(self, text, context, render_options):
        return markdown.markdown(text)


def create(config):
    return Markdown(config)
