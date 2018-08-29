# -*- coding: utf-8 -*-
"""

@author: David Li
Date: Aug 28, 2018
File Name: lim_job_scrapper.py
Summary: Extract metadata from job postings, keywords and save job postings as static html pages. Requires the user can access https://learninginmotion.uvic.ca and submitted their "pink slip" see (https://web.uvic.ca/calendar2018-01/undergrad/engineering/co-op.html) for details

    This program will log into lim using an automated browser, then:
        1. find job postings, 
        2. extract metadata for job Postings.
        3. create a html document containing all extracted data
    
    Arguments passed in:
        1. UVIC netlink ID
        2. UVIC password
        3. Relative term, current(default, looking for co-op in the next term), future(looking for co-op starting a few months later), past
    
	
    Output:
        Produces one index.html page containing relative links to individual job postings, keywords and links to the LIM webpage. Requires selenium, BeautifulSoup and pandas. 
        
        Future improvements could include using a jinja template to improve the appearance of the html pages, would need to add css, also searchable/sortable tables would be helpful.
"""

# Make sure arguments are passed in
import sys
print('Starting Script to scrap uvic job postings')
if len(sys.argv) < 3:
	print('pass in more arguments')
	sys.exit()
print('Loading Packages')
# Load packages
import time
from selenium import webdriver
from bs4 import BeautifulSoup

import os
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.common.exceptions import TimeoutException
import re

from nltk.corpus import stopwords
print('Reading Arguments')
my_username = sys.argv[1]  # netlinkID is passed in as command line argument
print('Hello', my_username, '\n')
my_password = sys.argv[2]  # netlinkID password is passed in as command line argument

# Pass in the coopTerm, this is necessary to select the correct term url, to start parsing jobs
print('Searching for jobs in %s term' % sys.argv[3])
driver = webdriver.Chrome()# Optional argument, if not specified will search path.
print('Opening browser\n')

# Get the LIM URL and logon
driver.get('https://learninginmotion.uvic.ca/login/student.htm')
time.sleep(7.5) # Let the user actually see something!
username = driver.find_element_by_name("username") 
password = driver.find_element_by_name("password")
username.send_keys(my_username)
password.send_keys(my_password)

# Click the logon button
driver.find_element_by_name("form-submit").click()
time.sleep(2)

# Click the other submit button allowing personal data to be used
# I suspect using something like selenium requires signing off on information being used every time, i.e no cookies.
attempts = 0
while attempts < 3:
    try:
        driver.find_element_by_name("_eventId_proceed").click()
        break
    except Exception as e:
        print(e)
        time.sleep(3)
        attempts = attempts+1

## Go to the page with job postings
driver.get('https://learninginmotion.uvic.ca/myAccount/co-op/postings.htm')

urls = []

# Current, for example if I am taking courses in the spring and seeking co-op in the summer, this is the best option.
if str.lower(sys.argv[3]) == "current":
    term_num = 1
elif str.lower(sys.argv[3]) == "past":
    term_num = 2
else :
    term_num = 3 # 8 months away

# Grabs the correct url for the selected term
term_posting_path = r'//*[@id="dashboard"]/div[4]/div[1]/div[2]/div/div/a[%d]' % term_num

# Since javascript:void(0) is used in many urls on LIM, a script must be executed on the element before proceeding
copost_link = driver.find_element(By.XPATH, term_posting_path)
driver.execute_script("arguments[0].click();", copost_link)

### Base url of job postings, the metadata table contains relative urls from the base_url
base_url = 'https://learninginmotion.uvic.ca/myAccount/co-op/postings.htm'

time.sleep(6)
# Get links from metadata table about job postings
post_table = driver.find_element_by_id('postingsTable')
post_table_HTML = post_table.get_attribute('innerHTML')
soup = BeautifulSoup('<table>'+post_table_HTML+'</table>','lxml')
urls = soup.findAll('a')

### Get only the href field from the urls
urlsTest = [link['href'] for link in urls] 
### remove all the 'useless' links, used to save the job posting, apply to it, and sorting.
goodUrls  = [ x for x in urlsTest if "javascript:void(0)" not in x ]

### append the number of postings to a "txt" file, plot later.
date = time.strftime("%Y%m%d")
with open("numofJobs.txt", "a+") as f:
	f.write("%s,%s \n" % (date, len(goodUrls)))
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
html_output = soup.prettify("utf-8") # Clean html output for pandas


### Create pandas df and remove columns for saving, applying and whetever or not the user applied to a posting.

pandas_table_HTML = pd.read_html(html_output)
pandas_table_HTML = pandas_table_HTML[0]
pandas_table_HTML.drop(pandas_table_HTML.columns[7:9], axis=1, inplace=True)

def create_new_dir(dir_name):
    """
    Check if a directory exists, if not create and cd it.
    """
    directory = dir_name
    if not os.path.exists(directory):
        os.makedirs(directory)
    # go to that new directory
    os.chdir(directory)

### Create new directory for term of interest
create_new_dir('Fall2018')

### Create new directory
year_month_day = time.strftime("%Y%m%d")
create_new_dir(year_month_day)
	
### Create subfolder for html files
create_new_dir('html')

#### Get keywords from job postings
#for this function, thanks to this blog:https://jessesw.com/Data-Science-Skills/ 
program_languages=['bash','r','python','java','c++','ruby','perl','matlab','javascript','scala','php','julia','VBA','Power BI']
analysis_software=['excel','tableau','d3.js','sas','spss','d3','saas','pandas','numpy','scipy','sps','spotfire','scikits.learn','splunk','powerpoint','h2o']
bigdata_tool=['hadoop','mapreduce','spark','pig','hive','shark','oozie','zookeeper','flume','mahout']
databases=['sql','nosql','hbase','cassandra','mongodb','mysql','mssql','postgresql','oracle db','rdbms']
emer_tech = ['C#','C++','JIRA','Confluence','machine learning']
game_dev = ['LUA','Sketchup','Unity']
other_tech = ['QT','Squish','Windows 10','big data','Unstructured Data handling']
# Produce dictionary of keywords, note that this is not complete
overall_dict = program_languages + analysis_software + bigdata_tool + databases + emer_tech + game_dev + other_tech

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
from jinja2 import Template
jinja_job_template = "../../../lim_job_posting.template"
for i in range(len(goodUrls)): # iterative across urls
    get_info = True
    table1 = ""
    table2 = ""
    table3 = ""
    try:
        driver.get(base_url+goodUrls[i]) # Try to get the url
    except TimeoutException:
        get_info = False  # skip this url
        continue
    time.sleep(2) #waits for a random time so that the website don't consider you as a bot (not applicable?)
    if get_info:
        # Get keywords from job posting and append to dataframe, merging will occur later
        soup=BeautifulSoup(driver.page_source,'lxml')
        print('Getting data from %s' % base_url+goodUrls[i])
        single_job = keywords_f(soup)   # extract keywords from posting
        try:
            print('Extracted %d job keywords from posting %d' % (len(single_job),i))
        except:
            print('Extracted no keywords from posting %d' % (i))
            single_job = ""
        time.sleep(4)
        # This should get three tables, one with the job description, one with related disciplines that can apply, and finally organizational information, ie (Amazon)
        job_desc_table = driver.find_elements_by_class_name("table-bordered");
        # Add tables tags to create proper html
        table1 = r'<table>'+job_desc_table[0].get_attribute('innerHTML') + r'</table>'
        table2 = r'<table>'+job_desc_table[1].get_attribute('innerHTML') + r'</table>'
        table3 =  r'<table>'+job_desc_table[2].get_attribute('innerHTML') + r'</table>'
        
        # Print each job posting as an individual job posting, remove tabs and newline characters from the html
        table1 = table1.replace("\t", "").replace("\r", "").replace("\n", "")
        table2 = table2.replace("\t", "").replace("\r", "").replace("\n", "")
        table3 = table3.replace("\t", "").replace("\r", "").replace("\n", "")
        with open(jinja_job_template) as f:
            job_tmpl = Template(f.read())
        f.close()
        jinja_job_output =job_tmpl.render(
            JOBPOSTINGTABLE = table1,
            APPINFO = table2,
            ORGINFO = table3,
            KEYWORDS = single_job
        )
        
        urlString= (base_url+goodUrls[i])
        # Find number in url, re.findall returns a single item list in this case
        jobNum = re.findall(r'\d+', urlString)
        job_file_html = 'job%s.html' % jobNum[0] # Create html file with job ID #
        with open(job_file_html, "wb") as job_post_file:
            job_post_file.write(jinja_job_output.encode())
        
        ### Apply LIM URL, job keywords and single job relative link
        job_keywords.append([base_url+goodUrls[i],single_job,job_file_html])

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
# Calculate the frequency of keywords using a dataframe, consider adding plot or other data, perhaps save a csv and load it using d3
result = pd.DataFrame()
result['Skill'] = dict.keys()
result['Count'] = dict.values()
result['Ranking'] = result['Count']/float(len(job_keywords))

pd.set_option('display.max_colwidth', -1) #display entire column (needed for writing to html file)
job_output = pd.DataFrame.from_dict(job_keywords,orient='columns') # create dataframe
# Rename default columns to something meaningful
job_output.rename(columns={0: 'Hyperlinks', 1: 'Keywords',2:'Relative Link'}, inplace=True)
# Create clickable urls back to LIM
job_output['Hyperlinks'] = job_output['Hyperlinks'].apply(lambda x: r'<a href = "{0}">{0:.25s}</a>'.format(x))
# Create relative urls in the html folder from the main html file.
job_output['Relative Link'] = job_output['Relative Link'].apply(lambda x: r'<a href = "{0}">{0:.25s}</a>'.format(x))

# Create a single dataframe containing metadata from LIM and relative urls, keywords and links back to LIM
merged_table = job_output.join(pandas_table_HTML)
# create html table that contains link tags (<a> </a>), need escape = False
merged_jobinfotable_html = merged_table.to_html(buf=None, columns=None, col_space=None, header=True, index=True, na_rep='NaN', formatters=None, float_format=None, sparsify=None, index_names=True, justify='left', bold_rows=True, classes='myTable', escape=False, show_dimensions=True)
# Set id using regex, kinda messy I know
merged_jobinfotable_html = re.sub('myTable', r'" id="myTable',merged_jobinfotable_html)
lim_data_Result_csv_file =  r'lim_data_result.csv'
result.to_csv(path_or_buf=lim_data_Result_csv_file,index=True)
# Output final html file, clean up
with open("outputMetaData.html", "w") as fileMeta:
    fileMeta.write(merged_jobinfotable_html)

# Output metadata table as a html file using a  JINJA Template
jinja_main_temp = '../../../lim_metadata.template'
jinja_main_outfile = 'lim_data.html'

result_table_html = result.to_html(buf=None, columns=None, col_space=None, header=True, index=True, na_rep='NaN', formatters=None, float_format=None, sparsify=None, index_names=True, justify=None, bold_rows=True, classes=None, escape=True, max_rows=None, max_cols=None, show_dimensions=True, notebook=False) 

import matplotlib.pyplot as plt
fig = plt.figure() # Create matplotlib figure
default_size = fig.get_size_inches()
ax = fig.add_subplot(111) # Create matplotlib axes
ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

width = 0.4
result.plot(x=['Skill'], y=['Count'], kind='bar', table=False, yerr=None,ax=ax, width=width, position=1,legend=False)
result.plot(x=['Skill'], y=['Ranking'], kind='bar',table=False, yerr=None,ax=ax2, width=width, position=0,legend=True)


ax.set_ylabel('Count')
ax2.set_ylabel('Ranking')

### Must save the image before it is shown
plotname = 'uvic_job_plot' + '.png'
fig.set_size_inches((default_size[0]*2, default_size[1]*2))
fig.tight_layout()
### This should be 2 x 2 times bigger, one 2 for dpi and one 2 for default size
plt.savefig(plotname, dpi = 200)
## Consider adding css to limit the image size on the html output
# Consider adding fig.tight_layout(), to auto adjust image
## Since Ranking is calculated from Count, only one line is needed.

# fig.set_size_inches(8, 6)
# fig.tight_layout()
# plt.show()

with open(jinja_main_temp) as f:
    tmpl = Template(f.read())


jinja_output =tmpl.render(
    RESULTTABLECSV = lim_data_Result_csv_file,
    JOBINFO = merged_jobinfotable_html,
    MATPLOTLIBPLOT = plotname
)
f.close()

with open(jinja_main_outfile,'w',encoding='utf-8') as f:
    f.write(jinja_output)
    
f.close()

#### Output csv data 

#### go to html folder, and then go to Summer 2018 folder, then create a data folder if it doesn't exist
os.chdir(os.path.join('', os.pardir))
os.chdir(os.path.join('', os.pardir))

### Create subfolder for data files
create_new_dir('data')

import time
timestr = time.strftime("%Y%m%d")
job_info_data = r'lim_job_info %s.csv' % timestr 
merged_table.to_csv(path_or_buf=job_info_data,index=True)
time.sleep(1) # Let the user actually see something!
driver.quit()
### Could add regex to highlighting COMPUTER ENGINEERING
