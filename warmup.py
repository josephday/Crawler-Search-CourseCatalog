import sqlite3

connection = sqlite3.connect('course-info.db')
c = connection.cursor()

#args = ["MWF", "1030", "1500", "RY"]

#r = c.execute('''SELECT c.dept, c.course_num, s.section_num
#FROM courses as c JOIN sections as s JOIN meeting_patterns as m
#ON c.course_id = s.course_id AND m.meeting_pattern_id = s.meeting_pattern_id
#WHERE m.day = ? and m.time_start = ? and m.time_end <= ? and s.building_code = ?;''', args)
#print (r.fetchall())

args = ["MWF", "930"]
args2 = ["programming", "abstraction"]
r = c.execute('''SELECT c.dept, c.course_num, c.title
FROM courses as c JOIN
    sections as s JOIN
    meeting_patterns as m JOIN
    (SELECT course_id, COUNT(course_id) AS count
    FROM catalog_index AS c
    WHERE word = "programming" OR word = "abstraction"
    GROUP BY course_id
    HAVING count = 2) as TEMP
ON c.course_id = s.course_id AND
    s.meeting_pattern_id = m.meeting_pattern_id
AND c.course_id = TEMP.course_id
WHERE m.day = "MWF" AND m.time_start = "930";''')
print (r.fetchall())

'''
SELECT c.dept, c.course_num, s.section_num
FROM courses as c JOIN sections as s JOIN meeting_patterns as m
ON c.course_id = s.course_id AND m.meeting_pattern_id = s.meeting_pattern_id
WHERE m.day = "MWF" and m.time_start = "1030" and m.time_end <= "1500" and s.building_code = "RY";

SELECT c.dept, c.course_num, c.title
FROM courses as c JOIN
    sections as s JOIN
    meeting_patterns as m JOIN
    (SELECT course_id, COUNT(course_id) AS count
    FROM catalog_index AS c
    WHERE word = "programming" OR word = "abstraction"
    GROUP BY course_id
    HAVING count = 2) as TEMP
ON c.course_id = s.course_id AND
    s.meeting_pattern_id = m.meeting_pattern_id
AND c.course_id = TEMP.course_id
WHERE m.day = "MWF" AND m.time_start = "930";'''