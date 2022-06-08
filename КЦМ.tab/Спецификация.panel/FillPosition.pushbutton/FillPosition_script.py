# -*- coding: utf-8 -*-
import clr
import sys
import traceback
import utils

import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI
from pyrevit import forms
from pyrevit import script
from System import Guid

clr.AddReference('System')

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
output = script.get_output()
cache = {}

script_name = 'Проставить позицию'
ADSK_POS = Guid('ae8ff999-1f22-4ed7-ad33-61503d85f0f4')
ADSK_POS_name = 'ADSK_Позиция'
param_to_numerate = None
param_to_numerate_name = ''
start_number = ''
start_number_prefix = ''
row_number = None


def main():
    init_output()
    try:
        auto_numerate_pos()
        output.log_success('Готово')
    except Exception as e:
        output.log_error('Произошла ошибка: {}'.format(e))
        print(get_decorated_traceback())


def init_output():
    output.close_others(all_open_outputs=True)
    output.self_destruct(120)


def get_decorated_traceback():
    trace = traceback.format_exc()
    trace = '-' * 100 + '\nСтек вызовов: {}\n'.format(trace) + '-' * 100
    return trace


def auto_numerate_pos():
    global row_number
    utils.check_active_view_is_schedule()
    request_user_config()
    schedule = doc.ActiveView
    transaction_name = script_name + ' ' + schedule.Name
    number_of_rows = utils.get_number_of_rows_of_schedule(schedule)
    if not number_of_rows:
        return
    row_number = start_number
    with DB.Transaction(doc, transaction_name) as transaction:
        transaction.Start()
        start_index = 0 + schedule.Definition.ShowHeaders
        for row_index in range(start_index, number_of_rows):
            row_elements = utils.get_row_elements(schedule, row_index)
            value = '{}{}'.format(start_number_prefix, row_number)
            set_value_to_els(value, row_elements)
            if type(row_number) == int:
                row_number += 1
        transaction.SetName('Проставить {} {}÷{}'.format(
            param_to_numerate_name,
            '{}{}'.format(start_number_prefix, start_number),
            '{}{}'.format(start_number_prefix, row_number)))
        transaction.Commit()


def request_user_config():
    while True:
        dialog = UI.TaskDialog(script_name)
        dialog.MainContent = 'Задайте конфигурацию и нажмите Esc или ОК'
        dialog.FooterText = 'Esc - продолжить'
        dialog.TitleAutoPrefix = False
        dialog.AllowCancellation = True
        initialize_or_edit_parameter()
        dialog.AddCommandLink(
            UI.TaskDialogCommandLinkId.CommandLink1,
            'Параметр "{}"'.format(param_to_numerate_name),
            'Выбрать другой параметр'
        )
        initialize_or_edit_start_number()
        dialog.AddCommandLink(
            UI.TaskDialogCommandLinkId.CommandLink2,
            'Начальное значение "{}{}"'.format(start_number_prefix,
                                               start_number),
            'Задать другое начальное значение'
        )
        dialog.CommonButtons = UI.TaskDialogCommonButtons.Close |\
                               UI.TaskDialogCommonButtons.Ok
        dialog.DefaultButton = UI.TaskDialogResult.Ok
        res = dialog.Show()
        if res == UI.TaskDialogResult.CommandLink1:
            initialize_or_edit_parameter(edit=True)
            utils.check(param_to_numerate_name)
        elif res == UI.TaskDialogResult.CommandLink2:
            initialize_or_edit_start_number(edit=True)
        elif res == UI.TaskDialogResult.Ok or\
             res == UI.TaskDialogResult.Cancel:
            utils.check(param_to_numerate_name)
            return
        elif res == UI.TaskDialogResult.Close:
            sys.exit()


def initialize_or_edit_start_number(edit=False):
    global start_number
    global start_number_prefix
    cfg = script.get_config()
    init_value = '1'
    default_value = cfg.get_option(
        'fill_position_start_number', init_value)
    default_value = default_value or init_value
    if edit:
        res = forms.ask_for_string(
            default=default_value,
            prompt='Введите начальное значение (поддерживается префикс)',
            title='Начальное значение'
        )
        res = res or default_value
        cfg.fill_position_start_number = res
        script.save_config()
    else:
        res = default_value
    digits = ''.join([c for c in res if c.isdigit()])
    start_number = int(digits) if digits else ''
    start_number_prefix = ''.join([c for c in res if not c.isdigit()])


def initialize_or_edit_parameter(edit=False):
    global param_to_numerate
    global param_to_numerate_name
    cfg = script.get_config()
    init_value = ADSK_POS_name
    default_value = cfg.get_option('fill_position_parameter', init_value)
    default_value = default_value or init_value
    available_param_ids, available_param_names = get_param_info_from_schedule()
    if edit:
        param_name = forms.SelectFromList.show(
            available_param_names,
            button_name='Выберите параметр спецификации для нумерации'
        )
        cfg.fill_position_parameter = param_name
        script.save_config()
    else:
        param_name = default_value
    # if not param_name:
    #     param_to_numerate = ADSK_POS
    #     return
    if param_name not in available_param_names:
        param_name = available_param_names[0]
    param_to_numerate_name = param_name
    param_id = available_param_ids[available_param_names.index(param_name)]
    if param_id.IntegerValue < -1:
        param_to_numerate = DB.BuiltInParameter.ToObject(DB.BuiltInParameter,
                                                         param_id.IntegerValue)
    else:
        param_to_numerate = doc.GetElement(param_id).GuidValue


def get_param_info_from_schedule():
    available_param_names = []
    available_param_ids = []
    schedule_field_ids = doc.ActiveView.Definition.GetFieldOrder()
    for id in schedule_field_ids:
        field = doc.ActiveView.Definition.GetField(id)
        name = field.GetName()
        param_id = field.ParameterId
        available_param_names.append(name)
        available_param_ids.append(param_id)
    return available_param_ids, available_param_names


def set_value_to_els(value, elements):
    for el in elements:
        wrapped_el = Wrapper.create_of_fetch(el)
        check_el_and_set_value(wrapped_el, value)
        if is_child(wrapped_el.origin):
            if el_is_alone(elements, wrapped_el):
                wrapped_el.is_written_as_alone = True


class Wrapper:
    objects = {}

    def __init__(self, revit_element):
        self.__class__.objects[revit_element.Id] = self
        self.origin = revit_element
        self.id = revit_element.Id
        self.is_written_as_alone = False

    @classmethod
    def create_of_fetch(cls, revit_element):
        if revit_element.Id in cls.objects:
            return cls.objects[revit_element.Id]
        else:
            return cls(revit_element)


def check_el_and_set_value(wrapped_el, value):
    if writing_is_allowed(wrapped_el):
        parameter = wrapped_el.origin.get_Parameter(param_to_numerate)
        if parameter.StorageType == DB.StorageType.Double:
            parameter.Set(float(value))
        else:
            parameter.Set(value)


def writing_is_allowed(wrapped_el):
    result = True
    if is_child(wrapped_el.origin):
        result = not wrapped_el.is_written_as_alone
    return result


def is_child(el):
    return type(el) is DB.FamilyInstance and el.SuperComponent is not None


def el_is_alone(elements, wrapped_el):
    result = True
    row_el_ids = [i.Id.IntegerValue for i in elements]
    parents = get_parents(wrapped_el.origin)
    for parent in parents:
        if parent.Id.IntegerValue in row_el_ids:
            result = False
    return result


def get_parents(el):
    parents = []
    parent = el.SuperComponent
    if parent:
        parents.append(parent)
        parents += get_parents(parent)
    return parents


if __name__ == '__main__':
    main()
