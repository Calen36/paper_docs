import datetime
import re
import sqlite3
from copy import copy
from collections import Counter

from django.db.models import Q
from django.shortcuts import render, HttpResponse, redirect
from letters.models import *
import openpyxl


def beautify_name(name):
    parts = name.split()
    for i, v in enumerate(parts):
        if v.isalpha():
            word = v.capitalize()

            word = re.sub(r'еву\b', 'ев', word)
            word = re.sub(r'ову\b', 'ов', word)
            word = re.sub(r'скому\b', 'ский', word)
            word = re.sub(r'ской\b', 'ская', word)
            word = re.sub(r'ну\b', 'н', word)
            word = re.sub(r'евой\b', 'ева', word)
            word = re.sub(r'овой\b', 'ова', word)
            word = re.sub(r'еcю\b', 'есь', word)

            parts[i] = word
    return ' '.join(parts)


def myscript(request):
    procs = ['Прокуратура Западного административного округа г. Краснодара',
    'Прокуратура Центрального административного округа г. Краснодара',
    'Прокуратура  Карасунского административного округа г. Краснодара',
    'Прокуратура  Прикубанского административного округа г. Краснодара',
    'Прокуратура г. Краснодара',
    'Прокуратура г. Новороссийска',
    'Прокуратура г. Сочи - Адлерский район',
    'Прокуратура г. Сочи - Лазаревский район',
    'Прокуратура г. Сочи - Центральный район',
    'Прокуратура г. Сочи - Хостинский район',
    'Прокуратура г. Сочи',
    'Прокуратура Абинского района',
    'Анапская межрайонная прокуратура',
    'Прокуратура Апшеронского района',
    'Прокуратура г. Армавира',
    'Белореченская межрайонная прокуратура',
    'Прокуратура Белоглинского района',
    'Прокуратура Брюховецкого района',
    'Прокуратура Выселковского района',
    'Прокуратура г. Геленджика',
    'Прокуратура г. Горячий Ключ',
    'Прокуратура Гулькевичского района',
    'Прокуратура Динского района',
    'Ейская межрайонная прокуратура',
    'Краснодарская прокуратура по надзору за соблюдением законов в исправительных учреждениях',
    'Прокуратура Кавказского района',
    'Прокуратура Калининского района',
    'Прокуратура Каневского района',
    'Прокуратура Кореновского района',
    'Крымская межрайонная прокуратура',
    'Прокуратура Курганинского района',
    'Прокуратура Кущевского района',
    'Прокуратура Красноармейского района',
    'Прокуратура Крыловского района',
    'Лабинская межрайонная прокуратура',
    'Прокуратура Ленинградского района',
    'Прокуратура Мостовского района',
    'Прокуратура Новокубанского района',
    'Прокуратура Новопокровского района',
    'Прокуратура Отрадненского района',
    'Прокуратура Павловского района',
    'Прокуратура Приморско-Ахтарского района',
    'Славянская межрайонная прокуратура',
    'Прокуратура Северского района',
    'Прокуратура Староминского района',
    'Прокуратура Темрюкского района',
    'Прокуратура Тимашевского района',
    'Туапсинская межрайонная прокуратура',
    'Тихорецкая межрайонная прокуратура',
    'Прокуратура Тбилисского района',
    'Прокуратура Успенского района',
    'Прокуратура Усть-Лабинского района',
    'Прокуратура Щербиновского района',
    'Азово-Черноморская межрайонная природоохранная прокуратура',
    'Сочинская межрайонная природоохранная прокуратура',]


    for proc in procs:
        get_org(proc)

    context = {'stuff': [], 'message': 'DONE'}
    return render(request, template_name='letters/index.html', context=context)


def get_type():
    return LetterType.objects.get(pk=1)


class LetterNotFoundExeption(BaseException):
    pass


def get_parent(num):
    num = num.strip()
    return BaseLetter.objects.get(pk=num)


def get_date(date):
    if isinstance(date, datetime.datetime):
        return date.date()
    elif isinstance(date, str):
        date = date.strip()
        date = date[:10]
        return datetime.datetime.strptime(date, "%d.%m.%Y").date()


def get_counterparty(name):
    name = name.strip()
    if not Counterparty.objects.filter(name=name).exists():
        Counterparty.objects.create(name=name)
    return Counterparty.objects.get(name=name)


def get_executor(string):
    users = string.split('/')
    for i, u in enumerate(users):
        users[i] = u.replace(".", ' ').strip().split(' ')

    result = []
    for user in users:
        if not Executor.objects.filter(Q(surname=user[0]) & Q(name__startswith=user[1]) & Q(patronimic__startswith=user[2])).exists():
            Executor.objects.create(surname=user[0], name=user[1], patronimic=user[2])
        result.append(Executor.objects.get(Q(surname=user[0]) & Q(name__startswith=user[1]) & Q(patronimic__startswith=user[2])))
    return result


def get_delivery(name):
    name = name.strip()
    if not name:
        return
    if not WayOfDelivery.objects.filter(name__icontains=name).exists():
        WayOfDelivery.objects.create(name=name)
    return WayOfDelivery.objects.get(name=name)


def read_xls(request):
    book = openpyxl.load_workbook('in.xlsx')
    sheet = book.worksheets[1]
    log = []
    for row in sheet.values:
        _, date, number, reply_to, out_num, counerparty, subj, signed_by, contact, delivery, recv_date, __, ___, ____, cipher, *_____ = row
        if isinstance(reply_to, str) and (reply_to.strip().startswith('2/') or reply_to.strip().startswith('3/')):
            continue

        if number and date and number != 'Номер' and not BaseLetter.objects.filter(number=number).exists():
            log.append(f"cоздается {number}")
            print(f"cоздается {number}")
            try:
                if not reply_to or reply_to.strip() in ('-',):
                    obj = BaseLetter.objects.create(type=get_type(), sign_date=get_date(date), number=number,
                                                    outgoing_number=out_num,
                                                    counterparty=get_counterparty(counerparty), subj=subj,
                                                    signed_by=signed_by, contact=contact,
                                                    way_of_delivery=get_delivery(delivery),
                                                    receive_date=get_date(recv_date), cipher=cipher)
                else:
                    obj = BaseLetter.objects.create(type=get_type(), sign_date=get_date(date), number=number,
                                                    parent=get_parent(reply_to), outgoing_number=out_num,
                                                    counterparty=get_counterparty(counerparty), subj=subj,
                                                    signed_by=signed_by, contact=contact,
                                                    way_of_delivery=get_delivery(delivery),
                                                    receive_date=get_date(recv_date), cipher=cipher)

                log.append(f"----успешно")
                print(f"----успешно")
            except Exception as ex:
                log.append(f"----{ex}")
                print(f"----{ex}")
            print()

    result = log
    return HttpResponse(result)


def get_org(name):
    name = name.strip()
    if not Organization.objects.filter(name=name).exists():
        Organization.objects.create(name=name)
    return Organization.objects.get(name=name)


def get_pos(name, org):
    name = name.strip()
    if not Position.objects.filter(Q(name=name) & Q(parent=org)).exists():
        Position.objects.create(name=name, parent=org)
    return Position.objects.get(Q(name=name) & Q(parent=org))


def get_geotag(name, parent):
    name = name.strip()
    if not GeoTag.objects.filter(Q(name=name) & Q(parent=parent)).exists():
        GeoTag.objects.create(name=name, parent=parent)
    return GeoTag.objects.get(Q(name=name) & Q(parent=parent))


def rebuld_counterparty(request):
    Counterparty.objects.rebuild()
    context = {'stuff': [], 'message': 'ДЕРЕВО КОНТРАГЕНТОВ ПЕРЕСТРОЕНО'}
    return render(request, template_name='letters/index.html', context=context)



def myscript_cut(request):
    """ВЫЧЛЕНЯЕМ ИЗ ИМЕНИ ЛИЦА ДОЛЖНОСТЬ И ОРГАНИЗАЦИЮ"""
    position_name = 'И.о. прокурора'
    qs = Counterparty.objects.filter(type_id=3).filter(name__icontains=position_name)
    results = []
    for c in qs:
        name = copy(c.name)
        pos = 'И.О. прокурора'
        pers = ''
        for x in re.findall(r"\w*\s\w\.\w\.?$", name):
            pers = x
        org = 'Прокуратура ' + name.replace(position_name, '').replace(pers, '').strip()
        results.append((pos, org, beautify_name(pers)))

        if not all((org, pers)):
            continue

        # organization = get_org(org)
        # position = get_pos(pos, organization)
        # c.name = pers
        # c.parent = position
        # c.save()

    qs = Counterparty.objects.filter(type_id=3).filter(name__icontains=position_name)

    context = {'stuff': results, 'message': 'message'}
    return render(request, template_name='letters/index.html', context=context)


def reduce_pepetitive_ctrp(request):
    """Ищет Контрагентов с одинаковыми строковыми представлениями, удаляет всех кроме 1го и перекидывает ему всех потомков от удаленных"""
    result = ['------------ОРГАНИЗАЦИИ']
    qs = Counterparty.objects.filter(type_id=1)
    workdict = {}
    for ctrp in qs:
        print('.', end='')
        if not str(ctrp) in workdict:
            workdict[str(ctrp)] = ctrp
        else:
            print('\nповтор: ', ctrp)
            result.append(ctrp)
            letters = BaseLetter.objects.filter(counterparty=ctrp)
            for letter in letters:
                letter.counterparty = workdict[str(ctrp)]
                letter.save()
            ctrp.delete()

    result.append('-------------ДОЛЖНОСТИ')
    qs = Counterparty.objects.filter(Q(type_id=2) & Q(parent_id__gt=0))
    workdict = {}
    for ctrp in qs:
        print('.', end='')
        if not str(ctrp) in workdict:
            workdict[str(ctrp)] = ctrp
        else:
            print('\nповтор: ', ctrp)
            result.append(ctrp)
            letters = BaseLetter.objects.filter(counterparty=ctrp)
            for letter in letters:
                letter.counterparty = workdict[str(ctrp)]
                letter.save()
            ctrp.delete()

    result.append('-------------ЛИЦА')
    qs = Counterparty.objects.filter(Q(type_id=2) & Q(parent_id__gt=0))
    workdict = {}
    for ctrp in qs:
        print('.', end='')
        if not str(ctrp) in workdict:
            workdict[str(ctrp)] = ctrp
        else:
            print('\nповтор: ', ctrp)
            result.append(ctrp)
            letters = BaseLetter.objects.filter(counterparty=ctrp)
            for letter in letters:
                letter.counterparty = workdict[str(ctrp)]
                letter.save()
            ctrp.delete()



    context = {'stuff': result, 'message': 'СЛИЯНИЕ ЗАПИСЕЙ ДУБЛИРУЮЩИХСЯ КОНТРАГЕНТОВ'}
    return render(request, template_name='letters/index.html', context=context)


