# src/storage/schema.py
from pydantic import BaseModel
from typing import List, Optional

class Victim(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None

class AccidentRecord(BaseModel):
    date: str
    time: Optional[str]
    mine: Optional[str]
    owner: Optional[str]
    district: Optional[str]
    state: Optional[str]
    code: Optional[str]
    cause: Optional[str]
    narrative: Optional[str]
    prevention: Optional[str]
    persons_killed: int
    victims: List[Victim]
    source_doc: str
    page_span: List[int]
