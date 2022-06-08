# -*- coding: utf-8 -*-

import Autodesk.Revit.DB as DB
import datetime
import os
import subprocess as sp
from pyrevit import forms

app = __revit__.Application

DEBUG = True

time_str = str(datetime.datetime.now()).split('.')[0].replace(':', '-')
log_path = os.getenv('temp') + "\\Family Info " + time_str + ".csv"
log_path_short = os.getenv('temp') + "\\Family Info " + time_str + " short.csv"


def log(s):
    with open(log_path, "a") as myfile:
        myfile.write(s.encode("utf-8") + '\n')


class ReportEntity:
    counter = 0
    is_first = True

    def __init__(self, family, param):
        self.__class__.counter += 1
        self.id = self.__class__.counter
        self.family = family
        self.param = param
        self.name = self.param.Definition.Name
        self.get_family_parameter_data()

    def get_family_parameter_data(self):
        try:
            self.parameter_type = DB.LabelUtils.GetLabelFor(
                self.param.Definition.ParameterType)
            self.parameter_group = DB.LabelUtils.GetLabelFor(
                self.param.Definition.ParameterGroup)
            self.guid = self.param.GUID if self.param.IsShared else ''
            self.built_in_parameter =\
                str(self.param.Definition.BuiltInParameter)\
                .replace('INVALID', '')
            self.is_instance =\
                'По экземпляру' if self.param.IsInstance else 'По типу'
            self.units = ''
            if self.param.StorageType == DB.StorageType.Double\
                    and has_display_unit_type(self.param):
                self.units = DB.LabelUtils.GetLabelFor(
                    self.param.DisplayUnitType)
        except Exception as e:
            log('Ошибка обработки параметра: {}: {}'.format(self.name, e))
            if DEBUG:
                raise

    def get_family_parameter_values_by_types(self):
        pass

    def write_to_file_long(self):
        pass

    def write_to_file_short(self):
        info = []
        for val, title in [
            (self.id, '#'),
            (self.family.path, 'Путь'),
            (self.family.size, 'Размер, Кбайт'),
            (self.family.title, 'Семейство'),
            (self.family.types_count, 'Количество типоразмеров'),
            (self.parameter_type, 'Тип параметра'),
            (self.parameter_group, 'Группа параметров'),
            (self.name, 'Параметр'),
            (self.guid, 'GUID'),
            (self.built_in_parameter, 'BuiltInParameter'),
            (self.units, 'Единицы'),
            (self.is_instance, 'По экземпляру'),
            ]:
            info.append(val)
            add_title(title)
        info = '\t'.join([str(i) for i in info])
        if self.__class__.is_first:
            self.__class__.is_first = False
            log('\t'.join(titles))
        log(info)


titles = []


def add_title(s):
    if s not in titles:
        titles.append(s)


def has_display_unit_type(fam_param):
    parameter_type = fam_param.Definition.ParameterType
    return parameter_type in allowed_parameter_types\
        or 100 < int(parameter_type)


allowed_parameter_types = [
    DB.ParameterType.Length,
    DB.ParameterType.Area,
    DB.ParameterType.Volume,
    DB.ParameterType.Angle,
    DB.ParameterType.Number,
    DB.ParameterType.Force,
    DB.ParameterType.LinearForce,
    DB.ParameterType.AreaForce,
    DB.ParameterType.Moment,
]


class FamilyFile:
    def __init__(self, path):
        self.path = path
        self.doc = app.OpenDocumentFile(path)
        self.get_family_document_data()

    def get_family_document_data(self):
        self.size = os.path.getsize(self.path) / 1024
        self.title = self.doc.Title
        self.types = list(self.doc.FamilyManager.Types)
        if len(self.types) > 1:
            self.types = [i for i in self.types if i.Name != ' ']
        self.types_count = len(self.types)

    def work_params(self):
        for param in self.doc.FamilyManager.GetParameters():
            try:
                ReportEntity(self, param).write_to_file_short()
            except Exception as e:
                log('Ошибка обработки семейства: {}: {}'.format(self.path, e))
                if DEBUG:
                    raise
        try:
            self.doc.Close(False)
        except:
            pass

# paths = [r"C:\Users\hp22\Desktop\Семейство1.rfa"]
title = 'Выбор семейств (для выбора папки нажмите Отмена или закройте это окно)'
paths = forms.pick_file(file_ext='rfa', multi_file=True, title=title) or []
if not paths:
    folder = forms.pick_folder(title='Выбор семейств')
    if folder:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".rfa"):
                    paths.append(os.path.join(root, file))

if paths:
    max_value = len(paths)
    with forms.ProgressBar(title='Обработано семейств: {value} из {max_value}', cancellable=True) as pb:
        for i, path in enumerate(paths):
            pb.update_progress(i, max_value)
            if pb.cancelled:
                break
            FamilyFile(path).work_params()
    sp.Popen(["notepad.exe", log_path])
    # sp.Popen(["notepad.exe", log_path_short])
