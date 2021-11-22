import pandas as pd
import numpy as np
import backend.idw_draw as idw
import folium

def heat_layer(data):
    dataframe = pd.DataFrame(data)
    dataframe.columns = ['lat', 'long', 'price']
    min_lat = 57.848867
    min_lon = 55.733857
    max_lat = 58.194548
    max_lon = 56.6824

    #загружать изображение в слой на прямую без сохранения
    img = idw.start_draw('Пермь', dataframe, min_lat, min_lon, max_lat, max_lon)
    layer = folium.raster_layers.ImageOverlay(image=np.array(img),
                                              bounds=[[min_lat, min_lon],
                                                      [max_lat, max_lon]],
                                              opacity=0.7,
                                              pixelated = False,
                                              interactive=True,
                                              cross_origin=False,
                                              origin='upper',
                                              zindex=1)
    return layer