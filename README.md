# UVIC-Job-Board-Scrapper
Extract information from job postings on the uvic job board, learning in motion (LIM).

![Script in Action](scripterInAction.gif)

Soon, I will generate a report highlighting statistics of interest, where the jobs are on a map (maybe), saturation, ( maybe use num of jobs/(apps per job*deadline weight +num of jobs), and number of jobs vs date.

**Requirements**

1. This program uses selenium to navigate and extract html from webpages, then performs analysis with pandas and nltk.
2. If anything breaks just add a time.sleep (5) because when I was testing this script, I tested it a lot, and files were stored on the cache, resulting a quicker load time.
## Information

| info | value|
|--- | --- |
|author: | David Li |
|Date:  | Jan 07, 2018 |
|File Name: | lim_job_scrapper.py |

Summary: Extract metadata from job postings, keywords and save job postings as static html pages. Requires the user can access https://learninginmotion.uvic.ca and submitted their "pink slip" see (https://web.uvic.ca/calendar2018-01/undergrad/engineering/co-op.html) for details.

This program will log into lim using an automated browser, then:
1. find job postings, 
2. extract metadata for job Postings.
3. create a main html file containing metadata that is linked to individual job postings.

Arguments passed in:
1. UVIC netlink ID
2. UVIC password
3. Co-op term of interest. For example current( i.e, taking classes in the spring, looking for summer co-op), future, past

Output:
    Produces one index.html page containing relative links to individual job postings, keywords and links to the LIM webpage. Requires selenium, BeautifulSoup and pandas. 

As shown in the screenshot below the value of current depends where you are at in the term, for example, at May 2018, current respresents the preceeding term, Fall 2018, but a few weeks ago, we were still at Summer 2018.

![What does current mean](https://github.com/FriendlyUser/UVIC-Job-Board-Scrapper/blob/master/job_scrapper_currentpic.png)

Future improvements could include using a ~~jinja template to improve the appearance of the html pages, would need to add css, also searchable/sortable tables would be helpful.~~

See  [Uvic Job Postings (Jan 01, 2018)](https://web.uvic.ca/~lidavid/jobScrapping/LIMScrap/) for sample output.

#### Future improvements 
* ~~Adding a summary of results (could be a plot).~~
* Determining if a job is suitable based on keywords ( text analysis).
* ~~Implementing searching/sortable tables.~~
* ~~Improving the appearance of HTML tables by rendering a template (Jinja)~~

##### Nice to Have
* Summarizating the job posting.
* Print out all html files as pdfs.

### Running the Script

After navigating to the directory of the script and installing the necessary packages (if needed).
The following commands can be used to run the script. 

Also, it will count the number of jobs vs the date

|Date       | Num of jobs |
|----       |             |
|2018-04-26 | 39          |

```bash
python lim_job_scrapper.py netlinkid netlinkPass term year 
```

Where the arguments are:
* netlinkid and netlinkPass are uvic login information
* term is either [Current, Future, Past]

![File Directory](https://github.com/FriendlyUser/UVIC-Job-Board-Scrapper/blob/master/job_scrap_file_directory.png)
