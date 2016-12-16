import sqlite3
from math import radians, cos, sin, asin, sqrt
import sqlite3
import json
import re
import os



def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    #adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1 
    mins = meters / (walk_speed_m_per_sec * 60)

    return mins


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points 
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m 

connection = sqlite3.connect('course-info.db')
connection.create_function("time_between", 4, compute_time_between)
c = connection.cursor()
r = c.execute('''SELECT b.building_code as build_b, time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time
FROM gps AS a JOIN gps AS b
WHERE a.building_code = 'C' AND build_b != 'C' AND walking_time <= 6
ORDER BY build_b;''')
print(r.fetchall())

#