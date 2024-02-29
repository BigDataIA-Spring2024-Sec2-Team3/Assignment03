# File: WebScraping
# Run under root
# command: python src/WebScraping.py

#Importing all important libraries for automation and scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pydantic import HttpUrl
import time
import csv
import sys
import os

sys.path.append(os.getcwd())
from utils.URLclass import Article


def create_from_list(data_list):
    """Make sure use a dict for class objects create"""
    field_names = ['topic', 'year', 'level', 'paragraphs', 'bullet', 'full_links', 'link1']
    data_dict = dict(zip(field_names, data_list))
    return Article(**data_dict)



def scrape_content(driver,page_link: HttpUrl) :
    """Function to scrape content using BeautifulSoup"""
    link1 = page_link
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    topic_class = soup.find('h1', class_='article-title')
    
    # Extract the article title text
    topic = topic_class.text.strip()
    
    # Extract the year text
    year_span = soup.find('span', class_='content-utility-curriculum')
    if year_span is not None:
        year_text = year_span.get_text(strip=True)
    else:
        year_text = "Doesn't Exist"

    # Extract the level text
    level_span = soup.find('span', class_='content-utility-level')
    # Find the span with class "content-utility-topic" within the level_span
    if level_span is not None:
        level_text = level_span.find('span', class_='content-utility-topic').text.strip()
    else:
        level_text = "Doesn't Exist"

    # Find the introduction paragraphs
    introduction_section = soup.find('h2', class_='article-section', string=['Introduction', 'Overview'])

    # Find all paragraphs within the Introduction section
    if introduction_section is not None:
        intro_paragraphs = introduction_section.find_next_siblings('p')
        # Extract the text from the paragraphs
        paragraphs = ''
        for p in intro_paragraphs:
            # Check if the paragraph is within the Example section
            if p.find_parents('figure', class_='example'):
                break
            # Append text from paragraph
            paragraphs += p.get_text(strip=True) + ' '
    else: 
        paragraphs = "Doesn't Exist"

    # Find all <li> elements within the <ol> element to extract Learning Outcomes text
    learning_outcomes_section = soup.find('h2', class_='article-section', string='Learning Outcomes')
    if learning_outcomes_section is not None:
        outcomes_section= learning_outcomes_section.find_next_sibling()
        bullet_points = [li.get_text(strip=True) for li in outcomes_section.find_all(['li'])] 
        if bullet_points is None:
            bullet_points = [li.get_text(strip=True) for li in outcomes_section.find_all(['p'])]
        
        bullet = '\n'.join(bullet_points)
    else:
        bullet="Doesn't Exist"

    # Find the <a> tag for Full PDF link
    # get the content from the PDF
    locked_content_links = soup.find_all('a', class_='locked-content')

    # get rid of the underlined-anchor
    target_links = [link for link in locked_content_links if 'underlined-anchor' not in link.get('class', [])]

    full_link = "Doesn't Exist" # init
    for link_tag in target_links:
        if link_tag is not None:
            link = link_tag['href']
            full_link = "https://www.cfainstitute.org" + link
        

    # # Find the <a> tag for Full PDF link
    # link_tag = soup.find('a', class_='locked-content')
    # # Extract the link
    # if link_tag is not None:
    #     link = link_tag['href']
    #     full_link = "https://www.cfainstitute.org" + link
    # else:
    #     full_link = "Doesn't Exist"
        
    # Store all extracted data in list format
    data = [topic, year_text, level_text, paragraphs, bullet, full_link, link1]
    
    return create_from_list(data)
    # print(*data)
    

def process_coveo_link(driver, link):
    """Function to click CoveoLink and return to main page"""
    driver.execute_script("window.open('{}', '_blank');".format(link))
    
    # Switch to new tab if opened
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[1])
    
    # Scraping content
    article = scrape_content(driver, link)
    
    # Closing the tab and switching back to main page
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return article


def webScrabing():
    """Function to return the articles list"""
    articles = []
    
    driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
    time.sleep(2)
    
    for offset in [0, 100, 200]:
        main_frame = f'https://www.cfainstitute.org/membership/professional-development/refresher-readings#first={offset}&sort=@refreadingcurriculumyeardescending&numberOfResults=100'
        driver.get(main_frame)
        time.sleep(2)
    
        # Wait for CoveoLinks to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "CoveoResultLink")))
        
        # Find all CoveoLinks
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = soup.find_all('a', class_='CoveoResultLink')
    
        # Extract the 'href' attribute from each link
        coveo_links = [link['href'] for link in links]
        print(len(links))     # To check no. of links extracted from the page
        for link in coveo_links:
            try:
                articles.append( process_coveo_link(driver, link) )    
                # Wait for some time to simulate human-like behavior
                time.sleep(0.5)
            except Exception as e:
                print(f"Error when get data: {e}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
    driver.quit()
    return articles



## print the log
log_file = open("data/log.txt", "w")
original_stdout = sys.stdout
sys.stdout = log_file


articles = webScrabing()

sys.stdout = original_stdout
log_file.close()

# for article in articles:
#     print(article.topic, 'Succeed')
print(len(articles), 'Succeed')


## write to csv
article = articles[0]

# turn to dict structure
article_dict = article.dict()

# point the file position
csv_file = "data/items.csv"


with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=article_dict.keys())
    writer.writeheader()  # header
    for article in articles:
        article_dict = article.dict()
        writer.writerow(article_dict)  # write in data
