import requests
from bs4 import BeautifulSoup

def naukri_jobs():
        url = f"https://www.naukri.com/{job_title}-jobs-in-{location}"
        response = requests.get(url)
        soup = BeautifulSoup(response)
