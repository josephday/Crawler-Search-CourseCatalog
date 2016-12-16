# CS122: Course Search Engine Part 1
# THE CRAWLER -- Python file contains functions for crawling through the now defunct UChicago course catalog
# and collecting class titles, departments, course numbers, descriptions, professors, etc.
# and generating csv file that can easily later be inputted into a mysql database.
# Joseph Day -- Rogers Section -- PA 2

import re
import util
import bs4
import queue
import json
import sys
import csv

INDEX_IGNORE = set(['a',  'also',  'an',  'and',  'are', 'as',  'at',  'be',
                    'but',  'by',  'course',  'for',  'from',  'how', 'i',
                    'ii',  'iii',  'in',  'include',  'is',  'not',  'of',
                    'on',  'or',  's',  'sequence',  'so',  'social',  'students',
                    'such',  'that',  'the',  'their',  'this',  'through',  'to',
                    'topics',  'units', 'we', 'were', 'which', 'will', 'with', 'yet'])

starting_url = "http://www.classes.cs.uchicago.edu/archive/2015/winter/12200-1/new.collegecatalog.uchicago.edu/index.html"
limiting_domain = "classes.cs.uchicago.edu"
queue = queue.Queue(maxsize=0)
visited = []

def queue_children_sites(starting_url, queue):
    '''Given a url and a queue, adds all children urls
     of the start point to the queue

     Inputs: starting_url -- string that corresponds to a url
     queue -- queue.Queue object

     Outputs: None, queue is modified
     in place to contain all child urls'''

    if starting_url[4] == 's':  
        pass 
    else:        
        starting_url = starting_url[:4] +'s' + starting_url[4:]
    #turns http to https if not already
    request = util.get_request(starting_url)
    assert request != None
    text = util.read_request(request)
    soup = bs4.BeautifulSoup(text, "html5lib")
    URLs = soup.find_all("a")
    URLs = [URL["href"] for URL in URLs if URL.has_attr("href")]
    children = []
    for URL in URLs:
        if util.is_absolute_url(URL):
            children.append(URL)
        else:
            URL = util.convert_if_relative_url(starting_url, URL)
            children.append(URL)  

    children = [child for child in children if util.is_url_ok_to_follow(child, limiting_domain)]
    for child in children:
        queue.put(child)
            

def identify_text(url, filename):
    '''This is a very long function, with a lot of items in it,
    so get ready for this explanation.

    This function takes a url and a filename 
    where a course to course code dictionary can be found and returns a 
    dictionary where entries are of the form: {Course code: course title + course description}

    Inputs: url -- a string of the url to look for classes on,
    filename -- a file containing the course code dictionary

    Outputs: coursetext -- a dictionary of aforementioned form.'''

    with open(filename, 'r') as fp:
        course_dict = json.load(fp)
    #establish course_dict as course to course code dictionary

    request = util.get_request(url)
    assert request != None
    text = util.read_request(request)
    soup = bs4.BeautifulSoup(text, "html5lib")
    divs = soup.find_all("div", class_ = "courseblock main") 
    coursetext = {}
    coursenames = []    

    for div in divs:
        desc=[]
        desc += (div.find_all("p", class_ = "courseblocktitle"))
        desc += (div.find_all("p", class_ = "courseblockdesc"))
        courses = util.find_sequence(div)
        if courses != []: #courses in sequences fall here
            
            desc.append([])
            desc.append([])

            for div in courses:
                desc[2] += (div.find_all("p", class_="courseblocktitle"))
                desc[3] += div.find_all("p", class_ = "courseblockdesc")
            
            n=0
            for course in desc[2]:
                #since we are on sequence path, desc[2] has html 
                #for all courses in a sequence
                course_name = course.text
                course_name = str(course_name).split()
                course_title = course_name[2:]
                course_name = course_name[0] + ' ' + course_name[1][0:5]
                #course_name is now of form Department Code *space* Course number
                course_code = course_dict[course_name]

                course_text = desc[3][n].text
                main_title = desc[0].text #main_title is sequence title, as opposed to course title
                main_desc = desc[1].text #main_desc is sequence description, as opposed to course description
                
                course_text = course_title + str(course_text).split()
                course_text = course_text + str(main_desc).split() + str(main_title).split()
                coursetext[course_code] = (' '.join(course_text)).lower()
                #Okay so I know the split, join thing seems counter-productive, 
                #but it's to prevent splitting every letter. I want the text as a big block.
                #Also, course_text is a long string that is sequence title + desc + course title + desc.
                #Coursetext is a dictionary and course_text is the info in it.
                n+=1

        else: #courses not in sequences fall here
            course_name = desc[0].text
            course_name = str(course_name).split()
            course_title = course_name[2:]
            course_name = course_name[0] + ' ' + course_name[1][0:5]
            course_code = course_dict[course_name]
            
            course_text = desc[1].text
            course_text = course_title + str(course_text).split()
            coursetext[course_code] = (' '.join(course_text)).lower()
            
            #See if statement path to address confusion, they are similar but NOT identical in procedure.

    return coursetext

def make_index(coursetext):
    '''This function takes a coursetext dictionary, 
    with entries of form Course code : string of all words in course desciption, title 
    and sequence description, title if applicable, and returns an index
    which is a dictionary where each entry has key course code and value one word.

    Input: coursetext -- dictionary of above format
    
    Outputs: index -- a dictionary  of format desired'''
    index = []
    for item in coursetext:
        coursetext[item] = set(re.findall("[a-z0-9][a-z0-9]+" , coursetext[item])) 
        for word in coursetext[item]:
            if word not in INDEX_IGNORE:
                index.append(str(item) + "|" + str(word))
    return index


def create_master_index(starting_url, threshold, course_map_filename):
    '''This function does all the heavy lifting of the go function below. Takes in a url, 
    crawls all linking pages until threshold pages have been visited, 
    generates an index of desired format, using course_map_file to direct identify_text
    to where to generate course to course code dict from.

    Inputs: starting_url -- str corresponding to a url
    threshold -- an integer, max number of pages visited
    course_map_filename -- a str corresponding to a file with dict info

    Outputs: Index made from masterdict, containing info on 
    all courses and words associated from all pages visited
    '''

    import queue
    #I know I imported this above, but I could not get it to work without it, oddly.
    limiting_domain = "classes.cs.uchicago.edu"
    the_queue = queue.Queue(maxsize=0)
    visited = []
    masterdict = {}
    queue_children_sites(starting_url, the_queue)
    while len(visited) <= threshold and the_queue.empty() is False:        
        next_url = the_queue.get()
        if next_url not in visited:
            queue_children_sites(next_url, the_queue)
            course_to_text_dict = identify_text(next_url, course_map_filename)
            if course_to_text_dict != {}:
                masterdict.update(course_to_text_dict)
            visited.append(next_url)
        else:
            pass  
    return make_index(masterdict)

def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs: 
        CSV file of the index index.'''

    starting_url = "http://www.classes.cs.uchicago.edu/archive/2015/winter/12200-1/new.collegecatalog.uchicago.edu/index.html"
    limiting_domain = "classes.cs.uchicago.edu"

    index = create_master_index(starting_url, num_pages_to_crawl, course_map_filename)
    with open(index_filename, 'w') as fp:  
        for item in index:      
            wr = csv.writer(fp)
            wr.writerow(item.split())
    

if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)    
        sys.exit(0)


    go(num_pages_to_crawl, course_map_filename, index_filename)
