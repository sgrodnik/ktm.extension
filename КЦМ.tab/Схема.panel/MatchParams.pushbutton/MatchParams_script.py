# -*- coding: utf-8 -*-
from Autodesk.Revit import DB, Exceptions, UI
from pyrevit import forms
from pyrevit import script

import utils
from bip_group_order import get_group_order_number
from constants import doc, uidoc, sel, shift_click

params_to_match = []
denied_params = []
source_el = None

script_name = 'Сопоставить параметры'


def main():
    utils.init_output_and_safely_run(match_params)


def match_params():
    global source_el
    if not sel:
        return
    source_el = sel[0]
    ask_user_for_params()
    if not params_to_match:
        return
    category_name = sel[0].LookupParameter('Категория').AsValueString()
    done = [source_el]
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
        transaction.SetName('{} ({} эл.)'.format(transaction.GetName(),
                                                 len(done) - 1))
        transaction.Commit()
    utils.select(done)


def ask_user_for_params():
    global params_to_match
    initialize_or_edit_deny_list(edit=shift_click)
    params = []
    for p in source_el.GetOrderedParameters():
        is_checked = False if p.Definition.Name in denied_params else None
        params.append(Param(p, is_checked=is_checked))
    params = sorted(params, key=lambda p: p.param_group_order)
    params = [p for p in params if p.is_valid]
    title = 'Выберите параметры (в черном листе {} эл.)'.format(
        len(denied_params))
    params_to_match = forms.SelectFromList.show(
        params,
        multiselect=True,
        button_name='ОК',
        title=title,
        width=450, height=700
    )


def initialize_or_edit_deny_list(edit=False):
    global denied_params
    denied_params = restore_denied_params()
    if not edit:
        return
    params = []
    for p in source_el.GetOrderedParameters():
        params.append(Param(p, is_checked=p.Definition.Name in denied_params))
    params = sorted(params, key=lambda p: p.param_group_order)
    params = [p for p in params if p.is_valid]
    params_to_deny = forms.SelectFromList.show(
        params,
        multiselect=True,
        button_name='ОК',
        title='Чёрны лист',
        width=450, height=700
    )
    store_denied_params(params_to_deny)


def restore_denied_params():
    cfg = script.get_config()
    params = cfg.get_option('denied_params', [])
    return params


def store_denied_params(params):
    global denied_params
    if params is None:
        return
    denied_params = [param.Definition.Name for param in params]
    cfg = script.get_config()
    cfg.denied_params = denied_params
    script.save_config()


class Param(forms.TemplateListItem):
    def __init__(self, parameter, is_checked=None):
        forms.TemplateListItem.__init__(self, parameter)
        self.parameter = parameter
        self.is_read_only = parameter.IsReadOnly
        self.parameter_group = parameter.Definition.ParameterGroup
        self.param_group_order = get_group_order_number(self.parameter_group)
        self.value = parameter.HasValue and (parameter.AsString() or
                                             parameter.AsValueString() or '')
        self.is_valid = not self.is_read_only
        if is_checked is None:
            self.state = bool(self.value)
        else:
            self.state = is_checked

    @property
    def name(self):
        return '{}{}'.format(self.parameter.Definition.Name,
                             ' [{}]'.format(self.value) if self.value else '')


def pick_element(category_name):
    footer_message = 'Выберите следующий элемент категории ' \
                     '{} [Esc для отмены]'.format(category_name)
    reference = uidoc.Selection.PickObject(
        UI.Selection.ObjectType.Element,
        utils.CategoryNameSelectionFilter(category_name),
        footer_message)
    target = doc.GetElement(reference.ElementId)
    return target


def set_params(target):
    for param in params_to_match:
        parameter = target.get_Parameter(param.Definition) or \
                    target.LookupParameter(param.Definition.Name)
        if not parameter or parameter.IsReadOnly:
            continue
        parameter.Set(get_typed_value(param))


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
