from bs4 import BeautifulSoup
from typing import List, Optional

from utils.PDFClassModel import MetaDataPDF, ContentPDF

def read_tei(tei_file):
    with open(tei_file, 'r') as tei:
        soup = BeautifulSoup(tei, 'xml')
        return soup


class TEIFile(object):
    def __init__(self, filename: str):
        self.filename = filename
        self.soup = read_tei(filename)
        self._metadata = None
        self._content = None

    @property
    def metadata(self) -> MetaDataPDF:
        if not self._metadata:
            idno = self.soup.find('idno', type='DOI')
            self._metadata = MetaDataPDF(
                doc_id=1,
                doc_name=self.soup.title.text,
                doc_source=self.filename,
                doc_md5=idno.text if idno else '',
                doc_length=10  # dummy value
            )
        return self._metadata

    @property
    def content(self) -> List[ContentPDF]:
        if not self._content:
            content_data = []
            for div in self.soup.body.find_all("div"):
                if not div.get("type"):
                    section_title = div.head.text if div.head else None
                    for p_num, p in enumerate(div.find_all('p')):
                        content_data.append(
                            ContentPDF(
                                content_id=len(content_data) + 1,
                                doc_id=self.metadata.doc_id,
                                section='body',
                                section_title=section_title,
                                paragraph_num=p_num,
                                paragraph_text=p.text
                            )
                        )
            self._content = content_data
        return self._content

tei = TEIFile('./xml/2024-l1-topics-combined-2.pdf.tei.xml')
print(tei.metadata)
print(tei.content[1].json())