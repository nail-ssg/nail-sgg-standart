from nail_ssg.modules.baserender import BaseRender


class Plain(BaseRender):

    """docstring for Plain"""

    def __init__(self, config):
        super().__init__(config)

    def render(self, text, context, render_options):
        return text


def create(config):
    return Plain(config)
