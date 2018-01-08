# UVIC-Job-Board-Scrapper
Extract information from job postings on the uvic job board, learning in motion (LIM).

## Information
@author: David Li
Date: Jan 01, 2018
File Name: lim_job_scrapper.py
Summary: Extract metadata from job postings, keywords and save job postings as static html pages. Requires the user can access https://learninginmotion.uvic.ca and submitted their "pink slip" see (https://web.uvic.ca/calendar2018-01/undergrad/engineering/co-op.html) for details.

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

See [Uvic Job Postings (Jan 01, 2018)](file:///C:/Users/wu/Downloads/Job%20Hunt/Scripts/html/index.html)

#### Future improvements 
* Adding a summary of results (could be a plot).
* Determining if a job is suitable based on keywords.
* Adding searching/sortable tables.

##### Nice to Have
* Summarizating the job posting.
* Print out all html files as pdfs.
