"""
Business logic layer for organization management.
Handles all organization-related operations with proper separation of concerns.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from fastapi import HTTPException, status
from app.database import DatabaseManager
from app.security import SecurityManager
from app.models import OrganizationModel, AdminUserModel
from app.schemas import (
    OrganizationCreateRequest,
    OrganizationUpdateRequest,
    OrganizationResponse,
    AdminLoginRequest,
    TokenResponse
)


class OrganizationService:
    """Service class for organization management operations."""
    
    def __init__(
        self, 
        db_manager: DatabaseManager, 
        security_manager: SecurityManager
    ):
        self.db = db_manager
        self.security = security_manager
        self.organizations_collection = "organizations"
        self.admins_collection = "admins"
    
    async def create_organization(
        self, 
        request: OrganizationCreateRequest
    ) -> OrganizationResponse:
        """
        Create a new organization with its admin user.
        
        Args:
            request: Organization creation request data
            
        Returns:
            Created organization details
            
        Raises:
            HTTPException: If organization already exists
        """
        master_db = self.db.get_master_db()
        
        # Check if organization already exists
        existing_org = await master_db[self.organizations_collection].find_one(
            {"organization_name": request.organization_name}
        )
        
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization '{request.organization_name}' already exists"
            )
        
        # Check if admin email already exists
        existing_admin = await master_db[self.admins_collection].find_one(
            {"email": request.email}
        )
        
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Admin with email '{request.email}' already exists"
            )
        
        # Generate unique IDs
        organization_id = str(uuid4())
        admin_id = str(uuid4())
        collection_name = f"org_{request.organization_name}"
        
        # Hash password
        hashed_password = self.security.hash_password(request.password)
        
        # Create admin user document
        admin_data = AdminUserModel(
            admin_id=admin_id,
            email=request.email,
            hashed_password=hashed_password,
            organization_id=organization_id,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        # Create organization document
        organization_data = OrganizationModel(
            organization_id=organization_id,
            organization_name=request.organization_name,
            collection_name=collection_name,
            admin_id=admin_id,
            created_at=datetime.utcnow()
        )
        
        # Store in master database
        await master_db[self.admins_collection].insert_one(
            admin_data.dict()
        )
        await master_db[self.organizations_collection].insert_one(
            organization_data.dict()
        )
        
        # Create dynamic collection for the organization
        await self.db.create_organization_collection(collection_name)
        
        # Initialize the organization collection with metadata
        org_collection = self.db.get_organization_collection(collection_name)
        await org_collection.insert_one({
            "type": "metadata",
            "organization_id": organization_id,
            "created_at": datetime.utcnow(),
            "description": f"Data collection for {request.organization_name}"
        })
        
        return OrganizationResponse(
            organization_id=organization_id,
            organization_name=request.organization_name,
            collection_name=collection_name,
            admin_email=request.email,
            created_at=organization_data.created_at
        )
    
    async def get_organization(
        self, 
        organization_name: str
    ) -> OrganizationResponse:
        """
        Retrieve organization details by name.
        
        Args:
            organization_name: Name of the organization
            
        Returns:
            Organization details
            
        Raises:
            HTTPException: If organization not found
        """
        master_db = self.db.get_master_db()
        
        organization = await master_db[self.organizations_collection].find_one(
            {"organization_name": organization_name}
        )
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{organization_name}' not found"
            )
        
        # Get admin details
        admin = await master_db[self.admins_collection].find_one(
            {"admin_id": organization["admin_id"]}
        )
        
        return OrganizationResponse(
            organization_id=organization["organization_id"],
            organization_name=organization["organization_name"],
            collection_name=organization["collection_name"],
            admin_email=admin["email"] if admin else "N/A",
            created_at=organization["created_at"],
            updated_at=organization.get("updated_at")
        )
    
    async def update_organization(
        self, 
        request: OrganizationUpdateRequest,
        current_user: dict
    ) -> OrganizationResponse:
        """
        Update organization name and migrate data to new collection.
        
        Args:
            request: Organization update request data
            current_user: Current authenticated user
            
        Returns:
            Updated organization details
            
        Raises:
            HTTPException: If organization not found or update fails
        """
        master_db = self.db.get_master_db()
        
        # Verify current organization exists
        current_org = await master_db[self.organizations_collection].find_one(
            {"organization_name": request.organization_name}
        )
        
        if not current_org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{request.organization_name}' not found"
            )
        
        # Verify user is admin of this organization
        if current_user["organization_id"] != current_org["organization_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this organization"
            )
        
        # Check if new name already exists
        if request.organization_name != request.new_organization_name:
            existing_org = await master_db[self.organizations_collection].find_one(
                {"organization_name": request.new_organization_name}
            )
            
            if existing_org:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Organization '{request.new_organization_name}' already exists"
                )
        
        old_collection_name = current_org["collection_name"]
        new_collection_name = f"org_{request.new_organization_name}"
        
        # Create new collection
        await self.db.create_organization_collection(new_collection_name)
        
        # Migrate data from old collection to new collection
        old_collection = self.db.get_organization_collection(old_collection_name)
        new_collection = self.db.get_organization_collection(new_collection_name)
        
        # Copy all documents
        async for document in old_collection.find():
            await new_collection.insert_one(document)
        
        # Update organization record
        await master_db[self.organizations_collection].update_one(
            {"organization_id": current_org["organization_id"]},
            {
                "$set": {
                    "organization_name": request.new_organization_name,
                    "collection_name": new_collection_name,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Delete old collection
        await self.db.delete_organization_collection(old_collection_name)
        
        # Get admin details
        admin = await master_db[self.admins_collection].find_one(
            {"admin_id": current_org["admin_id"]}
        )
        
        return OrganizationResponse(
            organization_id=current_org["organization_id"],
            organization_name=request.new_organization_name,
            collection_name=new_collection_name,
            admin_email=admin["email"] if admin else "N/A",
            created_at=current_org["created_at"],
            updated_at=datetime.utcnow()
        )
    
    async def delete_organization(
        self, 
        organization_name: str,
        current_user: dict
    ) -> dict:
        """
        Delete an organization and its associated data.
        
        Args:
            organization_name: Name of the organization to delete
            current_user: Current authenticated user
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If organization not found or user unauthorized
        """
        master_db = self.db.get_master_db()
        
        # Find organization
        organization = await master_db[self.organizations_collection].find_one(
            {"organization_name": organization_name}
        )
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{organization_name}' not found"
            )
        
        # Verify user is admin of this organization
        if current_user["organization_id"] != organization["organization_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this organization"
            )
        
        # Delete organization collection
        await self.db.delete_organization_collection(
            organization["collection_name"]
        )
        
        # Delete admin user
        await master_db[self.admins_collection].delete_one(
            {"admin_id": organization["admin_id"]}
        )
        
        # Delete organization record
        await master_db[self.organizations_collection].delete_one(
            {"organization_id": organization["organization_id"]}
        )
        
        return {
            "message": f"Organization '{organization_name}' successfully deleted",
            "organization_id": organization["organization_id"]
        }
    
    async def admin_login(
        self, 
        request: AdminLoginRequest
    ) -> TokenResponse:
        """
        Authenticate admin and generate JWT token.
        
        Args:
            request: Login credentials
            
        Returns:
            JWT token and user details
            
        Raises:
            HTTPException: If authentication fails
        """
        master_db = self.db.get_master_db()
        
        # Find admin by email
        admin = await master_db[self.admins_collection].find_one(
            {"email": request.email}
        )
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not self.security.verify_password(
            request.password, 
            admin["hashed_password"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if admin is active
        if not admin.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive"
            )
        
        # Get organization details
        organization = await master_db[self.organizations_collection].find_one(
            {"organization_id": admin["organization_id"]}
        )
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this admin"
            )
        
        # Create JWT token
        token_data = {
            "admin_id": admin["admin_id"],
            "email": admin["email"],
            "organization_id": admin["organization_id"],
            "organization_name": organization["organization_name"]
        }
        
        access_token = self.security.create_access_token(data=token_data)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            organization_name=organization["organization_name"],
            admin_email=admin["email"]
        )
