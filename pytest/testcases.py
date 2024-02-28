from unittest import TestCase
import os 
import sys 

utils_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(utils_path)

from utils.Model_PDFClass import MetaDataPDF, ContentPDF
from notebooks.Part2Script_Metadata_Content import TEIFile
from pydantic import ValidationError
from pathlib import Path

class TEIFileTestClass(TestCase):
    def setUp(self):
        xml_folder = os.path.join(os.path.dirname(os.getcwd()), 'xml')
        tei_files = [
            '2024-l1-topics-combined-2.pdf.tei.xml',
            '2024-l2-topics-combined-2.pdf.tei.xml',
            '2024-l3-topics-combined-2.pdf.tei.xml'
        ]
        self.valid_tei_files = [os.path.join(xml_folder, tei_file) for tei_file in tei_files]

    def test_paragraph_length_validation(self):
        for tei_path in self.valid_tei_files:
            tei = TEIFile(tei_path)
            content = tei.content
            max_length = 5000  
            min_length = 20   
            for paragraph in content:
                    actual_length = len(paragraph.paragraph_text)
                    self.assertLessEqual(actual_length, max_length, f"Paragraph exceeds maximum length: {tei_path}. Found: {actual_length}, Expected: <= {max_length}")
                    self.assertGreaterEqual(actual_length, min_length, f"Paragraph falls below minimum length: {tei_path}. Found: {actual_length}, Expected: >= {min_length}")

    def test_valid_tei_metadata_date_format(self):
        for tei_path in self.valid_tei_files:
            tei = TEIFile(tei_path)
            metadata = tei.metadata
            actual_date_type = type(metadata.doc_date).__name__
            self.assertIsInstance(metadata.doc_date, (str, type(None)), f"Invalid doc_date type: {tei_path}. Found: {actual_date_type}, Expected: (str, None)")

    def test_valid_tei_content_details(self):
        for tei_path in self.valid_tei_files:
            tei = TEIFile(tei_path)
            content = tei.content
            actual_section_title_type = type(content[0].section_title).__name__
            self.assertIsInstance(content[0].section_title, (str, type(None)), f"Invalid section_title type: {tei_path}. Found: {actual_section_title_type}, Expected: (str, None)")

    def test_unique_content_identifiers(self):
        for tei_path in self.valid_tei_files:
            tei = TEIFile(tei_path)
            content = tei.content
            actual_content_id_0 = content[0].content_id
            actual_content_id_1 = content[1].content_id
            self.assertNotEqual(actual_content_id_0, actual_content_id_1, f"Content identifiers are not unique: {tei_path}. Found: {actual_content_id_0}, {actual_content_id_1}")