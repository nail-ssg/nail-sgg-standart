import os

import nail_ssg_base
import pytest


# Создать объект builder
def full_path(filename):
    return os.path.join(os.path.dirname(__file__), 'data', filename)


@pytest.fixture()
def empty_builder():
    filename = full_path('config_minimal.yml')
    print(filename)
    return nail_ssg_base.builder.Builder(filename)


def test_builder(empty_builder):
    # empty_builder.add_module('pages')
    empty_builder.build()
