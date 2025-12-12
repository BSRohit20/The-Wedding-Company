"""
Database models representing the structure of documents in MongoDB.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class OrganizationModel(BaseModel):
    """Model representing an organization in the master database."""
    organization_id: str
    organization_name: str
    collection_name: str
    admin_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AdminUserModel(BaseModel):
    """Model representing an admin user in the master database."""
    admin_id: str
    email: EmailStr
    hashed_password: str
    organization_id: str
    created_at: datetime
    is_active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
