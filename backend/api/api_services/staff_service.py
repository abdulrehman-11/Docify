"""
Staff service for API
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Dict
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.staff import Staff
import bcrypt


class StaffService:
    """Service for managing staff members"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    async def create_staff(
        self,
        name: str,
        email: str,
        password: str,
        role: str = "staff",
        permissions: Dict[str, bool] = None,
        created_by: Optional[int] = None
    ) -> Staff:
        """Create a new staff member"""
        # Check if email already exists
        result = await self.db.execute(
            select(Staff).where(Staff.email == email)
        )
        if result.scalar_one_or_none():
            raise ValueError(f"Staff member with email {email} already exists")

        # Hash password
        password_hash = self.hash_password(password)

        # Create staff
        staff = Staff(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            permissions=permissions or {},
            created_by=created_by
        )
        
        self.db.add(staff)
        await self.db.flush()
        return staff

    async def get_staff_by_id(self, staff_id: int) -> Optional[Staff]:
        """Get a staff member by ID"""
        result = await self.db.execute(
            select(Staff).where(Staff.id == staff_id)
        )
        return result.scalar_one_or_none()

    async def get_staff_by_email(self, email: str) -> Optional[Staff]:
        """Get a staff member by email"""
        result = await self.db.execute(
            select(Staff).where(Staff.email == email)
        )
        return result.scalar_one_or_none()

    async def list_staff(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> tuple[list[Staff], int]:
        """List all staff members with pagination"""
        query = select(Staff)
        
        if is_active is not None:
            query = query.where(Staff.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(Staff)
        if is_active is not None:
            count_query = count_query.where(Staff.is_active == is_active)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Staff.created_at.desc())
        result = await self.db.execute(query)
        staff_list = result.scalars().all()

        return list(staff_list), total

    async def update_staff(
        self,
        staff_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[str] = None,
        permissions: Optional[Dict[str, bool]] = None,
        is_active: Optional[bool] = None
    ) -> Staff:
        """Update a staff member"""
        staff = await self.get_staff_by_id(staff_id)
        if not staff:
            raise ValueError(f"Staff member with id {staff_id} not found")

        # Check if new email already exists
        if email and email != staff.email:
            existing = await self.get_staff_by_email(email)
            if existing:
                raise ValueError(f"Staff member with email {email} already exists")
            staff.email = email

        if name:
            staff.name = name
        if password:
            staff.password_hash = self.hash_password(password)
        if role:
            staff.role = role
        if permissions is not None:
            staff.permissions = permissions
        if is_active is not None:
            staff.is_active = is_active

        await self.db.flush()
        return staff

    async def delete_staff(self, staff_id: int) -> bool:
        """Delete a staff member (soft delete by setting is_active=False)"""
        staff = await self.get_staff_by_id(staff_id)
        if not staff:
            raise ValueError(f"Staff member with id {staff_id} not found")

        staff.is_active = False
        await self.db.flush()
        return True

    async def authenticate_staff(self, email: str, password: str) -> Optional[Staff]:
        """Authenticate a staff member"""
        staff = await self.get_staff_by_email(email)
        if not staff:
            return None
        
        if not staff.is_active:
            return None

        if not self.verify_password(password, staff.password_hash):
            return None

        return staff
