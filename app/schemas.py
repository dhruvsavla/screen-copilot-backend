# app/schemas.py
from pydantic import BaseModel
from typing import List

# --- Steps ---
class StepBase(BaseModel):
    selector: str
    instruction: str
# ... (rest of Step classes are unchanged)
class StepCreate(StepBase):
    pass

class Step(StepBase):
    id: int
    step_number: int
    guide_id: int
    
    class Config:
        from_attributes = True

# --- Guides ---
class GuideBase(BaseModel):
    name: str
    shortcut: str
    description: str  # <-- ADD THIS LINE

class GuideCreate(GuideBase):
    steps: List[StepCreate]

class Guide(GuideBase):
    id: int
    owner_id: int
    steps: List[Step] = []

    class Config:
        from_attributes = True

# --- Users ---
# ... (no changes in User classes)
class UserCreate(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: int
    email: str
    guides: List[Guide] = []

    class Config:
        from_attributes = True