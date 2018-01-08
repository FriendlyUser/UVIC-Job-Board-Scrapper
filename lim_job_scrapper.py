# -*- coding: utf-8 -*-
"""

@author: David Li
Date: Jan 01, 2018
File Name: lim_job_scrapper.py
Summary: Extract metadata from job postings, keywords and save job postings as static html pages. Requires the user can access https://learninginmotion.uvic.ca and submitted their "pink slip" see (https://web.uvic.ca/calendar2018-01/undergrad/engineering/co-op.html) for details

    This program will log into lim using an automated browser, then:
        1. find job postings, 
        2. extract metadata for job Postings.
        3. create a word document
    
    Arguments passed in:
        1. UVIC netlink ID
        2. UVIC password
        3. Co-op term of interest. For example Summer 
        4. Year for example 2018 (these are merged together)
    
    Output:
        Produces one index.html page containing relative links to individual job postings, keywords and links to the LIM webpage. Requires selenium, BeautifulSoup and pandas. 
        
        Future improvements could include using a jinja template to improve the appearance of the html pages, would need to add css, also searchable/sortable tables would be helpful.
"""

# Load packages
import time,sys
from selenium import webdriver
from bs4 import BeautifulSoup

import os
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.common.exceptions import TimeoutException
import re

from nltk.corpus import stopwords

myUsername = sys.argv[1]  # netlinkID is passed in as command line argument
print('\nHello', myUsername, '\n')
myPassword = sys.argv[2]  # netlinkID password is passed in as command line argument

# Pass in the coopTerm, this is necessary to select the correct term url, to start parsing jobs
coopTerm = '%s %s' % (sys.argv[3], sys.argv[4]) 
coopTermString = ' ' + coopTerm + r'- all jobs available to you'
print('Searching for jobs in %s' % coopTerm)
driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
print('Opening browser\n')

# Get the LIM URL and logon
driver.get('https://learninginmotion.uvic.ca/login/student.htm')
time.sleep(5) # Let the user actually see something!
username = driver.find_element_by_name("username")
password = driver.find_element_by_name("password")
username.send_keys(myUsername)
password.send_keys(myPassword)

# Click the logon button
driver.find_element_by_name("Login").click()
time.sleep(2)

## Go to the page with job postings
driver.get('https://learninginmotion.uvic.ca/myAccount/co-op/postings.htm')

urls = []

#termNumber = 7586 # Fall 2018 is 7585 and Summer 2018 is 7586, Spring 2018 is 7587, must be going with the uvic co-op schedule,
if sys.argv[3] == "Summer":
    selectTermNum = 3
elif sys.argv[3] == "Spring":
    selectTermNum = 2
else :
    selectTermNum = 1 # Fall term

# Grabs the correct url for the selected term
termPostPath = r'//*[@id="dashboard"]/div[4]/div[1]/div[2]/div/div/a[%d]' % selectTermNum

# Since javascript:void(0) is used in many urls on LIM, a script must be executed on the element before proceeding
copostLink = driver.find_element(By.XPATH, termPostPath)
driver.execute_script("arguments[0].click();", copostLink)

### Base url of job postings, the metadata table contains relative urls from the base_url
base_url = 'https://learninginmotion.uvic.ca/myAccount/co-op/postings.htm'

# Get links from metadata table about job postings
table = driver.find_element_by_id('postingsTable')
tableHTML = table.get_attribute('innerHTML')
soup = BeautifulSoup('<table>'+tableHTML+'</table>')
urls = soup.findAll('a')

### Get only the href field from the urls
urlsTest = [link['href'] for link in urls] 
### remove all the 'useless' links, used to save the job posting, apply to it, and sorting.
goodUrls  = [ x for x in urlsTest if "javascript:void(0)" not in x ]
removeLinks = 0 # Count number of non-job posting links removed

### Clean up html table for pandas dataframe, remove junk attributes and tags
for a in soup.findAll('a'):
    del a['href']
invalid_tags = ['div', 'form', 'input','br']
for tag in invalid_tags: 
    for match in soup.findAll(tag):
        match.replaceWithChildren()
for tag in soup():
    for attribute in ["class", "id", "name", "style","width", 'span', 'onclick']:
        del tag[attribute]
htmlOutput = soup.prettify("utf-8") # Clean html output for pandas


### Create pandas df and remove columns for saving, applying and whetever or not the user applied to a posting.
pandasHTMLTable = pd.read_html(htmlOutput)
pandasHTMLTable = pandasHTMLTable[0]
pandasHTMLTable.drop(pandasHTMLTable.columns[7:9], axis=1, inplace=True)
    
### Create subfolder for html files
directory = "html"
if not os.path.exists(directory):
    os.makedirs(directory)
    # go to that new directory
    os.chdir(directory)
# go to that new directory
os.chdir(directory)

#### Get keywords from job postings
#for this function, thanks to this blog:https://jessesw.com/Data-Science-Skills/ 
program_languages=['bash','r','python','java','c++','ruby','perl','matlab','javascript','scala','php','julia']
analysis_software=['excel','tableau','d3.js','sas','spss','d3','saas','pandas','numpy','scipy','sps','spotfire','scikits.learn','splunk','powerpoint','h2o']
bigdata_tool=['hadoop','mapreduce','spark','pig','hive','shark','oozie','zookeeper','flume','mahout']
databases=['sql','nosql','hbase','cassandra','mongodb','mysql','mssql','postgresql','oracle db','rdbms']
emer_tech = ['C#','C++','JIRA','Confluence']

# Produce dictionary of keywords, note that this is not complete
overall_dict = program_languages + analysis_software + bigdata_tool + databases + emer_tech 

def keywords_f(soup_obj):
    """
    Get keywords from html(soup) and returns a list of keywords
    """
    for script in soup_obj(["script", "style"]):
        script.extract() # Remove these two elements from the BS4 object
    text = soup_obj.get_text() 
    lines = (line.strip() for line in text.splitlines()) # break into line
    chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break multi-headlines into a line each
    text = ''.join(chunk for chunk in chunks if chunk).encode('utf-8') # Get rid of all blank lines and ends of line
    try:
        text = text.decode('unicode_escape').encode('ascii', 'ignore') # Need this as some websites aren't formatted
    except:                                                          
        return
    ## Don't need to print text
    #print(text)
    ### Decode bytes text
    text = text.decode('utf-8')                                                       
    text = re.sub("[^a-zA-Z+3]"," ", text)  
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text) # Fix spacing issue from merged words
    text = text.lower().split()  # Go to lower case and split them apart
    stop_words = set(stopwords.words("english")) # Filter out any stop words
    text = [w for w in text if not w in stop_words]
    text = list(set(text)) #only care about if a word appears, don't care about the frequency
    keywords = [str(word) for word in text if word in overall_dict] #if a skill keyword is found, return it.
    return keywords

job_keywords=[] # create dict to store keyword hits, and urls
for i in range(len(goodUrls)): # iterative across urls
    get_info = True
    try:
        driver.get(base_url+goodUrls[i]) # Try to get the url
    except TimeoutException:
        get_info = False  # skip this url
        continue
    time.sleep(1) #waits for a random time so that the website don't consider you as a bot (not applicable?)
    if get_info:
        # Get keywords from job posting and append to dataframe, merging will occur later
        soup=BeautifulSoup(driver.page_source,'lxml')
        print('Getting data from %s' % base_url+goodUrls[i])
        single_job = keywords_f(soup)   # extract keywords from posting
        print('Extracted %d job keywords from posting %d' % (len(single_job),i))
        
        # This should get three tables, one with the job description, one with related disciplines that can apply, and finally organizational information, ie (Amazon)
        jobDescTable = driver.find_elements_by_class_name("table-bordered");
        # Add tables tags to create proper html
        table1 = r'<table>'+jobDescTable[0].get_attribute('innerHTML') + r'</table>'
        table1 = table1.replace("\t", "").replace("\r", "").replace("\n", "")
        table2 = jobDescTable[1].get_attribute('innerHTML')
        table2 = r'<table>'+table2.replace("\t", "").replace("\r", "").replace("\n", "") + r'</table>'
        table3 =  r'<table>'+jobDescTable[2].get_attribute('innerHTML') + r'</table>'
        table3 = table3.replace("\t", "").replace("\r", "").replace("\n", "")
        
        urlString= (base_url+goodUrls[i])
        # Find number in url, re.findall returns a single item list in this case
        jobNum = re.findall(r'\d+', urlString)
        fileName = 'job%s.html' % jobNum[0] # Create html file with job ID #
        # Print each job posting as an individual job posting
        with open(fileName, "wb") as file:
            # encode tables as bytes
            table1=table1.encode() 
            table2=table2.encode()
            table3=table3.encode()
            # Write tables to html file
            file.write(table1)
            file.write(table2)
            file.write(table3)
        
        ### Apply LIM URL, job keywords and single job relative link
        job_keywords.append([base_url+goodUrls[i],single_job,fileName])

print('done searching for jobs \n')
## Produce the Result dataframe
skills_dict = [w[1] for w in job_keywords]
dict={}
for words in skills_dict:
    for word in words:
        if not word in dict:
            dict[word]=1
        else:
            dict[word]+=1
# Calculate the frequency of keywords using a dataframe
Result = pd.DataFrame()
Result['Skill'] = dict.keys()
Result['Count'] = dict.values()
Result['Ranking'] = Result['Count']/float(len(job_keywords))

pd.set_option('display.max_colwidth', -1) #display entire column (needed for writing to html file)
job_output = pd.DataFrame.from_dict(job_keywords,orient='columns') # create dataframe
# Rename default columns to something meaningful
job_output.rename(columns={0: 'Hyperlinks', 1: 'Keywords',2:'Relative Link'}, inplace=True)
# Create clickable urls back to LIM
job_output['Hyperlinks'] = job_output['Hyperlinks'].apply(lambda x: r'<a href = "{0}">{0:.25s}</a>'.format(x))
# Create relative urls in the html folder from the main html file.
job_output['Relative Link'] = job_output['Relative Link'].apply(lambda x: r'<a href = "{0}">{0:.25s}</a>'.format(x))

# Create a single dataframe containing metadata from LIM and relative urls, keywords and links back to LIM
merged_table = job_output.join(pandasHTMLTable)
# create html table that contains link tags (<a> </a>), need escape = False
outputMergeOutput = merged_table.to_html(buf=None, columns=None, col_space=None, header=True, index=True, na_rep='NaN', formatters=None, float_format=None, sparsify=None, index_names=True, justify='left', bold_rows=True, classes='myTable', escape=False, show_dimensions=True)

# Output final html file, clean up
with open("outputMetaData.html", "w") as fileMeta:
    fileMeta.write(outputMergeOutput)

time.sleep(1) # Let the user actually see something!
driver.quit()
### Could add regex to highlighting COMPUTER ENGINEERING