from os.path import abspath

import nail_ssg_base
import pytest


# Создать объект builder
@pytest.fixture()
def empty_builder():
    filename = abspath('tests/data/config_minimal.yml')
    print(filename)
    return nail_ssg_base.builder.Builder(filename)


def test_builder(empty_builder):
    # empty_builder.add_module('pages')
    empty_builder.build()
