# -*- coding: utf-8 -*-
import clr
import traceback

import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI
from pyrevit import forms
from pyrevit import script
from System import Guid

clr.AddReference('System')

doc = __revit__.ActiveUIDocument.Document
output = script.get_output()
cache = {}


def init_output():
    output.close_others(all_open_outputs=True)
    output.self_destruct(120)


def get_decorated_traceback():
    trace = traceback.format_exc()
    trace = '-' * 100 + '\nСтек вызовов: {}\n'.format(trace) + '-' * 100
    return trace


def get_number_of_rows_of_schedule(schedule):
    table = schedule.GetTableData().GetSectionData(DB.SectionType.Body)
    number_of_rows = table.NumberOfRows
    return number_of_rows


def get_row_elements(schedule, row_number):
    cur_schedule_elem_ids = DB.FilteredElementCollector(doc, schedule.Id) \
        .ToElementIds()
    elements = [doc.GetElement(id) for id in cur_schedule_elem_ids if
                id not in get_elem_ids_from_other_rows(schedule, row_number)]
    return elements


def get_elem_ids_from_other_rows(schedule, row_number_to_exclude):
    if row_number_to_exclude not in cache:
        with DB.SubTransaction(doc) as t:
            t.Start()
            table = schedule.GetTableData().GetSectionData(DB.SectionType.Body)
            try:
                table.RemoveRow(row_number_to_exclude)
            except:
                if 'row_number' in globals():
                    global row_number
                    if type(row_number) == int:
                        row_number -= 1
            remains = DB.FilteredElementCollector(doc, schedule.Id)\
                        .ToElementIds()
            cache[row_number_to_exclude] = remains
            t.RollBack()
    return cache[row_number_to_exclude]


def check_active_view_is_schedule():
    if not doc.ActiveView.ViewType == DB.ViewType.Schedule:
        raise Exception('Требуется открыть спецификацию')


def check(param_name):
    if param_is_in_filters_or_sorting(param_name):
        raise Exception(
            'Выбранный параметр ' +
            '{} используется в фильтрации или сортировке'.format(param_name))


def param_is_in_filters_or_sorting(param_name):
    group_sort_fields = list(doc.ActiveView.Definition.GetSortGroupFields())
    group_sort_fields += list(doc.ActiveView.Definition.GetFilters())
    for field in group_sort_fields:
        banned_field_name = doc.ActiveView.Definition\
            .GetField(field.FieldId).GetName()
        if param_name == banned_field_name:
            return True
    return False

