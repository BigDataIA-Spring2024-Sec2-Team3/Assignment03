from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class MetaDataPDF(BaseModel):
    doc_id: int
    doc_name: str
    doc_source: str
    doc_date: Optional[date] = None
    doc_md5: str
    doc_length: int

    class Config:
        orm_mode = True

class ContentPDF(BaseModel):
    content_id: int
    doc_id: int
    section: str
    section_title: Optional[str] = None
    paragraph_num: Optional[int] = None
    paragraph_text: Optional[str] = None
    formula_id: Optional[str] = None
    figure_id: Optional[str] = None
    note_id: Optional[str] = None

    class Config:
        orm_mode = True