from __future__ import annotations

from httpx import AsyncClient


async def test_create_item(client: AsyncClient) -> None:
    """Test creating a new item."""
    data = {"title": "Test Item", "description": "Test Description"}
    response = await client.post("/api/v1/items/", json=data)
    assert response.status_code == 201
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content


async def test_read_item(client: AsyncClient) -> None:
    """Test reading an existing item."""
    # Create the item first
    data = {"title": "Find Me", "description": "Some description"}
    post_res = await client.post("/api/v1/items/", json=data)
    item_id = post_res.json()["id"]

    # Read the item
    response = await client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == item_id


async def test_read_item_not_found(client: AsyncClient) -> None:
    """Test reading a non-existent item returns 404."""
    response = await client.get("/api/v1/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


async def test_read_items(client: AsyncClient) -> None:
    """Test reading a list of items."""
    # Create multiple items
    item1 = {"title": "Item 1", "description": "Desc 1"}
    item2 = {"title": "Item 2", "description": "Desc 2"}
    await client.post("/api/v1/items/", json=item1)
    await client.post("/api/v1/items/", json=item2)

    response = await client.get("/api/v1/items/")
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 2
    titles = [item["title"] for item in content]
    assert "Item 1" in titles
    assert "Item 2" in titles


async def test_update_item(client: AsyncClient) -> None:
    """Test updating an item."""
    # Create the item first
    data = {"title": "Original Title", "description": "Original Desc"}
    post_res = await client.post("/api/v1/items/", json=data)
    item_id = post_res.json()["id"]

    # Update title only
    update_data = {"title": "Updated Title"}
    response = await client.put(f"/api/v1/items/{item_id}", json=update_data)
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == "Updated Title"
    assert content["description"] == "Original Desc"  # description remains unchanged


async def test_update_item_not_found(client: AsyncClient) -> None:
    """Test updating a non-existent item returns 404."""
    response = await client.put("/api/v1/items/999", json={"title": "New Title"})
    assert response.status_code == 404


async def test_delete_item(client: AsyncClient) -> None:
    """Test deleting an item."""
    # Create the item first
    data = {"title": "To Delete", "description": "Soon gone"}
    post_res = await client.post("/api/v1/items/", json=data)
    item_id = post_res.json()["id"]

    # Delete the item
    response = await client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 204

    # Verify item is deleted
    get_res = await client.get(f"/api/v1/items/{item_id}")
    assert get_res.status_code == 404


async def test_delete_item_not_found(client: AsyncClient) -> None:
    """Test deleting a non-existent item returns 404."""
    response = await client.delete("/api/v1/items/999")
    assert response.status_code == 404
