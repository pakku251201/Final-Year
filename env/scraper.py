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

# get user input
# console.print("Enter Job Title :", style="bold green", end=" ")
# inputJobTitle = input()
# console.print("Enter Job Location :", style="bold green", end=" ")
# inputJobLocation = input()


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


async def scrapeLinkedin(inputJobTitle, inputJobLocation):
    driver = DriverOptions()
    counter = 0
    pageCounter = 1
    results = []
    url = f"https://www.linkedin.com/jobs/search/?&keywords={inputJobTitle}&location={inputJobLocation}&refresh=true&start={counter}"
    print(url)
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
                results.append({"title": jobTitle, "location": jobLocation, "company": jobCompany, "desc" : jobDescription, "link": jobLink})

    finally: 
        driver.quit()
        return results


async def main():
    await scrapeLinkedin()

    # # create table
    # table.add_column("Title")
    # table.add_column("Company")
    # table.add_column("Location")
    # table.add_column("Link", width =100)
    # table.add_column("Description")
    # # loop over dataframe and print rich table
    # for index, row in df.iterrows():
    #     table.add_row(
    #         f"{row['Title']}",
    #         f"{row['Company']}",
    #         f"{row['Location']}",
    #         f"{row['Link']}",
    #         f"{(row['Description'])[:20]}...",
    #     )

    # console.print(table)

    # console.print("Save results locally? (y/n) :", style="bold yellow", end=" ")
    # continueInput = input()

    # if continueInput == "y":
    #     df.to_csv(f"{inputJobTitle}_{inputJobLocation}_jobs.csv", index=False)

    

    # Save scraped data into a CSV file
    with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Title", "Location", "Company", "Link", "Description"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)


if __name__ == "__main__":
    # run main function
    asyncio.run(main())



