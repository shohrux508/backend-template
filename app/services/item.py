from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.database.models import Item

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ItemBase(BaseModel):
    """Base fields for Item schema."""

    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    """Schema for creating an Item."""

    pass


class ItemUpdate(BaseModel):
    """Schema for updating an Item. All fields are optional."""

    title: str | None = None
    description: str | None = None


class ItemResponse(ItemBase):
    """Schema for serializing Item responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ItemService:
    """Service to handle business logic for Items."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, obj_in: ItemCreate) -> Item:
        """Create a new item in the database."""
        db_obj = Item(
            title=obj_in.title,
            description=obj_in.description,
        )
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, item_id: int) -> Item | None:
        """Retrieve an item by its ID."""
        result = await self.session.execute(select(Item).where(Item.id == item_id))
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[Item]:
        """Retrieve a list of items with pagination."""
        result = await self.session.execute(select(Item).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(self, db_obj: Item, obj_in: ItemUpdate) -> Item:
        """Update an existing item's fields."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Item) -> None:
        """Delete an item from the database."""
        await self.session.delete(db_obj)
        await self.session.commit()
