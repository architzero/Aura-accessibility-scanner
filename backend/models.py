from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    PlainSerializer,
    WithJsonSchema,
)
from typing import List, Optional, Annotated
from datetime import datetime
from bson import ObjectId

# This is the modern and simplest Pydantic V2 way to handle ObjectIds.
# 1. We tell Pydantic the core type is ObjectId.
# 2. PlainSerializer(str) converts the ObjectId to a string for JSON output.
# 3. WithJsonSchema tells the API docs (Swagger/OpenAPI) to treat it as a string.
PyObjectId = Annotated[
    ObjectId,
    PlainSerializer(lambda v: str(v), return_type=str),
    WithJsonSchema({"type": "string", "example": "60d5ec49e7b2e3b2e3f1b3a1"}),
]

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    auth_provider: str = "jwt"

class User(UserBase):
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime

    # Pydantic V2 uses model_config instead of class Config
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class ProjectBase(BaseModel):
    projectName: str
    url: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: PyObjectId = Field(alias="_id")
    userId: PyObjectId
    createdAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class AccessibilityIssue(BaseModel):
    element: str  # e.g., "<img src='logo.png'>"
    description: str # e.g., "Image is missing an alt attribute."
    guideline: str # e.g., "WCAG 1.1.1"

class ScanResult(BaseModel):
    id: PyObjectId = Field(alias="_id")
    projectId: PyObjectId
    scanType: str = "live"
    accessibilityScore: int
    issues: List[AccessibilityIssue]
    genericSuggestions: List[str] = []
    aiSuggestions: List[str] = []
    screenshotUrl: str
    createdAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
