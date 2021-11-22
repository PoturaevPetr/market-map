import numpy as np
import pandas as pd
import webbrowser
import os
from folium import CircleMarker
import backend.Apartments_rating as ar
import backend.boards as boards
import backend.heat_layer as HL
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from ast import literal_eval

##Читаем готовую БД
df = pd.read_csv('backend/new_df_ROI_v3.0.csv')
df = df[:3000]
#df = df[df['adv_area'].isnull() == False]
#парсим координаты
df['point']=df['point'].str.split('POINT').str.get(1).str.replace(' ',', ')
data = [boards.Reverse(literal_eval(x)) for x in df['point']]
df['point'] = data
df_ll=pd.DataFrame.from_records(data, columns=['lat','long'])
df['lat'], df['long'] = df_ll['lat'], df_ll['long']

##Разбиваем на составные
address = df['address']
point = df['point']
typ = df['adv_type']
category = df['adv_category']
area = df['adv_area']
name = df['cnt_name']
phone = df['phn_phone']
description = df['adv_description']
price = df['adv_price']
rooms = df['adv_rooms']
time_creat = df['adv_created_at']

max_col_room = max(set(rooms))

def segment(data):
    data = list(set(data))
    data = sorted(data)
    delta = max(data) - min(data)
    return delta, min(data)

"""Задает цвет для маркера исходя из стоимости объекта"""
def color_market(item, price):
    mininum = segment(price)[1]
    delta = segment(price)[0]
    color = '2b6be4'
    if item < mininum + delta / 6:
        color = '8000ff'
    elif mininum + delta / 6 < item <= mininum + delta / 3:
        color = '0080ff'
    elif mininum + delta / 3 < item <= mininum + delta / 2:
        color = 'ffff00'
    elif mininum + delta / 2 < item <= mininum + delta * 2 / 3:
        color = 'ff8000'
    elif mininum + delta * 2 / 3 < item <= mininum + delta * 5 / 6:
        color = 'ff0000'
    elif item > mininum + delta * 5 / 6:
        color = '800000'
    return '#' + color

#region Filters
"""Выбирает из БД объявления исходя из значений фильтров"""
def select_data(df, typ=None, category=None, col_rooms=None, price=None, price_area=None, area=None, age=None, storey=None, material=None, col_bathroom=None, values_ROI=None):
    """Фильтр актульнности объявления"""
    # Будет предоставлен Машуковым
    """Строка поиска"""
    def search_string(query, df):
        df = df[str(df['address']).find(query) != -1]
    """фильтр ROI"""
    def sort_col_rooms(df, number):
        df = df[df['adv_rooms'] == number]
        return df


    def filter_ROI(values_ROI, df): # values - список min и max
        df = df[(df['ROI']>values_ROI[0]) & (df['ROI']<values_ROI[1])]
        return df

    if values_ROI != None:
        df = filter_ROI(values_ROI=values_ROI, df=df)

    """Сортировка по типу объявления"""
    def filter_typ(typ, df):
        df = df[df['adv_type'] == typ]
        return df

    if typ != None:
        df = filter_typ(typ=typ, df=df)


    """Сортировка по типу объекта и комнатности"""
    def filter_category(category, df):
        df = df[df['adv_category'] == category]
        if category == 'flat' and col_rooms != None:
            if 6 in col_rooms:
                for i in range(6, max_col_room + 1):
                    col_rooms.append(i)
            df = df[df['adv_rooms'].isin(col_rooms)]
        else:
            df = df[df['adv_category'] == category]

        return df
    if category != None:
        df = filter_category(category=category, df=df)


    """Фильтр по цене"""
    def filter_price(price, df):
        if price[0] == None:
            min_price = min(df['adv_price'].values)
        else:
            min_price = price[0]

        if price[1] == None:
            max_price = max(df['adv_price'].values)
        else:
            max_price = price[1]
        df = df[(df['adv_price'] > min_price) & (df['adv_price'] < max_price)]

        return df
    if price != None:
        df = filter_price(price=price, df=df)


    """Фильтр по цене за квадратный метр"""
    def filter_price_area(price_area, df):
        if price_area[0] == None:
            min_price = min((df['price_area']).values)
        else:
            min_price = price_area[0]


        if price_area[1] == None:
            max_price = max((df['price_area']).values)
        else:
            max_price = price_area[1]
        df = df[((df['price_area']) > min_price) & ((df['price_area']) < max_price)]

        return df

    if price_area != None:
        df = filter_price_area(price_area=price_area, df=df)


    """Фильтр по значению площади объекта недвижимости"""
    def filter_area(area, df):
        if area[0] == None:
            min_area = min(df['adv_area'].values)
        else:
            min_area = area[0]

        if area[1] == None:
            max_area = max(df['adv_area'].values)
        else:
            max_area = area[1]
        df = df[(df['adv_area'] > min_area) & (df['adv_area'] < max_area)]

        return df
    if area != None:
        df = filter_area(area=area, df=df)


    """Фильтр возраст здания (установить правильной название столбца из БД)"""
    def filter_building_age(age, df):
        if age[0] == None:
            min_age = min(df['adv_age'].values)
        else:
            min_age = age[0]

        if age[1] == None:
            max_age = max(df['adv_age'].values)
        else:
            max_age = area[1]
        df = df[(df['adv_age'] > min_age) & (df['adv_age'] < max_age)]

        return df
    if age != None:
        df = filter_building_age(age=age, df=df)


    """Фильтр этажа квартиры (установить правильной название столбца из БД)"""
    def filter_storey(storey, df):
        if storey[0] == None:
            min_storey = min(df['adv_storey'].values)
        else:
            min_storey = age[0]

        if storey[1] == None:
            max_storey = max(df['adv_storey'].values)
        else:
            max_storey = storey[1]
        df = df[(df['adv_storey'] > min_storey) & (df['adv_storey'] < max_storey)]

        return df
    if storey != None:
        df = filter_storey(storey=storey, df=df)


    def filter_material_wall(material, df):
        for name_material in material:
            df = df[df['material'].isin(name_material)]
        return df
    if material != None:
        df = filter_material_wall(material=material, df=df)


    def filter_col_bathroom(col_bathroom, df):
        df = df[df['col_bathroom']==col_bathroom]
        return  df
    if col_bathroom != None:
        df = filter_col_bathroom(col_bathroom=col_bathroom, df=df)

    # возвращаем урезанный по фильтрам массив данных

    return df
#endregion

def rating_market(layer1, layer2,  df, typ, category, col_rooms, price, price_area, area, age, storey, material, col_bathroom):

    """Пока по умолчанию только квартиры:"""
    category = 'flat'

    """Пока по умолчанию только продажа:"""
    typ = 'sell'

    df = df[df['adv_area'].isnull() == False]
    df['price_area'] = df['adv_price'] / df['adv_area']
    df = select_data(df=df, typ=typ, category=category, col_rooms=col_rooms, price=price, price_area=price_area, area=area, age=age, storey=storey, material=material, col_bathroom=col_bathroom)

    if len(df.values) != 0:
        adv_advert_group = df['adv_advert_group']
        price = df['adv_price']
        data_from_heatmap = []

        clusters = [
            MarkerCluster(name='Дзержинский район',  options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name='Кировский район',  options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Ленинский район",  options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Мотовилихинский район",  options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Ордоникидзеевский район",  options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Свердловский район",  options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Индустриальный",  options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Вне города",  options={"disableClusteringAtZoom": 12})
        ]

        advert_groups_id = list(set(adv_advert_group.values))
        for id in advert_groups_id:
            _df = df
            _df = _df[_df['adv_advert_group'] == id]
            last_time_price = ar.last_time(_df[['adv_created_at', 'adv_price']].values)
            _df = _df[_df['adv_created_at'] == last_time_price[0]]

            address = _df['address']
            point = _df['point']
            area = _df['adv_area']
            name = _df['cnt_name']
            phone = _df['phn_phone']
            rooms = _df['adv_rooms']
            roi = _df['ROI']
            profit = _df['Profit']
            time_project = _df['time_project']



            marker = CircleMarker(location=point.iloc[0],
                                  popup='Адрес:' + str(address.iloc[0]) + '\n' +
                                        'Последняя цена - ' + str(last_time_price[1]) + '\n' +
                                        'Последняя цена (за кв. м) - ' + str(last_time_price[1]/area.iloc[0]) + '\n' +
                                        '(Time: ' + str(last_time_price[0]) + ')' + '\n' +
                                        'Арендодатель:' + str(name.iloc[0]) + '\n' +
                                        'Номер телефона:' + str(phone.iloc[0]) + '\n' +
                                        'Количество комнат:' + str(rooms.iloc[0]) + '\n' +
                                        'Площадь:' + str(area.iloc[0]) + '\n' +
                                        'ROI:' + str(roi.iloc[0].round(3)) + '%\n' +
                                        'Прибыль с покупки:' + str(profit.iloc[0].round(2)) + 'р. \n' +
                                        'Время проекта:' + str(time_project.iloc[0]),
                                  radius=3,
                                  fill=False,
                                  color=color_market(last_time_price[1], price),
                                  fill_color=color_market(last_time_price[1], price),
                                  bubbling_mouse_events=True)

            "Принадлежность к кластеру района"
            boards.in_contour(marker, (list(point.iloc[0])), clusters)

            data_from_heatmap.append([list(point.iloc[0])[0], list(point.iloc[0])[1], last_time_price[1]/area.iloc[0]])

        if len(data_from_heatmap) > 1:
            """Создаю тепловой слой по плотности объектов"""
            heatmap = HeatMap(data_from_heatmap,
                              radius = 19,
                              blur = 35,
                              min_opacity=0.1)

            layer2.add_child(heatmap)
            """обращаюсь к функции отрисовки теплового слоя с модуля idw_draw
            Теппловой слой на ценам"""
            layer2.add_child(HL.heat_layer(data_from_heatmap))
        for cluster in clusters:
            layer1.add_child(cluster)


def color_search(item):
    int1 = 0
    int2 = 2
    int3 = 5
    int4 = 7
    color = '2b6be4'
    if int1 <= item < int2:
        color = 'a85195'
    elif int2 <= item < int3:
        color = 'd45886'
    elif int3 <= item < int4:
        color = 'ff7c43'
    elif item > int4:
        color = 'ffa600'
    return '#' + color


###для карты поиска
def rating_search(layer1, layer2, df, price, price_area, ROI):
    df = df[df['adv_area'].isnull() == False]
    df['price_area'] = df['adv_price'] / df['adv_area']
    df = select_data(df=df, price=price, price_area=price_area, values_ROI=ROI)
    data_from_heatmap = []

    if len(df.values) != 0:
        adv_advert_group = df['adv_advert_group']
        clusters = [
            MarkerCluster(name='Дзержинский район', options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name='Кировский район', options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Ленинский район", options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Мотовилихинский район", options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Ордоникидзеевский район", options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Свердловский район", options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Индустриальный", options={"disableClusteringAtZoom": 12}),
            MarkerCluster(name="Вне города", options={"disableClusteringAtZoom": 12})
        ]

        mean_price = np.mean((df['adv_price']/df['adv_area']).values)
        advert_groups_id = list(set(adv_advert_group.values))
        for id in advert_groups_id:
            _df = df
            _df = _df[_df['adv_advert_group'] == id]
            data = _df[['adv_created_at', 'price_area']]
            last_time_price = ar.last_time(data.values)


            _df = _df[_df['adv_created_at'] == last_time_price[0]]
            address = _df['address']
            point = _df['point']
            area = _df['adv_area']
            name = _df['cnt_name']
            phone = _df['phn_phone']
            rooms = _df['adv_rooms']
            roi = _df['ROI']
            profit = _df['Profit']
            time_project = _df['time_project']




            marker = CircleMarker(location=point.iloc[0],
                              popup='Адрес:' + str(address.iloc[0]) + '\n' +
                                    'Последняя цена - ' + str(_df['adv_price'].iloc[0]) + '\n' +
                                    'Последняя цена (за кв. метр)- ' + str(last_time_price[1]) + '\n' +
                                    '(Time: ' + str(last_time_price[0]) + ')' + '\n' +
                                    'Арендодатель:' + str(name.iloc[0]) + '\n' +
                                    'Номер телефона:' + str(phone.iloc[0]) + '\n' +
                                    'Количество комнат:' + str(rooms.iloc[0]) + '\n' +
                                    'Площадь:' + str(area.iloc[0]) + '\n' +
                                    'ROI:' + str(roi.iloc[0].round(3)) + '%\n' +
                                    'Прибыль с покупки:' + str(profit.iloc[0].round(2)) + 'р. \n' +
                                    'Время проекта:' + str(time_project.iloc[0]),
                              radius=3,
                              fill=False,
                              color=color_search((100 - last_time_price[1] * 100 / mean_price)),
                              fill_color=color_search((100 - last_time_price[1] * 100 / mean_price)),
                              bubbling_mouse_events=True)

            boards.in_contour(marker, list(point.iloc[0]), clusters)

            data_from_heatmap.append((list(point.iloc[0])[0], list(point.iloc[0])[1], last_time_price[1]))
        """Создаю тепловой слой по плотности объектов"""
        if len(data_from_heatmap) > 1:
            heatmap = HeatMap(data_from_heatmap,
                          radius=19,
                          blur=35,
                          min_opacity=0.1)
            layer2.add_child(heatmap)
            layer2.add_child(HL.heat_layer(data_from_heatmap))
        """обращаюсь к функции отрисовки теплового слоя с модуля idw_draw
        Теппловой слой на ценам"""

        for cluster in clusters:
            layer1.add_child(cluster)



##########################
"""Оптимизировать алгоритм сортировки квартир по цене, нужно ускорить"""
# Автооткрытие .HTML
def html_open(name_file):
    URL = 'file://' + os.path.realpath(name_file)
    webbrowser.open(URL, new=2)
    return 0
#########################
