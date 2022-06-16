# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from System.Collections.Generic import List
from pyrevit import script

import utils

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
output = script.get_output()

script_name = 'Выбрать сегмент'


def main():
    utils.init_output()
    try:
        select_segment()
        output.log_success('Готово')
    except Exception as e:
        output.log_error('Произошла ошибка: {}'.format(e))
        print(utils.get_decorated_traceback())


def select_segment():
    initial_lines = []
    for el in get_selected_element():
        if type(el) == DB.DetailLine:
            initial_lines.append(el)
        elif type(el) == DB.FamilyInstance:
            initial_lines += get_underlying_lines(el)
    adjacent_lines = get_adjacent_lines(initial_lines)
    adjacent_els = []
    for line in adjacent_lines:
        adjacent_els += get_detail_components_located_on_line(line)
    if adjacent_els:
        if __shiftclick__:
            select(adjacent_els + adjacent_lines)
        else:
            select(adjacent_els)
    else:
        select(adjacent_lines)


def get_selected_element():
    sel = [doc.GetElement(el_id) for el_id in uidoc.Selection.GetElementIds()]
    return sel


def get_underlying_lines(el):
    bounding_box = el.get_BoundingBox(doc.ActiveView)
    outline = DB.Outline(bounding_box.Min, bounding_box.Max)
    bb_filter = DB.BoundingBoxIntersectsFilter(outline)
    collector = DB.FilteredElementCollector(doc).WherePasses(bb_filter)\
        .ToElements()
    return list(collector)


def get_adjacent_lines(lines):
    result_elements = []
    for line in lines:
        current_ids = [line.Id]
        visited_ids = []
        counter = 0
        while len(current_ids) > 0:
            visited_ids += current_ids
            neighbour_ids = []
            for id in current_ids:
                counter += 1
                el = doc.GetElement(id)
                lines = get_elements_at_join(el)
                lines = [i for i in lines if i.Id not in visited_ids]
                neighbour_ids += list(set(i.Id for i in lines))
            current_ids = neighbour_ids
        chain = [doc.GetElement(id) for id in visited_ids]
        result_elements += chain
    return result_elements


def get_elements_at_join(line):
    lines = []
    for end_index in [0, 1]:
        els = list(line.Location.ElementsAtJoin[end_index])
        lines += [el for el in els if el.Id != line.Id and
                  is_not_t_intersection(stem=line, cap=el)]
    return lines


def is_not_t_intersection(stem, cap):
    cap_neighbours = list(cap.Location.ElementsAtJoin[0]) \
                     + list(cap.Location.ElementsAtJoin[1])
    return stem.Id in [i.Id for i in cap_neighbours]


def get_detail_components_located_on_line(line):
    collector = DB.FilteredElementCollector(doc) \
        .OfCategory(DB.BuiltInCategory.OST_DetailComponents) \
        .WhereElementIsNotElementType()
    els = []
    for el in collector:
        if does_element_belong_to_line(el, line):
            els.append(el)
    return els


def does_element_belong_to_line(el, line):
    if type(el.Location) is not DB.LocationPoint:
        return False
    point = el.Location.Point
    intersection_result = line.GeometryCurve.Project(point)
    is_far_away = intersection_result.Distance > utils.mm_to_ft(0.1)
    if is_far_away:
        return False
    normalized_parameter  = line.GeometryCurve.ComputeNormalizedParameter(
        intersection_result.Parameter)
    projection_is_between_ends = 0 < normalized_parameter < 1
    return projection_is_between_ends


def select(elements):
    if len(elements):
        if type(elements[0]) is not DB.ElementId:
            elements = [el.Id for el in elements]
        uidoc.Selection.SetElementIds(List[DB.ElementId](elements))


if __name__ == '__main__':
    main()
