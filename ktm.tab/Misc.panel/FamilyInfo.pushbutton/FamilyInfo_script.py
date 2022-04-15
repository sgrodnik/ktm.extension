# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
import datetime
import os
import subprocess as sp
from pyrevit import forms

app = __revit__.Application

time_str = str(datetime.datetime.now()).split('.')[0].replace(':', '-')
log_path = os.getenv('temp') + "\\Family Info " + time_str + ".csv"
log_path_short = os.getenv('temp') + "\\Family Info " + time_str + " short.csv"


def log(s):
    with open(log_path, "a") as myfile:
        myfile.write(s.encode("utf-8") + '\n')


log_info_titles_short = [
    '#',
    'Путь',
    'Размер, Кбайт',
    'Семейство',
    'Количество типоразмеров',
    'Тип параметра',
    'Группа параметров',
    'Имя параметра',
    'GUID',
    'BuiltInParameter',
    'Единицы',
    'По экземпляру',
    # 'Формула',
]


def log_short(s):
    with open(log_path_short, "a") as myfile:
        myfile.write(s.encode("utf-8") + '\n')


log_short('\t'.join(log_info_titles_short))

# GroupOrder = {
#     DB.BuiltInParameterGroup.PG_CONSTRAINTS:                                    1,  # Зависимости
#     DB.BuiltInParameterGroup.PG_CONSTRUCTION:                                   2,  # Строительство
#     DB.BuiltInParameterGroup.PG_REBAR_ARRAY:                                    3,  # Набор арматурных стержней
#     DB.BuiltInParameterGroup.PG_COUPLER_ARRAY:                                  4,  # Набор
#     DB.BuiltInParameterGroup.PG_GRAPHICS:                                       5,  # Графика
#     DB.BuiltInParameterGroup.PG_TEXT:                                           6,  # Текст
#     DB.BuiltInParameterGroup.PG_MATERIALS:                                      7,  # Материалы и отделка
#     DB.BuiltInParameterGroup.PG_DIVISION_GEOMETRY:                              8,  # Геометрия разделения
#     DB.BuiltInParameterGroup.PG_AELECTRICAL:                                    9,  # Электросети
#     DB.BuiltInParameterGroup.PG_ELECTRICAL:                                     10,  # Электросети
#     DB.BuiltInParameterGroup.PG_ELECTRICAL_LIGHTING:                            11,  # Электросети - Освещение
#     DB.BuiltInParameterGroup.PG_ELECTRICAL_LOADS:                               12,  # Электросети - Нагрузки
#     DB.BuiltInParameterGroup.PG_SEGMENTS_FITTINGS:                              13,  # Сегменты и соединительные детали
#     DB.BuiltInParameterGroup.PG_PLUMBING:                                       14,  # Сантехника
#     DB.BuiltInParameterGroup.PG_PRIMARY_END:                                    15,  # Основной конец
#     DB.BuiltInParameterGroup.PG_SECONDARY_END:                                  16,  # Второстепенный конец
#     DB.BuiltInParameterGroup.PG_STRUCTURAL:                                     17,  # Несущие конструкции
#     DB.BuiltInParameterGroup.PG_REBAR_SYSTEM_LAYERS:                            18,  # Слои
#     DB.BuiltInParameterGroup.PG_SLAB_SHAPE_EDIT:                                19,  # Редактирование формы перекрытия
#     DB.BuiltInParameterGroup.PG_GEOMETRY:                                       20,  # Размеры
#     DB.BuiltInParameterGroup.PG_MECHANICAL:                                     21,  # Механизмы
#     DB.BuiltInParameterGroup.PG_MECHANICAL_AIRFLOW:                             22,  # Механизмы - Расход
#     DB.BuiltInParameterGroup.PG_MECHANICAL_LOADS:                               23,  # Механизмы - Нагрузки
#     DB.BuiltInParameterGroup.PG_ANALYTICAL_MODEL:                               24,  # Аналитическая модель
#     DB.BuiltInParameterGroup.PG_ANALYTICAL_ALIGNMENT:                           25,  # Выравнивание аналитической модели
#     DB.BuiltInParameterGroup.PG_RELEASES_MEMBER_FORCES:                         26,  # Снятие связей/усилия для элемента
#     DB.BuiltInParameterGroup.PG_STRUCTURAL_ANALYSIS:                            27,  # Расчет несущих конструкций
#     DB.BuiltInParameterGroup.PG_FORCES:                                         28,  # Силы
#     DB.BuiltInParameterGroup.PG_MOMENTS:                                        29,  # Моменты
#     DB.BuiltInParameterGroup.PG_IDENTITY_DATA:                                  1030,  # Идентификация
#     DB.BuiltInParameterGroup.PG_PHASING:                                        31,  # Стадии
#     DB.BuiltInParameterGroup.PG_ENERGY_ANALYSIS:                                32,  # Расчет энергопотребления
#     DB.BuiltInParameterGroup.PG_IFC:                                            33,  # Параметры IFC
#     DB.BuiltInParameterGroup.PG_FIRE_PROTECTION:                                34,  # Система пожаротушения
#     DB.BuiltInParameterGroup.PG_TITLE:                                          35,  # Шрифт заголовков
#     DB.BuiltInParameterGroup.PG_GREEN_BUILDING:                                 36,  # Свойства экологически чистого здания
#     DB.BuiltInParameterGroup.PG_LIGHT_PHOTOMETRICS:                             37,  # Фотометрические
#     DB.BuiltInParameterGroup.PG_ANALYSIS_RESULTS:                               38,  # Результаты анализа
#     DB.BuiltInParameterGroup.PG_ADSK_MODEL_PROPERTIES:                          39,  # Свойства модели
#     DB.BuiltInParameterGroup.PG_GENERAL:                                        40,  # Общие
#     DB.BuiltInParameterGroup.PG_ELECTRICAL_CIRCUITING:                          41,  # Электросети - Создание цепей
#     DB.BuiltInParameterGroup.PG_DATA:                                           42,  # Данные
#     DB.BuiltInParameterGroup.PG_VISIBILITY:                                     43,  # Видимость
#     DB.BuiltInParameterGroup.PG_OVERALL_LEGEND:                                 44,  # Общая легенда
#     DB.BuiltInParameterGroup.INVALID:                                           45,  # Прочее
#     DB.BuiltInParameterGroup.PG_ANALYTICAL_PROPERTIES:                          101,  # Свойства аналитической модели
#     DB.BuiltInParameterGroup.PG_AREA:                                           102,  # Площадь
#     DB.BuiltInParameterGroup.PG_CONCEPTUAL_ENERGY_DATA:                         103,  # Концептуальное энергопотребление
#     DB.BuiltInParameterGroup.PG_CONCEPTUAL_ENERGY_DATA_BUILDING_SERVICES:       104,  # Модель энергопотребления - Инженерные сети здания
#     DB.BuiltInParameterGroup.PG_CONTINUOUSRAIL_BEGIN_BOTTOM_EXTENSION:          105,  # Примыкание (начало/низ)
#     DB.BuiltInParameterGroup.PG_CONTINUOUSRAIL_END_TOP_EXTENSION:               106,  # Примыкание (конец/верх)
#     DB.BuiltInParameterGroup.PG_CURTAIN_GRID:                                   107,  # Сетка
#     DB.BuiltInParameterGroup.PG_CURTAIN_GRID_1:                                 108,  # Сетка 1
#     DB.BuiltInParameterGroup.PG_CURTAIN_GRID_2:                                 109,  # Сетка 2
#     DB.BuiltInParameterGroup.PG_CURTAIN_GRID_HORIZ:                             110,  # Горизонтальная сетка
#     DB.BuiltInParameterGroup.PG_CURTAIN_GRID_U:                                 111,  # Линии сетки U
#     DB.BuiltInParameterGroup.PG_CURTAIN_GRID_V:                                 112,  # Линии сетки V
#     DB.BuiltInParameterGroup.PG_CURTAIN_GRID_VERT:                              113,  # Вертикальная сетка
#     DB.BuiltInParameterGroup.PG_CURTAIN_MULLION_1:                              114,  # Импосты сетки 1
#     DB.BuiltInParameterGroup.PG_CURTAIN_MULLION_2:                              115,  # Импосты сетки 2
#     DB.BuiltInParameterGroup.PG_CURTAIN_MULLION_HORIZ:                          116,  # Горизонтальные импосты
#     DB.BuiltInParameterGroup.PG_CURTAIN_MULLION_VERT:                           117,  # Вертикальные импосты
#     DB.BuiltInParameterGroup.PG_DISPLAY:                                        118,  # Представление
#     DB.BuiltInParameterGroup.PG_ENERGY_ANALYSIS_ADVANCED:                       119,  # Расширенная
#     DB.BuiltInParameterGroup.PG_ENERGY_ANALYSIS_BLDG_CONS_MTL_THERMAL_PROPS:    120,  # Тепловые свойства материала
#     DB.BuiltInParameterGroup.PG_ENERGY_ANALYSIS_BUILDING_DATA:                  121,  # Данные о здании
#     DB.BuiltInParameterGroup.PG_ENERGY_ANALYSIS_CONCEPTUAL_MODEL:               122,  # Аналитическая модель энергопотребления
#     DB.BuiltInParameterGroup.PG_ENERGY_ANALYSIS_DETAILED_AND_CONCEPTUAL_MODELS: 123,  # Основная
#     DB.BuiltInParameterGroup.PG_ENERGY_ANALYSIS_DETAILED_MODEL:                 124,  # Подробная модель
#     DB.BuiltInParameterGroup.PG_ENERGY_ANALYSIS_ROOM_SPACE_DATA:                125,  # Данные о помещении/пространстве
#     DB.BuiltInParameterGroup.PG_FABRICATION_PRODUCT_DATA:                       126,  # Данные о продукте производителя
#     DB.BuiltInParameterGroup.PG_FITTING:                                        127,  # Соединительные детали
#     DB.BuiltInParameterGroup.PG_FLEXIBLE:                                       128,  # Адаптивный компонент
#     DB.BuiltInParameterGroup.PG_GEO_LOCATION:                                   129,  # Геопозиционирование
#     DB.BuiltInParameterGroup.PG_GEOMETRY_POSITIONING:                           130,  # Геометрическое положение
#     DB.BuiltInParameterGroup.PG_INSULATION:                                     131,  # Изоляционный слой
#     DB.BuiltInParameterGroup.PG_LENGTH:                                         132,  # Длина
#     DB.BuiltInParameterGroup.PG_LINING:                                         133,  # Внутренняя изоляция
#     DB.BuiltInParameterGroup.PG_NODES:                                          134,  # Узлы
#     DB.BuiltInParameterGroup.PG_PATTERN:                                        135,  # Образец
#     DB.BuiltInParameterGroup.PG_PATTERN_APPLICATION:                            136,  # Применение образца
#     DB.BuiltInParameterGroup.PG_PROFILE:                                        137,  # Профиль
#     DB.BuiltInParameterGroup.PG_PROFILE_1:                                      138,  # Профиль 1
#     DB.BuiltInParameterGroup.PG_PROFILE_2:                                      139,  # Профиль 2
#     DB.BuiltInParameterGroup.PG_RAILING_SYSTEM_FAMILY_HANDRAILS:                140,  # Перила 1
#     DB.BuiltInParameterGroup.PG_RAILING_SYSTEM_FAMILY_SEGMENT_PATTERN:          141,  # Образец сегмента (по умолчанию)
#     DB.BuiltInParameterGroup.PG_RAILING_SYSTEM_FAMILY_TOP_RAIL:                 142,  # Верхний поручень
#     DB.BuiltInParameterGroup.PG_RAILING_SYSTEM_SECONDARY_FAMILY_HANDRAILS:      143,  # Перила 2
#     DB.BuiltInParameterGroup.PG_RAILING_SYSTEM_SEGMENT_PATTERN_REMAINDER:       144,  # Остаток образца
#     DB.BuiltInParameterGroup.PG_RAILING_SYSTEM_SEGMENT_PATTERN_REPEAT:          145,  # Повтор образца
#     DB.BuiltInParameterGroup.PG_RAILING_SYSTEM_SEGMENT_POSTS:                   146,  # Стойки
#     DB.BuiltInParameterGroup.PG_RAILING_SYSTEM_SEGMENT_U_GRID:                  147,  # Линии сетки U
#     DB.BuiltInParameterGroup.PG_RAILING_SYSTEM_SEGMENT_V_GRID:                  148,  # Линии сетки V
#     DB.BuiltInParameterGroup.PG_REFERENCE:                                      149,  # Ссылка
#     DB.BuiltInParameterGroup.PG_ROTATION_ABOUT:                                 150,  # Поворот вокруг оси
#     DB.BuiltInParameterGroup.PG_ROUTE_ANALYSIS:                                 151,  # Анализ трассировки
#     DB.BuiltInParameterGroup.PG_SPLIT_PROFILE_DIMENSIONS:                       152,  # Размеры (линейные единицы или % от толщины)
#     DB.BuiltInParameterGroup.PG_STAIR_RISERS:                                   153,  # Подступенки
#     DB.BuiltInParameterGroup.PG_STAIR_STRINGERS:                                154,  # Косоуры/Тетивы
#     DB.BuiltInParameterGroup.PG_STAIR_TREADS:                                   155,  # Проступи
#     DB.BuiltInParameterGroup.PG_STAIRS_CALCULATOR_RULES:                        156,  # Правила расчета
#     DB.BuiltInParameterGroup.PG_STAIRS_OPEN_END_CONNECTION:                     157,  # Соединение в конце
#     DB.BuiltInParameterGroup.PG_STAIRS_SUPPORTS:                                158,  # Опоры
#     DB.BuiltInParameterGroup.PG_STAIRS_TREADS_RISERS:                           159,  # Проступи/подступенки
#     DB.BuiltInParameterGroup.PG_STAIRS_WINDERS:                                 160,  # Забежные ступени
#     DB.BuiltInParameterGroup.PG_STRUCTURAL_SECTION_GEOMETRY:                    161,  # Геометрия сечения несущей конструкции
#     DB.BuiltInParameterGroup.PG_SUPPORT:                                        162,  # Опоры
#     DB.BuiltInParameterGroup.PG_SYSTEMTYPE_RISEDROP:                            163,  # Подъем/опуск
#     DB.BuiltInParameterGroup.PG_TERMINTATION:                                   164,  # Ограничения
#     DB.BuiltInParameterGroup.PG_TRANSLATION_IN:                                 165,  # Перемещение по направлению оси
#     DB.BuiltInParameterGroup.PG_TRUSS_FAMILY_BOTTOM_CHORD:                      166,  # Нижние пояса
#     DB.BuiltInParameterGroup.PG_TRUSS_FAMILY_DIAG_WEB:                          167,  # Раскосные решетки
#     DB.BuiltInParameterGroup.PG_TRUSS_FAMILY_TOP_CHORD:                         168,  # Верхние пояса
#     DB.BuiltInParameterGroup.PG_TRUSS_FAMILY_VERT_WEB:                          169,  # Стойки
#     DB.BuiltInParameterGroup.PG_UNDERLAY:                                       170,  # Подложка
#     DB.BuiltInParameterGroup.PG_VIEW_CAMERA:                                    171,  # Камера
#     DB.BuiltInParameterGroup.PG_VIEW_EXTENTS:                                   172,  # Границы
# }

has_DUT_parameterTypes = [
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

# for i in app.Documents:
#     print(i.Title)
#     print(i.PathName)


class Fam:
    objects = []

    def __init__(self, path):
        self.__class__.objects.append(self)
        self.path = path
        try:
            self.size = os.path.getsize(path) / 1024
            self.doc = app.OpenDocumentFile(path)
            self.title = self.doc.Title
        # self.params = []
            self.types = list(self.doc.FamilyManager.Types)
            self.types = self.types if len(self.types) == 1 else [i for i in self.types if i.Name != ' ']
            try:
                self.params = [Param_short(p, self).log() for p in self.doc.FamilyManager.GetParameters()]
            except Exception as e:
                log_short('Ошибка семейства: ' + self.path + ': ' + str(e))
                # raise
            # LIMIT = 10
            # if len(self.types) > LIMIT:
            #     print('Предупреждение ({}): Количество типов урезано с {} до {} (см. переменную LIMIT)'.format(path, len(self.types), LIMIT))
            # self.types = self.types[:LIMIT]
            # if False:
            #     self.type_values = [TypeValue(t, self) for t in self.types]
        except Exception as e:
            log('Ошибка семейства: ' + self.path + ': ' + str(e))
            # raise
        finally:
            try:
                self.doc.Close(False)
            except:
                pass


# class TypeValue:
#     objects = []
#     counter = 0

#     def __init__(self, Type, Fam):
#         self.__class__.counter += 1
#         self.__class__.objects.append(self)
#         self.id = self.__class__.counter
#         self.fam = Fam
#         # self.values_by_param = [(p, GetVal(Type, Param(p, self.fam), self.fam.doc)) for p in self.fam.doc.FamilyManager.GetParameters()]
#         try:
#             ordered_params = sorted(self.fam.doc.FamilyManager.GetParameters(), key=lambda p: GroupOrder[p.Definition.ParameterGroup])
#             [GetVal(Type, Param(p, self.fam), self.fam.doc) for p in ordered_params]
#         except Exception as e:
#             log('Ошибка типа: ' + Type.Name + ': ' + str(e))
#             raise


def HasDisplayUnitType(fam_param):
    parameterType = fam_param.Definition.ParameterType
    return parameterType in has_DUT_parameterTypes or 100 < int(parameterType)


# def GetVal(Type, Param, doc):
#     fam_param = Param.param
#     # value_as_string = Type.AsValueString(fam_param)
#     if fam_param.StorageType == DB.StorageType.Double:
#         value = Type.AsDouble(fam_param)
#         if HasDisplayUnitType(fam_param):
#             value = str(DB.UnitUtils.ConvertFromInternalUnits(value,
#                 fam_param.DisplayUnitType)) if value is not None else ''
#     elif fam_param.StorageType == DB.StorageType.ElementId:
#         id = Type.AsElementId(fam_param)
#         e = doc.GetElement(id)
#         # value = str(id.IntegerValue) + ' ' + e.Name if e else ''
#         try:
#             value = '{} <id {}>'.format(e.Name, id.IntegerValue) if e else ''
#         except:
#             value = '??? <id {}>'.format(id.IntegerValue) if e else ''
#     elif fam_param.StorageType == DB.StorageType.Integer:
#         value = str(Type.AsInteger(fam_param))
#     elif fam_param.StorageType == DB.StorageType.String:
#         value = str(Type.AsString(fam_param) or '').replace('\n', '\\n').replace('\r', '\\r')
#     # log('{}\t{}\t{}'.format(Type.Name, Param.info, value))

#     info_items = []
#     info_items.append(Param.id)
#     info_items.append(Param.fam.path)
#     info_items.append(Param.fam.size)
#     info_items.append(Param.fam.title)
#     info_items.append(Type.Name)
#     info_items.append(Param.parameter_group)
#     info_items.append(Param.name)
#     info_items.append(Param.guid)
#     info_items.append(Param.built_in_parameter)
#     info_items.append(fam_param.StorageType)
#     info_items.append(Param.parameter_type)
#     info_items.append(DB.LabelUtils.GetLabelFor(Param.units) if Param.units else '')
#     info_items.append('По экземпляру' if Param.is_instance else 'По типу')
#     # info_items.append(value_as_string)
#     info_items.append(value)
#     info_items.append(Param.formula or '')

#     info = '\t'.join([str(i) for i in info_items])
#     log(info)

#     # return value, value_as_string


def Convert(val, DisplayUnitType):
    DB.UnitUtils.ConvertFromInternalUnits(val, Param.DisplayUnitType)


class Param:
    objects = []
    counter = 0

    def __init__(self, Param, Fam):
        self.__class__.counter += 1
        self.__class__.objects.append(self)
        self.id = self.__class__.counter
        self.fam = Fam
        self.param = Param
        self.name = Param.Definition.Name
        try:
            try:
                self.parameter_type = DB.LabelUtils.GetLabelFor(Param.Definition.ParameterType)
            except:
                self.parameter_type = Param.Definition.ParameterType
            self.parameter_group = DB.LabelUtils.GetLabelFor(Param.Definition.ParameterGroup)
            self.is_shared = Param.IsShared
            self.guid = Param.GUID if self.is_shared else ''
            self.built_in_parameter = Param.Definition.BuiltInParameter
            self.formula = Param.Formula
            self.is_instance = Param.IsInstance
    # info_items.append(DB.LabelUtils.GetLabelFor(Param.units) if Param.units else '')
            # try:
            self.units = DB.LabelUtils.GetLabelFor(Param.DisplayUnitType) if HasDisplayUnitType(Param) else Param.DisplayUnitType
            # except:
            #     self.units = ''
        except Exception as e:
            log('Ошибка параметра: ' + self.name + ': ' + str(e))


class Param_short:
    objects = []
    counter = 0

    def __init__(self, Param, Fam):
        self.__class__.counter += 1
        self.__class__.objects.append(self)
        self.id = self.__class__.counter
        self.fam = Fam
        self.param = Param
        self.name = Param.Definition.Name
        try:
            try:
                self.parameter_type = DB.LabelUtils.GetLabelFor(Param.Definition.ParameterType)
            except:
                self.parameter_type = Param.Definition.ParameterType
            self.parameter_group = DB.LabelUtils.GetLabelFor(Param.Definition.ParameterGroup)
            self.is_shared = Param.IsShared
            self.guid = Param.GUID if self.is_shared else ''
            self.built_in_parameter = str(Param.Definition.BuiltInParameter).replace('INVALID', '')
            self.formula = Param.Formula
            self.is_instance = Param.IsInstance
            # try:
            self.units = ''
            if Param.StorageType == DB.StorageType.Double and HasDisplayUnitType(Param):
                self.units = DB.LabelUtils.GetLabelFor(Param.DisplayUnitType)
            # self.units = DB.LabelUtils.GetLabelFor(Param.DisplayUnitType) if HasDisplayUnitType(Param) else Param.DisplayUnitType if Param.StorageType == DB.StorageType.Double else ''
            # except:
            #     self.units = ''
        except Exception as e:
            log('Ошибка параметра: ' + self.name + ': ' + str(e))
            # raise

    def log(self):
        info_items = []
        info_items.append(self.__class__.counter)
        info_items.append(self.fam.path)
        info_items.append(self.fam.size)
        info_items.append(self.fam.title)
        info_items.append(len(self.fam.types))
        info_items.append(self.parameter_type)
        info_items.append(self.parameter_group)
        info_items.append(self.name)
        info_items.append(self.guid)
        info_items.append(self.built_in_parameter)
        info_items.append(self.units)
        info_items.append('По экземпляру' if self.is_instance else 'По типу')
        # info_items.append(self.formula)
        info = '\t'.join([str(i) for i in info_items])
        log_short(info)


log_info_titles = [
    '#',
    'Путь',
    'Размер, Кбайт',
    'Семейство',
    'Типоразмер',
    'Группа параметров',
    'Имя параметра',
    'GUID',
    'BuiltInParameter',
    'Тип данных',
    'Тип параметра',
    'Единицы',
    'По экземпляру',
    'Значение',
    'Формула',
]
log('\t'.join(log_info_titles))

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
            Fam(path)
    # sp.Popen(["notepad.exe", log_path])
    sp.Popen(["notepad.exe", log_path_short])

# Fam(r"C:\Users\hp22\Desktop\Семейство1.rfa")
# sp.Popen(["notepad.exe", log_path])

    # import shlex, subprocess
    # args = shlex.split('explorer.exe /select, "{}"'.format(doc.PathName))
    # subprocess.Popen(args)
