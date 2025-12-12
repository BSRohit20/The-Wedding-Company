"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class OrganizationCreateRequest(BaseModel):
    """Request model for creating an organization."""
    organization_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('organization_name')
    def validate_organization_name(cls, v):
        """Ensure organization name contains only alphanumeric and underscores."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Organization name must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower().replace(' ', '_').replace('-', '_')


class OrganizationUpdateRequest(BaseModel):
    """Request model for updating an organization."""
    organization_name: str = Field(..., min_length=3, max_length=50)
    new_organization_name: str = Field(..., min_length=3, max_length=50)
    
    @validator('organization_name', 'new_organization_name')
    def validate_organization_name(cls, v):
        """Ensure organization name contains only alphanumeric and underscores."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Organization name must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower().replace(' ', '_').replace('-', '_')


class OrganizationResponse(BaseModel):
    """Response model for organization details."""
    organization_id: str
    organization_name: str
    collection_name: str
    admin_email: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class AdminLoginRequest(BaseModel):
    """Request model for admin login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication token."""
    access_token: str
    token_type: str = "bearer"
    organization_name: str
    admin_email: str


class OrganizationDeleteRequest(BaseModel):
    """Request model for deleting an organization."""
    organization_name: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    details: Optional[dict] = None
