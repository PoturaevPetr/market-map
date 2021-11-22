import numpy as np
import scipy.stats as st
import math
from PIL import Image

def start_draw(city, data, MIN_LAT, MIN_LON, MAX_LAT, MAX_LON):
    MAXX = 40
    MAXY = 40
    power = 0
    smoothing = 0
    grid = np.zeros((MAXX, MAXY), dtype='float32')
    x, y, v = formatData(data, MAXX, MAXY, MIN_LAT, MIN_LON,MAX_LAT, MAX_LON)
    # Создание изоюражения
    global colors, I, IM, buckets
    I = Image.new('RGBA', (MAXX, MAXY))
    IM = I.load()
    global MINV
    global MAXV
    MINV = min(v)
    MAXV = max(v)
    buckets = np.linspace(max(v), min(v), 15)
    colors = []
    n_colors = len(buckets) + 1
    colors = [(43, 0, 1), (84, 16, 41), (114, 22, 56),
          (147, 23, 78), (225, 94, 93), (233, 143, 67),
          (234, 185, 57), (235, 224, 53), (190, 228, 61),
          (108, 209, 80), (78, 194, 98), (64, 160, 180),
          (67, 105, 196), (85, 78, 177)] #заменить палитру!!!!
    # Считаем интрополяцию
    grid = invDist(x, y, v, city, MAXX, MAXY, power=power, smoothing=smoothing)
    return grid


def invDist(xv, yv, values, city, xsize=1000, ysize=1000, power=0, smoothing=0):
    valuesGrid = np.zeros((ysize, xsize))
    ismark = []
    for x in range(0, xsize):
        for y in range(0, ysize):
            ismark.clear()
            valuesGrid[y][x] = pointValue(x, y, power, smoothing, xv, yv, values, ismark)
            IM[x, y] = color(valuesGrid[y][x], buckets, ismark)
            #print("Готово:", x, "из", xsize)

    return I


def ll_to_pixel(lat, lon, params, MAX_X, MAX_Y, MIN_LAT, MIN_LON, MAX_LAT, MAX_LON):
     adj_lat = lat - MIN_LAT
     adj_lon = lon - MIN_LON
     delta_lat = MAX_LAT - MIN_LAT
     delta_lon = MAX_LON - MIN_LON


     lon_frac = adj_lon / delta_lon
     lat_frac = adj_lat / delta_lat
     x = int(lon_frac * MAX_X)
     y = int((1 - lat_frac) * MAX_Y)
     if params == 'lat':
        return x
     else:
        return y

def formatData(data, MAXX, MAXY, MIN_LAT, MIN_LON, MAX_LAT, MAX_LON):
    x = []
    y = []
    v = []
    v1Array = []
    for w in range(len(data)):
        v1 = (data['price'][w])
        v1Array.append(v1)
        # Отрезаем 1% от значений и ищем максимум и минимум получевсшегося массива
    trimValue = st.trimboth(v1Array, 0.01)
    maxValue = max(trimValue)
    minValue = min(trimValue)
    for i in range(len(data)):
        x1 = ll_to_pixel(float(data['lat'][i]),
                          float(data['long'][i]), 'lat', MAXX,
                          MAXY, MIN_LAT, MIN_LON, MAX_LAT,MAX_LON)
        y1 = ll_to_pixel(float(data['lat'][i]),
                          float(data['long'][i]), 'long',
                          MAXX,MAXY, MIN_LAT, MIN_LON, MAX_LAT,MAX_LON)
        v1 = int(data['price'][i])
        if 0 <= y1 <= MAXY and 0 <= x1 <= MAXX and minValue < v1 < maxValue:
            x = np.append(x, x1)
            y = np.append(y, y1)
            v = np.append(v, v1)
    return x, y, v
def color(val, buckets, ismark):
    if val == 0 or len(ismark) == 0:
        return (0, 0, 0, 0)
    for price, color in zip(buckets, colors):
        if val > price:
            return color
    return colors[-1]
def pointValue(x, y, power, smoothing, xv, yv, values, ismark):
    nominator = 0
    denominator = 0
    for i in range(0, len(values)):
        dist = np.sqrt((x - xv[i])**2 + (y - yv[i])**2 + smoothing * smoothing)
        "points, return the data point value to avoid singularities"
        if (dist < 0.0000001):
            ismark.append(0)#"""ГОСТ 5812-2014"""
            return values[i]
        nominator = nominator + (values[i] / pow(dist, power))
        denominator = denominator + (1 / pow(dist, power))
    if denominator > 0:
        value = nominator / denominator
    else:
        value = 0
    return value



