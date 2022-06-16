# -*- coding: utf-8 -*-
from Autodesk.Revit import DB, Exceptions, UI
from pyrevit import forms

import utils
from bip_group_order import get_group_order_number
from constants import doc, uidoc

params_to_match = []

script_name = 'Сопоставить параметры'
sel = [doc.GetElement(el_id) for el_id in uidoc.Selection.GetElementIds()]


def main():
    utils.init_output_and_safely_run(match_params)


def match_params():
    el = sel[0]
    ask_user_for_params(el)
    if not params_to_match:
        return
    category_name = sel[0].LookupParameter('Категория').AsValueString()
    done = [el]
    with DB.Transaction(doc, script_name) as transaction:
        transaction.Start()
        while True:
            try:
                target = pick_element(category_name)
                set_params(target)
                doc.Regenerate()
                done.append(target)
            except Exceptions.OperationCanceledException:
                break
        transaction.Commit()
    utils.select(done)


def ask_user_for_params(el):
    global params_to_match
    params = [Param(i) for i in el.GetOrderedParameters()]
    params = sorted(params, key=lambda p: p.param_group_order)
    params = [p for p in params if p.is_valid]
    params_to_match = forms.SelectFromList.show(
        params,
        multiselect=True,
        button_name='ОК',
        title='Выберите параметры',
        width=400, height=700
    )


class Param(forms.TemplateListItem):
    def __init__(self, parameter):
        forms.TemplateListItem.__init__(self, parameter)
        self.parameter = parameter
        self.is_read_only = parameter.IsReadOnly
        self.parameter_group = parameter.Definition.ParameterGroup
        self.param_group_order = get_group_order_number(self.parameter_group)
        self.value = parameter.HasValue and (parameter.AsString() or
                                             parameter.AsValueString() or '')
        self.is_valid = not self.is_read_only
        self.state = bool(self.value)

    @property
    def name(self):
        return '{}{}'.format(self.parameter.Definition.Name,
                             ' [{}]'.format(self.value) if self.value else '')


def pick_element(category_name):
    footer_message = 'Выберите следующий элемент категории ' \
                     '{} [Esc для отмены]'.format(category_name)
    reference = uidoc.Selection.PickObject(
        UI.Selection.ObjectType.Element,
        CustomISelectionFilter(category_name),
        footer_message)
    target = doc.GetElement(reference.ElementId)
    return target


class CustomISelectionFilter(UI.Selection.ISelectionFilter):
    def __init__(self, nom_categorie):
        self.nom_categorie = nom_categorie

    def AllowElement(self, e):
        if self.nom_categorie in e.Category.Name:
            return True
        else:
            return False

    def AllowReference(self, ref, point):
        return True


def set_params(target):
    for param in params_to_match:
        target.get_Parameter(param.Definition).Set(get_typed_value(param))


def get_typed_value(param):
    if param.StorageType == DB.StorageType.Integer:
        return param.AsInteger()
    elif param.StorageType == DB.StorageType.Double:
        return param.AsDouble()
    elif param.StorageType == DB.StorageType.String:
        return param.AsString() or ''
    elif param.StorageType == DB.StorageType.ElementId:
        return param.AsElementId()
    raise Exception('Недопустимый тип параметра "{}"'.format(
        param.Definition.Name))


if __name__ == '__main__':
    main()
