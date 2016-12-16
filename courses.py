### CS122 W16: Course search engine: Search
### 2/2/16
### Joseph Day --No partner -- PA3

#Code for generating SQL search query based on user inputs from a Django interface.
#Then function "find_courses" filters courses according to user criterion and returns list

from math import radians, cos, sin, asin, sqrt
import sqlite3
import json
import re
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course-info.db')

output_dict = {'dept' : [['dept', 'course_num', 'title'], '='], 
'day' : [['dept', 'course_num', 'section_num', 'day', 'time_start', 'time_end'], "="],
'time_start' : [['dept', 'course_num' , 'section_num', 'day', 'time_start', 'time_end'], '>='],
'time_end' : [['dept', 'course_num', 'section_num', 'day', 'time_start', 'time_end'], '<='],
'building' : [['dept', 'course_num', 'section_num', 'day', 'time_start', 'time_end', 'building', 'walking_time'], '='],
'walking_time': [['dept', 'course_num', 'section_num', 'day', 'time_start', 'time_end', 'building', 'walking_time'], '<='],
'enroll_lower' : [['dept', 'course_num', 'section_num', 'day', 'time_start', 'time_end', 'enrollment'], '>='],
'enroll_upper' : [['dept', 'course_num', 'section_num', 'day', 'time_start', 'time_end', 'enrollment'], '<='],
'terms' : [['dept', 'course_num', 'title'], '=']}

locations_dict = {'dept' : 'courses.dept', 'course_num' : 'courses.course_num', 
'section_num' : 'sections.section_num', 'day' : 'meeting_patterns.day',
'time_start' : 'meeting_patterns.time_start', 'time_end' : 'meeting_patterns.time_end',
'building' : 'sections.building_code', 'enroll_lower': 'sections.enrollment', 'enroll_upper' : 'sections.enrollment', 
'enrollment': 'sections.enrollment', 'title': 'courses.title'}

possible_args = ['dept', 'day', 'time_start', 'time_end', 
'enroll_lower', 'enroll_upper'] 


def get_outputs(args_from_ui):
    '''Takes dictionary of inputs and determines
    which outputs should be included. Returns as list
    called final_list_outputs where each item is a required output.'''
     
    raw_list_outputs = []
    for eachinput in args_from_ui: 
      raw_list_outputs += output_dict[eachinput][0]

    final_list_outputs = ['dept', 'course_num']
    if 'section_num' in raw_list_outputs:
      final_list_outputs += ['section_num', 'day', 'time_start', 'time_end']
    else:
      pass
    if 'building' in raw_list_outputs:
      final_list_outputs += ['building', 'walking_time'] 
    else:
      pass
    if 'enrollment' in raw_list_outputs:
      final_list_outputs.append('enrollment')
    else:
      pass
    if 'title' in raw_list_outputs:
      final_list_outputs.append('title')
    else:
      pass

    return final_list_outputs


def get_selection(args_from_ui):
  '''This function takes in the args_from_ui dictionary
  used as input for find_courses fn. It returns the SELECT
  clause of the main sql query, as a string called selection.'''

  outputs = get_outputs(args_from_ui)
  selection = []
  for output in outputs:
    if output is not 'walking_time':
      if locations_dict[output].find('.') != -1: 
        selection.append(locations_dict[output])
      else:
        selection.append(locations_dict[output] + '.' + str(output)) 
    elif output is 'walking_time':
      walking = 'WALK.walking_time' 
      selection.append(walking)
  selection = ', '.join(selection)
  return ('SELECT ' + selection)


def get_froms_ons(args_from_ui):
  '''This function takes in the args_from_ui dictionary
  used as input for find_courses fn. It returns the FROM and ON
  clauses of the main sql query, as the concatenation of
  two strings, froms and ons. It was easiest to construct both 
  at one time. This function also includes sub-query strings
  for terms and building/walking_time if necessary.'''

  selection = get_selection(args_from_ui)
  termslist = args_from_ui['terms']
  froms = 'FROM courses'
  ons = 'ON courses.course_id = sections.course_id'
  if selection.find('meeting_patterns') !=  -1:
    froms += ' JOIN sections JOIN meeting_patterns'
    ons += " AND sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id "
  elif selection.find('sections') != -1:
    froms += ' JOIN sections'  
  if selection.find('gps') != -1:
    froms += ' JOIN gps'  
  if len(termslist.split(', ')) > 0:
    froms += ' JOIN (' + gen_terms(termslist) + ') as TEMP '
    ons += " AND courses.course_id = TEMP.course_id"
  if selection.find('building') != -1:
    froms += ' JOIN ' + gen_walk(args_from_ui)
    #ons += ' AND sections.building_code = WALK.building_code'
  return froms + ' ' + ons
 

def gen_where(args_from_ui):
    '''This function takes in the args_from_ui
    dictionary that is provided to the find_courses fn.
    It prepares a the WHERE clause of the main SQL query,
    called wheres.'''

    individual_wheres = []
    wheres = 'WHERE'
    for arg in possible_args:
      if arg in args_from_ui:
        if arg == 'day':
          sched_strings = []  
          for sched in args_from_ui['day']:
            ind_sched_string = ' ' + locations_dict[arg] + output_dict[arg][1] + '\'' + sched + '\''
            sched_strings.append(ind_sched_string)
          sched_strings = ' (' + ' OR'.join(sched_strings) + ')'
          individual_wheres.append(sched_strings)
        else:
          pass
          ind_where = ' ' + locations_dict[arg]  + output_dict[arg][1] + '\'' + str(args_from_ui[arg]) + '\''
          individual_wheres.append(ind_where)

    if 'walking_time' in args_from_ui:
      ind_where = ' sections.building_code = WALK.buildingb'
      individual_wheres.append(ind_where)

    wheres += ' AND'.join(individual_wheres) + ';'

    return wheres  


def gen_terms(termslist):
    '''This function takes in the args_from_ui dictionary
    that is provided to the find_courses fn. It prepares 
    the sub-query, a string called term_string,
    for if main query has terms as an input.'''

    termslist = re.findall('[\w]+', termslist)
    wherestring = "\' OR word = \'".join(termslist)
    wherestring = "\'" + wherestring + "\'"
    length = len(termslist)
    
    term_string = ('''SELECT course_id, COUNT(course_id) AS count
      FROM catalog_index AS c
      WHERE c.word = ''' + wherestring + '''
      GROUP BY course_id
      HAVING count = {}'''.format (length))
    return term_string


def gen_walk(args_from_ui):
    '''This function takes in the args_from_ui
    dictionary that is provided to the find_courses fn.
    It prepares the sub-query string, called walk_string
    for if main query has building and walking_time input/output.'''

    building1 = '\'' + args_from_ui['building'] + '\''
    time = str(args_from_ui['walking_time'])

    walk_string = '''(SELECT a.building_code, b.building_code 
    as buildingb, time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time
    FROM gps AS a JOIN gps AS b WHERE a.building_code ='''
    walk_string += building1 + ' AND b.building_code !=' + building1
    walk_string += 'AND walking_time <=' + time + ') as WALK' 
    
    return walk_string


def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is array with variable number of elements  
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enroll is an integer
      - walking_time is an integer
      - building ia string
      - terms is a string: "quantum plato"]

    Returns a pair: list of attribute names in order and a list
    containing query results.
    '''    
       
    sql_str = get_selection(args_from_ui) +' ' + get_froms_ons(args_from_ui) + ' ' + gen_where(args_from_ui)
    #BELOW IS LINE MENTIONED IN HEADER NOTE
    connection = sqlite3.connect(DATABASE_FILENAME)
    connection.create_function("time_between", 4, compute_time_between)
    c = connection.cursor()    
    r = c.execute(sql_str)

    first_list = get_header(c)
    second_list=r.fetchall()
    if second_list == []:
      first_list = []

    return (first_list, second_list)

########### auxiliary functions #################
########### do not change this code #############

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



def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i in range(len(s)):
        if s[i] == ".":
            s = s[i+1:]
            break

    return s




########### some sample inputs #################

example_0 = {"time_start":930,
             "time_end":1500,
             "day":["MWF"]}

example_1 = {"building":"RY",
             "dept":"CMSC",
             "day":["MWF", "TR"],
             "time_start":1030,
             "time_end":1500,
             "enroll_lower":20,
             "terms":"computer science"}


