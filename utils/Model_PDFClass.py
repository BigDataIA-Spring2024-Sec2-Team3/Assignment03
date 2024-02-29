from pydantic import BaseModel, Field
from typing import Optional

class MetaDataPDF(BaseModel):
    filename: str
    title: str
    header: str
    paragraph: str
    idno: str
    application: str
    
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