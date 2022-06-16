# -*- coding: utf-8 -*-
import sys
import traceback

from Autodesk.Revit import DB, UI
from System.Collections.Generic import List
from pyrevit import script

from constants import uidoc

output = script.get_output()

MM_IN_FT = 304.8


def init_output_and_safely_run(function):
    init_output()
    try:
        function()
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


def mm_to_ft(mm):
    return mm / MM_IN_FT


def ft_to_mm(ft):
    return ft * MM_IN_FT


def exit():
    sys.exit()


def select(elements):
    if elements:
        if type(elements[0]) is not DB.ElementId:
            elements = [el.Id for el in elements]
        uidoc.Selection.SetElementIds(List[DB.ElementId](elements))


class CategoryNameSelectionFilter(UI.Selection.ISelectionFilter):
    def __init__(self, category_name):
        self.category_name = category_name

    def AllowElement(self, e):
        if self.category_name in e.Category.Name:
            return True
        else:
            return False

    def AllowReference(self, ref, point):
        return True
