from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    PlainSerializer,
    WithJsonSchema,
    field_validator,
    HttpUrl,
)
from typing import List, Optional, Annotated
from datetime import datetime
from bson import ObjectId

# Modern Pydantic V2 way to handle ObjectIds
PyObjectId = Annotated[
    ObjectId,
    PlainSerializer(lambda v: str(v), return_type=str),
    WithJsonSchema({"type": "string", "example": "60d5ec49e7b2e3b2e3f1b3a1"}),
]

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    auth_provider: str = "jwt"
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class User(UserBase):
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class ProjectBase(BaseModel):
    projectName: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., max_length=2048)
    
    @field_validator('projectName')
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()

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
    element: str
    description: str
    guideline: str

class ScanResult(BaseModel):
    id: PyObjectId = Field(alias="_id")
    projectId: PyObjectId
    scanType: str = "live"
    accessibilityScore: int = Field(..., ge=0, le=100)
    issues: List[AccessibilityIssue]
    genericSuggestions: List[str] = []
    aiSuggestions: List[str] = []
    screenshotUrl: str
    createdAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
