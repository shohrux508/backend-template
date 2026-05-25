from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.services.item import ItemCreate, ItemResponse, ItemService, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    obj_in: ItemCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ItemResponse:
    """Create a new item."""
    service = ItemService(session)
    item = await service.create(obj_in)
    return ItemResponse.model_validate(item)


@router.get("/", response_model=list[ItemResponse])
async def read_items(
    session: Annotated[AsyncSession, Depends(get_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[ItemResponse]:
    """Retrieve items with pagination."""
    service = ItemService(session)
    items = await service.get_multi(skip=skip, limit=limit)
    return [ItemResponse.model_validate(item) for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ItemResponse:
    """Get item by ID."""
    service = ItemService(session)
    item = await service.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return ItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    obj_in: ItemUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ItemResponse:
    """Update an item."""
    service = ItemService(session)
    item = await service.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    updated_item = await service.update(item, obj_in)
    return ItemResponse.model_validate(updated_item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete an item."""
    service = ItemService(session)
    item = await service.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    await service.delete(item)
