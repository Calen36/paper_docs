import datetime
import sqlite3

from django.db.models import Q
from django.shortcuts import render, HttpResponse, redirect
from letters.models import *
import openpyxl

def get_extended_letter_url(request, tail):
    pk = tail.replace('/change/', '').replace('_2F', '/')
    object = BaseLetter.objects.get(pk=pk)
    # return HttpResponse(f"{pk}")
    return redirect(object.get_extension_url())


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


def myscript(request):
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



def myscript(request):
    with sqlite3.connect('old.sqlite3') as conn:
        cur = conn.cursor()
        cur.execute('SELECT number, subj, sign_date, inbound_number, signed_by, contact, receive_date, send_date, cipher, counterparty_id, type_id, way_of_delivery_id, parent_id FROM letters_baseletter WHERE level == 1')
        results = cur.fetchall()
        for number, subj, sign_date, inbound_number, signed_by, contact, receive_date, send_date, cipher, counterparty_id, type_id, way_of_delivery_id, parent_id in results:
            counterparty = Counterparty.objects.get(pk=counterparty_id)
            type = LetterType.objects.get(pk=type_id)
            parent = BaseLetter.objects.get(number=parent_id)
            if way_of_delivery_id:
                way_of_delivery = WayOfDelivery.objects.get(pk=way_of_delivery_id)
                BaseLetter.objects.create(number=number, subj=subj, sign_date=sign_date, inbound_number=inbound_number,
                                  signed_by=signed_by, contact=contact, receive_date=receive_date, send_date=send_date,
                                  cipher=cipher, counterparty=counterparty, type=type, way_of_delivery=way_of_delivery,
                                  parent=parent)
            else:
                BaseLetter.objects.create(number=number, subj=subj, sign_date=sign_date, inbound_number=inbound_number,
                                  signed_by=signed_by, contact=contact, receive_date=receive_date, send_date=send_date,
                                  cipher=cipher, counterparty=counterparty, type=type, parent=parent)
                pass
        context = {'stuff': results, 'message': 'message'}
        return render(request, template_name='letters/index.html', context=context)

#
# def myscript(request):
#     book = openpyxl.load_workbook('settlements.xlsx')
#     sheet = book.worksheets[0]
#     results = []
#     krd = GeoTag.objects.get(name='Краснодарский край')
#     message = krd
#     for row in sheet.values:
#         if not row[0].startswith('ГО'):
#             if ' СП ' in row[0]:
#                 setl, raion = row[0][:-3].split(' СП ')
#                 setl = setl.strip() + ' с.п.'
#             elif ' ГП ' in row[0]:
#                 setl, raion = row[0][:-3].split(' ГП ')
#                 setl = setl.strip() + ' г.п.'
#             else:
#                 results.append(row[0])
#
#     context = {'stuff': results, 'message': message}
#     return render(request, template_name='letters/index.html', context=context)



# def myscript(request):
#     return None
#     """ Создание категорий и подкатегорий контрагентов"""
#     rns = ['Белореченское г.п.', 'Бжедуховское с.п.', 'Великовечненское с.п.', 'Дружненское с.п.', 'Первомайское с.п.', 'Пшехское с.п.', 'Родниковское с.п.', 'Рязанское с.п.', 'Черниговское с.п.', 'Школьненское с.п.', 'Южненское с.п.']
#
#     for r in rns:
#         region = GeoTag.objects.get(name__startswith='Белореченский')
#
#         GeoTag.objects.create(name=r, parent=region)
#
#     context = {'stuff': GeoTag.objects.all(), 'message': ''}
#     return render(request, template_name='letters/index.html', context=context)
#
