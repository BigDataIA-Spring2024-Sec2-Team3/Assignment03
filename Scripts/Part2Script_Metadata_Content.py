from bs4 import BeautifulSoup
import os 
import sys 

utils_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(utils_path)

from utils.Model_PDFClass import MetaDataPDF, ContentPDF

xml_folder = os.path.join(os.path.dirname(os.getcwd()), 'xml')
#xml_folder = os.path.join(os.getcwd(), 'xml')
METADATA_FILES = [os.path.join(xml_folder, f'Grobid_RR_2024_l{i}_combined_metadata.xml') for i in range(1, 4)]
CONTENT_FILES = [os.path.join(xml_folder, f'2024-l{i}-topics-combined-2.pdf.tei.xml') for i in range(1, 4)]


class Dataset:
    
    def __init__(self):
        self.metadata = []
        self.content = []
        self.load_data()
        
    def load_data(self):
        
        for file in METADATA_FILES:
            metadata = self.parse_metadata(file)
            self.metadata.append(metadata)
            
        for file in CONTENT_FILES:
            content = self.parse_content(file)
            self.content.extend(content)
            
    def parse_metadata(self, file):
        # Parse metadata XML
        with open(file) as f:
            soup = BeautifulSoup(f, 'xml')
            
        filename = soup.find('Filename').text
        title = soup.find('Title').text
        header = soup.find('Header').text
        paragraph = soup.find('Paragraph').text
        idno = soup.find('Idno').text
        application = soup.find('Application').text
        
        metadata = MetaDataPDF(
            filename = filename,
            title = title,
            header = header,
            paragraph = paragraph,
            idno = idno,
            application = application
        )
        
        return metadata
    
    def parse_content(self, file):
        # Parse content XML
        with open(file) as f:
            soup = BeautifulSoup(f, 'xml')
            
        contents = []
        for div in soup.find_all('div'):
            
            section_title = div.find('head').text if div.find('head') else None
            
            for i, p in enumerate(div.find_all('p')):
                content = ContentPDF(
                    content_id = len(contents)+1, 
                    doc_id = 1,
                    section = 'body',
                    section_title = section_title,
                    paragraph_num = i,
                    paragraph_text = p.text
                )
                contents.append(content)
                
        return contents
    
dataset = Dataset()
print(dataset.metadata[2])
print(dataset.content[2])