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

    def test_valid_tei_metadata_date_format(self):
        # Arrange & Act
        for tei_path in self.valid_tei_files:
            tei = TEIFile(tei_path)

            # Assert
            self.assertIsInstance(tei.metadata.doc_date, (type(None), datetime.date))

    def test_valid_tei_content_details(self):
        # Arrange & Act
        for tei_path in self.valid_tei_files:
            tei = TEIFile(tei_path)

            # Assert
            content_list = tei.content
            self.assertTrue(all(self.validate_content_details(content) for content in content_list))

    def validate_content_details(self, content):
        # Add your specific content validations here
        # Return True if content is valid, False otherwise
        return isinstance(content.paragraph_text, str) and len(content.paragraph_text) > 0

    def test_unique_content_identifiers(self):
        # Arrange & Act
        for tei_path in self.valid_tei_files:
            tei = TEIFile(tei_path)

            # Assert
            content_list = tei.content
            identifiers = set((content.formula_id, content.figure_id, content.note_id) for content in content_list)
            self.assertEqual(len(identifiers), len(content_list))
