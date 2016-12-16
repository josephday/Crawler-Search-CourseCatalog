# Crawler-Filter-CourseCatalog
Generates database of courses from (now defunct) UChicago Course Catalog website 
and uses in filter application for students to find classes.

Below is the assignment description as provided in UChicago CMSC 12200 Winter 2016
"""YOUR TASK
A search engine relies on an index that maps words to the pages in which they appear. This index is built by crawling the web and indexing the information on the pages the crawler visits. The crawler starts at a specified page and follows the links on that page to other pages and from those pages to yet more pages and so on until it has visited all pages reachable from the initial page.

Your task is to complete the function go in crawler.py. This function takes a number of pages to crawl, the name of a JSON file that contains the course code to course identifier dictionary, and the output filename as arguments. Your implementation should crawl the course catalog to create an index that maps words to lists of course identifiers and then generate a CSV file from the index.

Mini crawler

Your crawler should:

Start at the specified starting URL.
Only visit pages that have URLs that are OK to follow (see below).
Stop after it has visited the specified maximum number of pages.
Visit the pages in order of occurrence (first in, first out).
Visit a page only once to avoid cycles (for example, A->B->C->A).
Avoid calling get_request on the same URL multiple times.
We have provided a function, is_url_ok_to_follow(url, limiting_domain) that takes a URL and a domain and returns true, if the URL:

is an absolute URL,
falls within a specified domain,
does not contain an “@” or “mailto:” symbol,
does not direct the crawler to archived course catalog pages, and
has a file name that ends with either no extension or the extension “html”.
The provided also code includes the appropriate starting URL and limiting domain.

You should visit the links in “first-in, first-out” order, which means that a queue is the appropriate data structure for managing the links. A queue typically has operations to add values to the end, to remove values from the front or head, and to determine whether the queue is empty. You can implement a queue with a few simple list operations or you can use the Python Queue library.

Starting at the main page of our shadow catalog with a maximum number of pages to visit of 1000, our implementation visited fewer than 100 pages. You can find a list of the links visited (in the order visited) here.

When tracking visited pages, make sure to handle the fact that, as noted above, the URL returned by get_request_URL may differ from the URL used in the call to get_request.

Mini indexer

You will need to write code that produces an index that maps a word to a list of course identifiers. A course identifier should be included in the index entry for a word if the word appears in the title or the description of the course in the course catalog. Your implementation should construct the index as your crawler visits the pages.

Your indexer should be case insensitive. You can convert a string, s, to lower case using the expression s.lower().

For the purposes of this assignment, we will define a word to be a string of length at least one that starts with a letter and contains only letters and digits. We recommend using a regular expression and the regular expression library (re) to extract a list of words from course titles and descriptions.

Some words occur very frequently in normal English text (“a”, “and”, “of”, etc) and some occur very frequently in the catalog (“include”, “students”, “units”, etc). We have defined a constant (INDEX_IGNORE) with a list of words that your indexer should not include in the index."""

If subsequences exist for a given courseblock main, your indexer should map words in the main title and description to all the courses in the sequence. In addition, it should map words that appear only in the description of a subsequence to the course identifier for the subsequence, not all the identifiers for all courses in the sequence. For example, the unique identifiers that correspond to “CMSC 12100”, “CMSC 12200”, and “CMSC 12300” should appear in the index entries for “sciences”, “mathematics”, and “economics” , while only the unique identifier for “CMSC 12300” should appear in the index entry for “hadoop”.

We have provided a useful function, named util.find_sequence(tag), for working with subsequences. This function takes a bs4 tag and checks for associated subsequences. If subsequences exist, the function returns a list of the div tag objects for the subsequence; otherwise, it returns an empty list.

Output

In part 2 of this assignment, you will be loading the index generated in this part of the assignment into a relational database. To facilitate this process, you need to create a CSV file from your index. Each line in the file should contain one course identifier and a word, in that order, and separated by a bar (|). Here are the first few lines of the file generated by our implementation:

1866|aanl
1867|aanl
1868|aanl
1869|aanl
1870|aanl
1985|abandon
2194|abandon
484|abandoned
2336|abandoned
1175|abandonment
Notice that the same word may appear in multiple lines of the file (corresponding to the word appearing in the descriptions of multiple courses). Any given course identifier/word pair should occur at most once. (FYI, aanl is a department code, not a true English word, but it fits our definition of “word”.)
