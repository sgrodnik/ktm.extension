# -*- coding: utf-8 -*-
from __future__ import print_function

import Autodesk.Revit.DB as DB
import codecs
import csv
import os
import sys
from pyrevit import forms
from pyrevit import script

app = __revit__.Application

DEBUG = True
FIRST_PARAM_INDEX = 2

CANNOT_BE_ZERO_PARAMS = [
    'ADSK_Размер_Длина',
    'ADSK_Размер_Ширина',
    'ADSK_Размер_Высота'
]
SPECIAL_PARAM = "КЦМ_Базовая форма"


def print_mono(s):
    script.get_output().print_html(
        '<p style="font-family:consolas;">' + s + '</p>')


class Factory:
    working_folder_path = ''
    template_path = ''
    src_path = ''
    dest_folder = ''
    clean_table = []
    titles = []

    @classmethod
    def run(cls):
        cls.request_path()
        cls.print_info()
        if cls.src_path.endswith('.csv'):
            encoding = 'cp1251'
            delimiter = ';'
        elif cls.src_path.endswith('.txt'):
            encoding = 'utf8'
            delimiter = '\t'
        else:
            raise Exception('Расширение не поддерживается {}'
                            .format(cls.src_path))
        stream = open(cls.src_path, 'rb')
        table_reader = UnicodeReader(stream,
                                     encoding=encoding,
                                     delimiter=delimiter)
        table = list(table_reader)
        cls.clean_table = [row for row in table if cls.is_valid(row)]

        for row in table:
            if not cls.is_valid(row):
                continue
            if not cls.titles and row[0].startswith('Имя семейства'):
                cls.titles = row
                continue
            FamilySymbol(row)

        for family_symbol in FamilySymbol.objects.values():
            family_symbol.create_family()

    @classmethod
    def request_path(cls):
        cls.working_folder_path = forms.pick_folder(
            'Укажите папку с шаблоном и таблицей')
        for name in os.listdir(cls.working_folder_path):
            if not cls.template_path and (name.endswith('.rfa') or
                                          name.endswith('.rft')):
                cls.template_path = os.path.join(cls.working_folder_path, name)
            if not cls.src_path and (name.endswith('.txt') or
                                     name.endswith('.csv')):
                cls.src_path = os.path.join(cls.working_folder_path, name)
        if not cls.template_path:
            raise Exception('В указанной папке не найден шаблон')
        if not cls.src_path:
            raise Exception('В указанной папке не найдена таблица')
        cls.dest_folder = os.path.join(cls.working_folder_path, 'result')
        if not os.path.exists(cls.dest_folder):
            os.makedirs(cls.dest_folder)

    @classmethod
    def print_info(cls):
        output = script.get_output()
        output.close_others(all_open_outputs=True)
        output.self_destruct(120)
        info = 'Рабочая папка: {}{}'.format(' ' * 4, cls.working_folder_path)
        info += '\nБазовое семейство: {}'.format(cls.template_path)
        info += '\nТаблица: {}{}'.format(' ' * 10, cls.src_path)
        print_mono(info)

    @classmethod
    def is_valid(cls, row):
        return not row[0].startswith('#') and row[0]


class FamilySymbol:
    objects = {}

    def __init__(self, data):
        self.name = data[0]
        self.types = []
        self.used_columns = ColumnAnalyser.get_used_columns(self.name)
        objects = self.__class__.objects
        if self.name not in objects:
            objects[self.name] = self
        family_symbol = objects[self.name]
        family_symbol.types.append(FamilyType(family_symbol, data))

    def create_family(self):
        if Factory.template_path.endswith('.rft'):
            doc = app.NewFamilyDocument(Factory.template_path)
        elif Factory.template_path.endswith('.rfa'):
            doc = app.OpenDocumentFile(Factory.template_path)
        else:
            raise Exception('Расширение не поддерживается {}'
                            .format(Factory.template_path))
        with DB.Transaction(doc, 'Create types') as t:
            t.Start()
            print('Создание семейства: {}'.format(self.name))
            for type_ in self.types:
                self.create_type_optionally(doc, type_.name)
                print('Создание типа: {}'.format(type_.name))
                param_count = self.set_params(doc, type_)
                print('\tЗаписано параметров: {} шт.'.format(param_count))
            t.Commit()
        path = os.path.join(Factory.dest_folder, self.name + '.rfa')
        self.remove(path)
        doc.SaveAs(path)
        print('Сохранено: {}\n '.format(path))
        doc.Close(False)

    def create_type_optionally(self, doc, type_name):
        is_type_name_specified = bool(type_name)
        is_many_types = len(self.types) > 1
        if is_type_name_specified:
            new_type_name = type_name
        elif is_many_types:
            new_type_name = self.name
        else:
            return  # New type is not needed, default one is enough
        doc.FamilyManager.NewType(new_type_name)

    def set_params(self, doc, type_):
        for name, value in type_.params:
            fam_param = self.get_param(doc, name)
            if not fam_param:
                raise Exception('Не найден параметр {}'.format(name))
            value = self.typify(self, fam_param, value)
            doc.FamilyManager.set_value(fam_param, value)
        return len(type_.params)

    @staticmethod
    def get_param(doc, param_name):
        for param in doc.FamilyManager.GetParameters():
            if param.Definition.Name == param_name:
                return param

    @staticmethod
    def typify(self, fam_param, value):
        if fam_param.StorageType == DB.StorageType.Double:
            return DB.UnitUtils.ConvertToInternalUnits(
                float(self.parse_double(value, fam_param)), fam_param.DisplayUnitType)
        elif fam_param.StorageType == DB.StorageType.String:
            return value
        elif fam_param.StorageType == DB.StorageType.Integer:
            return self.parse_int(value)
        else:
            raise Exception()

    @staticmethod
    def parse_double(value, fam_param):
        default_value = 0
        if fam_param.Definition.Name in CANNOT_BE_ZERO_PARAMS:
            default_value = 1
        return value.replace(',', '.') or default_value

    @staticmethod
    def parse_int(value):
        if value.isdigit():
            return int(value)
        isdigits = ''.join(c for c in value if c.isdigit())
        return int(isdigits or 0)

    @staticmethod
    def remove(file_path):
        if os.path.isfile(file_path):
            os.remove(file_path)


class ColumnAnalyser:
    column_indexes = {}

    @classmethod
    def get_used_columns(cls, name):
        if not cls.column_indexes:
            cls.initialize()
        return cls.column_indexes[name]

    @classmethod
    def initialize(cls):
        for row in Factory.clean_table:
            fam_name = row[0]
            if fam_name not in cls.column_indexes:
                cls.column_indexes[fam_name] = set()
            for index, cell in enumerate(row[FIRST_PARAM_INDEX:]):
                if cell:
                    cls.column_indexes[fam_name].add(index)


class FamilyType:
    def __init__(self, symbol, data):
        # for i in data:
        #     print(i)
        self.name = data[1]
        self.symbol = symbol
        self.data = data[FIRST_PARAM_INDEX:]
        self.params = []
        self.populate_params()

    def populate_params(self):
        for index, val in enumerate(self.data):
            if not self.is_valid_cell(index, val):
                continue
            debug_info = '{} {} {} {} {} {}'.format(self.symbol.name,
                                                    self.name,
                                                    index,
                                                    self.get_title(index),
                                                    val,
                                                    self.symbol.used_columns)
            # print(debug_info)
            self.params.append((self.get_title(index), val))

    def is_valid_cell(self, index, val):
        if val:
            return True
        if index in self.symbol.used_columns:
            return True
        return False

    @staticmethod
    def get_title(index):
        return Factory.titles[FIRST_PARAM_INDEX + index]


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


try:
    Factory.run()
    script.get_output().log_success('Готово')
except Exception as e:
    import traceback
    import sys
    print('.')
    output = script.get_output()
    output.log_error('Произошла ошибка: {}'.format(e))
    # traceback = sys.exc_info()[2]
    traceback = traceback.format_exc()
    traceback = '-' * 100 + '\nСтек вызовов: {}\n'.format(traceback)+ '-' * 100
    print(traceback)
    # output.print_html('<font color="red">' + traceback + '</font>')
