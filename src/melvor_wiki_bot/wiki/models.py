from dataclasses import dataclass
from typing import List, Optional


@dataclass
class WikiSection:
    heading_level: int
    heading_id: Optional[str]
    heading_text: Optional[str]
    html: str
    plain_text: str


@dataclass
class WikiTable:
    kind: str
    section_heading_id: Optional[str]
    html: str


@dataclass
class WikiPageStructured:
    page_id: str
    page_title: str
    url: str
    last_updated_version: Optional[str]
    sections: List[WikiSection]
    tables: List[WikiTable]
