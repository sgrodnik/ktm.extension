# -*- coding: utf-8 -*-
import datetime
import os
import subprocess as sp

app = __revit__.Application

time_str = str(datetime.datetime.now()).split('.')[0].replace(':', '-')
log_path = os.getenv('temp') + "\\Family Info " + time_str + ".log"
# os.remove(log_path)
def log(s):
    with open(log_path, "a") as myfile:
        myfile.write(s.encode("utf-8") + '\n')


class Fam:
    objects = []

    def __init__(self, path):
        self.__class__.objects.append(self)
        self.path = path
        self.size = os.path.getsize(path)
        self.doc = app.OpenDocumentFile(path)
        self.title = self.doc.Title
        self.params = []
        try:
            self.params = [Param(p, self) for p in self.doc.FamilyManager.Parameters]
        except Exception as e:
            log('Ошибка: '+ self.path + ': ' + str(e))
        finally:
            self.doc.Close(False)

    def __str__(self):
        return "{}".format('\n'.join(self.params))


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
        self.is_shared = Param.IsShared
        self.guid = Param.GUID if self.is_shared else None
        self.formula = Param.Formula
        self.is_instance = Param.IsInstance
        try:
            self.units = Param.DisplayUnitType
        except:
            self.units = None
        self.info_items = []
        self.info_items.append(self.id)
        self.info_items.append(self.fam.title)
        self.info_items.append(self.fam.size)
        self.info_items.append(self.fam.path)
        self.info_items.append(self.name)
        self.info_items.append(self.guid)
        self.info_items.append(self.units)
        self.info_items.append(self.is_instance)

        self.info = '\t'.join([str(i) for i in self.info_items])

        log(self.info)

    def __str__(self):
        return "{} - {} - {}".format(self.fam, self.name, self.units)


paths = [
    r'C:\Users\hp22\Desktop\test fams\КЦМ_Hencon_УстановкаВакуумная_черт1080-06-0017.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_Вентилятор_Радиальный_Вытяжной_Совплим_Серия FUK.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_ДушАварийный_HAWS.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_ЕмкостьV=2м3_черт6682.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_Емкость_V=0.375м3_чертПИ15728.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_ЕмкостьДляАммиачнойВоды V=2м3_черт13386.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_ЕмкостьСтеклопластиковая_СПКЕ-5699.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_ЕмкостьСтеклопластиковая_черт15365-Э.ОЛ8.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_КонвекторЭлектрический_Nobo.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_ЛовушкаВакуумная_черт2722.0001.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_ЛовушкаВакуумнаяИзТитана_черт3445А.0001.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_МолотковаяДвухроторнаяДробилка_С-599_черт12578.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_Монтежю V=0.4м3_черт4550_Мод 2.rfa',
    # r'C:\Users\hp22\Desktop\test fams\КЦМ_Насос_Мембранный_Delmeco.rfa',
    r"C:\Users\hp22\Desktop\Семейство1.rfa"
]

log_info_titles = [
    'Счётчик',
    'Название',
    'Размер, байт',
    'Путь',
    'Имя параметра',
    'GUID',
    'Единицы',
    'По экземпляру',
    ]

log('\t'.join(log_info_titles))

[Fam(path) for path in paths]

sp.Popen(["notepad.exe", log_path])
