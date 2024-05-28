# web scraping
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# html parsing
from bs4 import BeautifulSoup

# dataframes
import pandas as pd

# async
import asyncio

import csv

# terminal formatting
from rich.progress import track
from rich.console import Console
from rich.table import Table

# instantiate global variables
df = pd.DataFrame(columns=["Title", "Location", "Company", "Link", "Description"])
console = Console()
table = Table(show_header=True, header_style="bold")

async def scrapeJobDescription(url):
    global df
    driver = DriverOptions()
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    try:
        jobDescription = soup.find(
            "div", class_="show-more-less-html__markup"
        ).text.strip()
        return jobDescription
    except:
        return ""

def DriverOptions():
    options = Options() 
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    return driver

async def scrapeNaukri(inputJobTitle, inputJobLocation, counter):
    driver = DriverOptions()
    inputJobTitle = inputJobTitle.replace(" ", "-")
    url = f"https://www.careerbuilder.co.in/jobs?keywords={inputJobTitle}&location={inputJobLocation}"
    res = []
    try:
        driver.get(url)

        soup = BeautifulSoup(driver.page_source,'html.parser')

        # print(soup.prettify())
# jobclassname srp-jobtuple-wrapper
# list styles_job-listing-container__OCfZC


        results = soup.find("ol",class_='ml5 list-style-none')

        job_elems = results.find_all('li')
        for job_elem in job_elems:
            # print(job_elem)
 
            Title = job_elem.find('a',class_='data-results-content block job-listing-item').get('title')
            # print(Title)
            # Post Title
            URL = url
            # print(URL)

            jobdetails = job_elem.find('div',class_='data-details').find_all('span')
            # Company Name
            Company = jobdetails[0].text
            # print(Company)/

            # Location for the job post
            Loc = jobdetails[1].text
            # print(Loc)

        #   Appending data to the DataFrame 
            res.append({'title':Title,'company':Company,'location':Loc,'link':URL})
    except Exception as e:
        print(e)
    finally:
        driver.close()
        counter = int(counter)
        counter += 1
        return [res,counter]

async def scrapeLinkedin(inputJobTitle, inputJobLocation, counter):
    driver = DriverOptions()
    pageCounter = 1
    results = []
    url = f"https://www.linkedin.com/jobs/search/?&keywords={inputJobTitle}&location={inputJobLocation}&refresh=true&start="
    url = url + str(counter)
    counter=int(counter)
    try:
        driver.get(
            url
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        ulElement = soup.find("ul", class_="jobs-search__results-list")
        liElements = ulElement.find_all("li")
        for item in track(
            liElements, description=f"Linkedin - Page: {pageCounter}"
        ):
            jobTitle = item.find(
                "h3", class_="base-search-card__title"
            ).text.strip()
            jobLocation = item.find(
                "span", class_="job-search-card__location"
            ).text.strip()
            jobCompany = item.find(
                "h4", class_="base-search-card__subtitle"
            ).text.strip()
            jobLink = item.find_all("a")[0]["href"]

            jobDescription = await scrapeJobDescription(jobLink)

            if jobTitle and jobLocation and jobCompany and jobLink:
                counter += 1
                results.append({"title": jobTitle, "location": jobLocation, "company": jobCompany, "link": jobLink})
    except Exception as e:
        print(e)
    finally: 
        driver.quit()
        return [results,counter]

async def main():
    # await scrapeLinkedin()
    # Save scraped data into a CSV file
    # with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #     fieldnames = ["Title", "Location", "Company", "Link", "Description"]
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
    #     writer.writeheader() 
    #     for result in results:
    #         writer.writerow(result)
    pass

if __name__ == "__main__":
    # run main function
    asyncio.run(main())



