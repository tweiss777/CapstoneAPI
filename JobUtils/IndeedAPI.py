import urllib.request

import certifi
import urllib3
from bs4 import BeautifulSoup

# Class for indeed api
class IndeedAPi:
    # limit should be in increments of 10
    def retrieve_urls(self,query,zipcode,page_limit):

        page = 0
        total_job_links = []
        while page <= page_limit:
            params = {
                'q' : query,
                'l' : str(zipcode),
                'start': str(page)
            }

            link = "https://www.indeed.com/jobs?" + urllib.parse.urlencode(params)
            http = urllib3.PoolManager(cert_reqs = 'CERT_REQUIRED', ca_certs = certifi.where())
            response = http.request('GET', link)
            html = response.data
            soup = BeautifulSoup(html, 'html.parser')

            job_links = [a_tags for a_tags in soup.find_all('a', class_='turnstileLink', href=True)]
            for job_link in job_links:
                total_job_links.append(job_link['href'])
            page +=10

        return total_job_links

    # test method that returns individual job description
    def getJobMarkup(self,href):

        #site url contatinated with the href taken from the dom
        link = "https://indeed.com" + str(href)
        try:
            # retrieve the url even if its a redirect
            initial_response = urllib.request.urlopen(link)
            # final link of the redirect if there is one
            finalLink = initial_response.geturl()

            # time.sleep(5)
            # initialize pool manager and request the html data from url
            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            response = http.request('GET', finalLink)
            html = response.data

            soup = BeautifulSoup(html, 'html.parser')
            job_title = soup.title.string
            job_title = job_title.split('-')[0].rstrip()

            # find the tag that holds the description.
            jdMarkup = soup.find_all('div', class_='jobsearch-JobComponent-description')

            # when the job description cannot be found
            if len(jdMarkup) < 1:
                return
            # return the title of the job and the html markup
            return (job_title, jdMarkup[0],finalLink)
        except Exception as inst:
            print(inst)



    #method that filters out NoneType indices in the jobs list
    def filterJobs(self,jobs):
        filtered_jobs = [job for job in jobs if job is not None]
        return filtered_jobs

    #method that will generate a json api for the jobs
    #returns a dictionary that should be exported as json data
    def generateJson(self,jobs):
        #assign a job_id to the job
        job_id = 0
        #initialize our json data to an empty dictionary at first
        json_data = {}
        for job in jobs:
            #set an empty dictionary to the job_id key
            json_data[job_id] = {}
            #set the title key to the title found in the first part of the tuple
            json_data[job_id]["title"] = job[0] #taken from the 0th indice of the tuple.
            # store the markup in the markup variable
            markup = job[1]
            json_data[job_id]["description"] = markup.get_text()
            json_data[job_id]["job_url"] = job[2]
            # json_data[job_id]["keywords"] = r.process_rake(json_data[job_id]["description"])
            #increment the job_id count by 1
            job_id +=1

            # return the json data
        return json_data
    def generateJsonParagraphs(self,jobs):
        #assign id to job
        job_id = 0
        json_data = {}

        for job in jobs:
            # holds the job_id as a key :
            # {title: str, description: list of paragraphs}
            json_data[job_id] = {}
            json_data[job_id]["title"] = job[0]
            html = job[1].find_all(['p', 'ul'])

            if len(html) > 0:
                json_data[job_id]["description"] = [tag.get_text() for tag in html]
            else:
                html = job[1].contents[1:]
                paragraphs = []
                for tag in html:
                    try:
                        paragraphs.append(tag.get_text())
                    except:
                        paragraphs.append(tag)
                json_data[job_id]["description"] = paragraphs
            job_id+=1
        return json_data





