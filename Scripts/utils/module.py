from pydantic import BaseModel, PositiveInt, HttpUrl,field_validator
from typing import List

class webPage(BaseModel):
    # data = [topic, year_text, level_text, paragraphs, bullet, full_link, link1]
    topic: str
    year: PositiveInt
    level: str
    paragraphs: str
    bullet: str
    full_links: HttpUrl
    link1: HttpUrl

    # year: 2024 Curriculum
    @field_validator('year', pre=True)
    def extract_year(cls, v):
        if isinstance(v, str):  
            # extract year from the str
            try:
                year_part = v.split(' ')[0]  # year at the first
                if 1900 <= year_part <=2100:
                    return int(year_part)  # return to int
                else:
                    raise ValueError(f"Year {year_part} not in range 1900-2100.")
            except ValueError:
                raise ValueError(f"No year in '{v}'.")
        
        return v
    



    @classmethod
    def create_from_list(cls, data_list):
        field_names = ['topic', 'year', 'level', 'paragraphs', 'bullet', 'full_links', 'link1']
        data_dict = dict(zip(field_names, data_list))
        return cls(**data_dict)


    @classmethod
    def scrape_content(cls, driver,page_link: HttpUrl) -> webPage:
        # Function to scrape content using BeautifulSoup
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
        introduction_section = soup.find('h2', class_='article-section', text=['Introduction', 'Overview'])

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
        learning_outcomes_section = soup.find('h2', class_='article-section', text='Learning Outcomes')
        if learning_outcomes_section is not None:
            outcomes_section= learning_outcomes_section.find_next_sibling()
            bullet_points = [li.get_text(strip=True) for li in outcomes_section.find_all(['li'])] 
            if bullet_points is None:
                bullet_points = [li.get_text(strip=True) for li in outcomes_section.find_all(['p'])]
            
            bullet = '\n'.join(bullet_points)
        else:
            bullet="Doesn't Exist"

        # Find the <a> tag for Full PDF link
        link_tag = soup.find('a', class_='locked-content')
        # Extract the link
        if link_tag is not None:
            link = link_tag['href']
            full_link = "https://www.cfainstitute.org" + link
        else:
            full_link = "Doesn't Exist"
            
        # Store all extracted data in list format
        data = [topic, year_text, level_text, paragraphs, bullet, full_link, link1]
        
        return cls.create_from_list(data)
        # print(*data)
        

    @classmethod
    def process_coveo_link(cls, driver, link):
        """Function to click CoveoLink and return to main page"""
        driver.execute_script("window.open('{}', '_blank');".format(link))
        
        # Switch to new tab if opened
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])
        
        # Scraping content
        article = cls.scrape_content(driver, link)
        
        # Closing the tab and switching back to main page
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return article
    
    @classmethod
    def webScrabing(cls)-> List:
        """Function to return the articles"""
        articles = []
        
        driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
        time.sleep(2)
        
        for offset in [0,100,200]:
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
                    articles.append( cls.process_coveo_link(driver, link) )    
                    # Wait for some time to simulate human-like behavior
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error: {e}")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
        driver.quit()
        return articles