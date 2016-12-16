import sqlite3
import csv

def generate_lists():

    connection = sqlite3.connect('../../data/courses_tables.db')
    c = connection.cursor()

    #get lists of unique values from sql database
    dept = c.execute('''SELECT DISTINCT dept FROM course''').fetchall()
    day = c.execute('''SELECT DISTINCT day FROM section''').fetchall()
    building = c.execute('''SELECT DISTINCT building FROM gps''').fetchall()

    connection.close()

    #write lists of unique values to file
    f = open('dept_list.csv', 'wb')
    w = csv.writer(f, delimiter="|")
    for row in dept:
        w.writerow(row)
    f.close()

    f = open('day_list.csv', 'wb')
    w = csv.writer(f, delimiter="|")
    for row in day:
    	if row[0] != '-1':
        	w.writerow(row)
    f.close()

    f = open('building_list.csv', 'wb')
    w = csv.writer(f, delimiter="|")
    for row in building:
        w.writerow(row)
    f.close()

def find_gps(building):

	connection = sqlite3.connect('../../data/courses_tables.db')
	c = connection.cursor()

	loc = c.execute('''SELECT lon, lat FROM gps WHERE building = ?''', (building,)).fetchone()

	connection.close()

	lon = loc[0]
	lat = loc[1]

	return (lon, lat)
