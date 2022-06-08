# -*- coding: utf-8 -*-
import clr
import sys
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

script_name = 'Конкатенировать параметры'
param_def_source = None
param_source_name = ''
param_def_target = None
param_target_name = ''
divider = ''


def main():
    utils.init_output()
    try:
        concat_params()
        output.log_success('Готово')
    except Exception as e:
        output.log_error('Произошла ошибка: {}'.format(e))
        print(utils.get_decorated_traceback())


def concat_params():
    utils.check_active_view_is_schedule()
    request_user_config()
    schedule = doc.ActiveView
    number_of_rows = utils.get_number_of_rows_of_schedule(schedule)
    with DB.Transaction(doc, script_name) as transaction:
        transaction.Start()
        start_index = 0 + schedule.Definition.ShowHeaders
        for row_index in range(start_index, number_of_rows):
            row_elements = utils.get_row_elements(schedule, row_index)
            concatenated = collect_values(row_elements)
            set_value_to_els(concatenated, row_elements)
        transaction.Commit()


def request_user_config():
    while True:
        dialog = UI.TaskDialog(script_name)
        dialog.MainContent = 'Выберите источник данных, целевой параметр и ' \
                             'разделитель:'
        dialog.FooterText = 'Для продолжения нажмите ОК или Esc'
        dialog.TitleAutoPrefix = False
        dialog.AllowCancellation = True
        initialize_or_edit_param_source()
        dialog.AddCommandLink(
            UI.TaskDialogCommandLinkId.CommandLink1,
            'Из параметра "{}"'.format(param_source_name),
            'Выбрать другой источник данных'
        )
        initialize_or_edit_param_target()
        dialog.AddCommandLink(
            UI.TaskDialogCommandLinkId.CommandLink2,
            'В параметр "{}"'.format(param_target_name),
            'Выбрать другой целевой параметр'
        )
        initialize_or_edit_divider()
        dialog.AddCommandLink(
            UI.TaskDialogCommandLinkId.CommandLink3,
            'Разделитель "{}"'.format(divider),
            'Задать другой разделитель'
        )
        dialog.CommonButtons = UI.TaskDialogCommonButtons.Close | \
                               UI.TaskDialogCommonButtons.Ok
        dialog.DefaultButton = UI.TaskDialogResult.Ok
        res = dialog.Show()
        if res == UI.TaskDialogResult.CommandLink1:
            initialize_or_edit_param_source(edit=True)
            utils.check(param_target_name)
        elif res == UI.TaskDialogResult.CommandLink2:
            initialize_or_edit_param_target(edit=True)
        elif res == UI.TaskDialogResult.CommandLink3:
            initialize_or_edit_divider(edit=True)
        elif res == UI.TaskDialogResult.Ok or \
                res == UI.TaskDialogResult.Cancel:
            utils.check(param_target_name)
            return
        elif res == UI.TaskDialogResult.Close:
            sys.exit()


def initialize_or_edit_param_source(edit=False):
    global param_def_source
    global param_source_name
    cfg = script.get_config()
    init_value = ''
    default_value = cfg.get_option('concat_params_param_source', init_value)
    default_value = default_value or init_value
    available_param_ids, available_param_names = get_param_info_from_schedule()
    if edit:
        param_name = forms.SelectFromList.show(
            available_param_names,
            button_name='ОК',
            title='Выберите источник данных',
            width=300, height=400
        )
        cfg.concat_params_param_source = param_name
        script.save_config()
    else:
        param_name = default_value
    if param_name not in available_param_names:
        param_name = available_param_names[0]
    param_source_name = param_name
    param_id = available_param_ids[available_param_names.index(param_name)]
    param_def_source = doc.GetElement(param_id).GetDefinition()


def initialize_or_edit_param_target(edit=False):
    global param_def_target
    global param_target_name
    cfg = script.get_config()
    init_value = ''
    default_value = cfg.get_option('concat_params_param_target', init_value)
    default_value = default_value or init_value
    available_param_ids, available_param_names = get_param_info_from_schedule()
    if edit:
        param_name = forms.SelectFromList.show(
            available_param_names,
            button_name='ОК',
            title='Выберите целевой параметр',
            width=300, height=400
        )
        cfg.concat_params_param_target = param_name
        script.save_config()
    else:
        param_name = default_value
    if param_name not in available_param_names:
        param_name = available_param_names[-1]
    param_target_name = param_name
    param_id = available_param_ids[available_param_names.index(param_name)]
    param_def_target = doc.GetElement(param_id).GetDefinition()


def initialize_or_edit_divider(edit=False):
    global divider
    cfg = script.get_config()
    init_value = '; '
    default_value = cfg.get_option(
        'concat_params_divider', init_value)
    default_value = default_value or init_value
    if edit:
        res = forms.ask_for_string(
            default=default_value,
            prompt='Поддерживаются два служебных символа:\n'
                   '\\t – табуляция;\n\\n – перенос строки.',
            title='Укажите разделитель'
        )
        res = res or default_value
        cfg.concat_params_divider = res
        script.save_config()
    else:
        res = default_value
    divider = res


def get_param_info_from_schedule():
    available_param_names = []
    available_param_ids = []
    schedule_field_ids = doc.ActiveView.Definition.GetFieldOrder()
    for id in schedule_field_ids:
        field = doc.ActiveView.Definition.GetField(id)
        name = field.GetName()
        param_id = field.ParameterId
        param_element = doc.GetElement(param_id)
        allowed_p_types = [DB.ParameterType.Text,
                           DB.ParameterType.MultilineText]
        if param_element and param_element.GetDefinition().ParameterType in \
                allowed_p_types:
            available_param_names.append(name)
            available_param_ids.append(param_id)
    return available_param_ids, available_param_names


def collect_values(elements):
    vals = []
    for el in elements:
        param = find_param(el, param_def_source)
        val = param.AsString() or ''
        if val:
            vals.append(val)
        vals = sorted(vals)
    return divider.replace(r'\n', '\n').replace(r'\t', '\t').join(vals)


def find_param(el, param_def):
    el_param = el.get_Parameter(param_def)
    if el_param.Id in [p.Id for p in el.GetOrderedParameters()]:
        return el_param
    type_ = doc.GetElement(el.GetTypeId())
    type_param = type_.get_Parameter(param_def)
    return type_param


def set_value_to_els(value, elements):
    for el in elements:
        parameter = find_param(el, param_def_target)
        if parameter:
            parameter.Set(value)


if __name__ == '__main__':
    main()
