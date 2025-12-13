"""
API routes for organization management.
Defines all REST endpoints for the service.
"""
from fastapi import APIRouter, Depends, status, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas import (
    OrganizationCreateRequest,
    OrganizationUpdateRequest,
    OrganizationResponse,
    OrganizationDeleteRequest,
    AdminLoginRequest,
    TokenResponse,
    MessageResponse
)
from app.services import OrganizationService
from app.database import get_database_manager, DatabaseManager
from app.security import get_security_manager, SecurityManager

# Create router
router = APIRouter()


def get_organization_service(
    db_manager: DatabaseManager = Depends(get_database_manager),
    security_manager: SecurityManager = Depends(get_security_manager)
) -> OrganizationService:
    """Dependency to get organization service instance."""
    return OrganizationService(db_manager, security_manager)


@router.post(
    "/org/create",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
    description="Creates a new organization with an admin user and dedicated collection"
)
async def create_organization(
    request: OrganizationCreateRequest,
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Create a new organization.
    
    - **organization_name**: Unique name for the organization
    - **email**: Admin email address
    - **password**: Admin password (min 8 characters)
    """
    return await service.create_organization(request)


@router.get(
    "/org/get",
    response_model=OrganizationResponse,
    summary="Get organization details",
    description="Retrieve organization information by name"
)
async def get_organization(
    organization_name: str = Query(..., description="Name of the organization"),
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Get organization details by name.
    
    - **organization_name**: Name of the organization to retrieve
    """
    return await service.get_organization(organization_name)


@router.put(
    "/org/update",
    response_model=OrganizationResponse,
    summary="Update organization",
    description="Update organization name and migrate data to new collection"
)
async def update_organization(
    request: OrganizationUpdateRequest,
    service: OrganizationService = Depends(get_organization_service),
    security_manager: SecurityManager = Depends(get_security_manager),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    """
    Update an organization (authentication required).
    
    - **organization_name**: Current organization name
    - **new_organization_name**: New organization name
    
    Requires admin authentication via Bearer token.
    """
    # Get current user from token
    current_user = await security_manager.get_current_user(credentials)
    return await service.update_organization(request, current_user)


@router.delete(
    "/org/delete",
    response_model=MessageResponse,
    summary="Delete organization",
    description="Delete an organization and all its associated data"
)
async def delete_organization(
    request: OrganizationDeleteRequest,
    service: OrganizationService = Depends(get_organization_service),
    security_manager: SecurityManager = Depends(get_security_manager),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    """
    Delete an organization (authentication required).
    
    - **organization_name**: Name of the organization to delete
    
    Requires admin authentication via Bearer token.
    Only the organization's admin can delete it.
    """
    # Get current user from token
    current_user = await security_manager.get_current_user(credentials)
    result = await service.delete_organization(
        request.organization_name, 
        current_user
    )
    return MessageResponse(
        message=result["message"],
        details={"organization_id": result["organization_id"]}
    )


@router.post(
    "/admin/login",
    response_model=TokenResponse,
    summary="Admin login",
    description="Authenticate admin and receive JWT token"
)
async def admin_login(
    request: AdminLoginRequest,
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Admin login endpoint.
    
    - **email**: Admin email address
    - **password**: Admin password
    
    Returns a JWT token for authenticated requests.
    """
    return await service.admin_login(request)
