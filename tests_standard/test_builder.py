import os

import pytest
from nail_ssg_base.builder import Builder


def full_path(filename):
    return os.path.join(os.path.dirname(__file__), 'data', filename)


@pytest.fixture()
def empty_data():
    return '---'


@pytest.fixture()
def plugin_data():
    return '''---
00. core:
  src: tests/data/src1
  dist: tests/data/site
  currentNamespace: default
  modules:
    nail_ssg_standard.modules.pages: true
    nail_ssg_standard.modules.static: true
  main: nail_ssg_standard.modules.main
10. scan:
  order:
    - nail_ssg_standard.modules.pages
    - nail_ssg_standard.modules.static
'''


# [+] Подключение встроенных модулей к генератору
def test_plugin(plugin_data):
    Builder(data=plugin_data)

#  [+] Загрузка файла конфигурации
#  [+] Загрузка модуля main
#  [+] Подключение обработчика регистрации файла
#  [+] Определение к какому правилу относится файл
#  [+] Вынести "список модулей" в отдельный модуль
#  [-] Преобразование пути файла к URL, если URL'а нет
#  [-] Подключение внешних модулей к генератору
#  [-] Перебор файлов
#  [-] Группировка файлов по типам
#  [-] Рендер plain
#  [-] Рендер mustache
#  [-] Алиасы
#  [-] Коллекции
#  [-] Папка для статики
#  [-] Переименование файлов
#  [-] Миксины (наследование)
#  [-] Загрузка данных из файла
#  [-] Загрузка данных из папки
