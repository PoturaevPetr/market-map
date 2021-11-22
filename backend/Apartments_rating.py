###Определение последней цены
import dateutil.parser
from pytz import utc

def last_time(data):
    time_new_format = []
    for t in data:
        time_new_format.append(dateutil.parser.parse(t[0]).astimezone(utc))
    index = time_new_format.index(max(time_new_format))
    return data[index][0], data[index][1]
"""Написать алгоритм реализации дополнительного слоя соответствующего подкрашенным маркерам
(аналог погодной карты), использовать градиенты цвета. Найти решение!!!!"""
