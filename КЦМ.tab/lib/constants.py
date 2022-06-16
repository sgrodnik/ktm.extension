app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
sel = [doc.GetElement(el_id) for el_id in uidoc.Selection.GetElementIds()]
shift_click = __shiftclick__
