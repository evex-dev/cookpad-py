"""Integration tests for Cookpad API client.

These tests hit the real API with the anonymous token.
Run with: pytest tests/ -v
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from cookpad import (
    Cookpad,
    Comment,
    CommentsResponse,
    Ingredient,
    NotFoundError,
    Recipe,
    SearchResponse,
    Step,
    User,
    UsersResponse,
)


@pytest_asyncio.fixture
async def client():
    async with Cookpad() as c:
        yield c


# --- search_recipes ---


@pytest.mark.asyncio
async def test_search_recipes_basic(client: Cookpad):
    results = await client.search_recipes("カレー", per_page=5)
    assert isinstance(results, SearchResponse)
    assert results.total_count > 0
    assert len(results.recipes) > 0
    assert results.next_page is not None


@pytest.mark.asyncio
async def test_search_recipes_recipe_fields(client: Cookpad):
    results = await client.search_recipes("カレー", per_page=1)
    recipe = results.recipes[0]
    assert isinstance(recipe, Recipe)
    assert recipe.id > 0
    assert recipe.title
    assert recipe.published_at
    assert recipe.user is not None
    assert isinstance(recipe.user, User)


@pytest.mark.asyncio
async def test_search_recipes_order_popular(client: Cookpad):
    results = await client.search_recipes("パスタ", order="popular", per_page=3)
    assert isinstance(results, SearchResponse)
    assert len(results.recipes) > 0


@pytest.mark.asyncio
async def test_search_recipes_excluded_ingredients(client: Cookpad):
    results = await client.search_recipes(
        "カレー", excluded_ingredients="トマト", per_page=3
    )
    assert isinstance(results, SearchResponse)
    assert results.total_count > 0


@pytest.mark.asyncio
async def test_search_recipes_pagination(client: Cookpad):
    page1 = await client.search_recipes("サラダ", page=1, per_page=5)
    assert page1.next_page == 2
    page2 = await client.search_recipes("サラダ", page=2, per_page=5)
    assert len(page2.recipes) > 0
    # Different pages should return different recipes
    ids1 = {r.id for r in page1.recipes}
    ids2 = {r.id for r in page2.recipes}
    assert ids1 != ids2


@pytest.mark.asyncio
async def test_search_recipes_raw_access(client: Cookpad):
    results = await client.search_recipes("ラーメン", per_page=1)
    assert "result" in results.raw
    assert "extra" in results.raw


# --- get_recipe ---


@pytest.mark.asyncio
async def test_get_recipe(client: Cookpad):
    recipe = await client.get_recipe(25410768)
    assert isinstance(recipe, Recipe)
    assert recipe.id == 25410768
    assert recipe.title
    assert recipe.serving
    assert recipe.href


@pytest.mark.asyncio
async def test_get_recipe_has_steps(client: Cookpad):
    recipe = await client.get_recipe(25410768)
    assert len(recipe.steps) > 0
    step = recipe.steps[0]
    assert isinstance(step, Step)
    assert step.description


@pytest.mark.asyncio
async def test_get_recipe_has_ingredients(client: Cookpad):
    recipe = await client.get_recipe(25410768)
    assert len(recipe.ingredients) > 0
    ing = recipe.ingredients[0]
    assert isinstance(ing, Ingredient)
    assert ing.name
    assert ing.quantity


@pytest.mark.asyncio
async def test_get_recipe_has_user(client: Cookpad):
    recipe = await client.get_recipe(25410768)
    assert recipe.user is not None
    assert isinstance(recipe.user, User)
    assert recipe.user.id > 0
    assert recipe.user.name


@pytest.mark.asyncio
async def test_get_recipe_not_found(client: Cookpad):
    with pytest.raises(NotFoundError):
        await client.get_recipe(999999999)


# --- get_similar_recipes ---


@pytest.mark.asyncio
async def test_get_similar_recipes(client: Cookpad):
    similar = await client.get_similar_recipes(25410768, per_page=5)
    assert isinstance(similar, list)
    assert len(similar) > 0
    assert isinstance(similar[0], Recipe)
    assert similar[0].id > 0
    assert similar[0].title


# --- get_comments ---


@pytest.mark.asyncio
async def test_get_comments(client: Cookpad):
    result = await client.get_comments(18510866, limit=3)
    assert isinstance(result, CommentsResponse)
    assert len(result.comments) > 0


@pytest.mark.asyncio
async def test_get_comments_fields(client: Cookpad):
    result = await client.get_comments(18510866, limit=3)
    comment = result.comments[0]
    assert isinstance(comment, Comment)
    assert comment.id > 0
    assert comment.body
    assert comment.created_at
    assert comment.user is not None
    assert isinstance(comment.user, User)


@pytest.mark.asyncio
async def test_get_comments_cursor_pagination(client: Cookpad):
    result = await client.get_comments(18510866, limit=3)
    assert result.next_cursor is not None
    # Fetch next page
    result2 = await client.get_comments(18510866, limit=3, after=result.next_cursor)
    assert len(result2.comments) > 0
    # Different comments
    ids1 = {c.id for c in result.comments}
    ids2 = {c.id for c in result2.comments}
    assert ids1 != ids2


# --- search_users ---


@pytest.mark.asyncio
async def test_search_users(client: Cookpad):
    result = await client.search_users("test", per_page=5)
    assert isinstance(result, UsersResponse)
    assert result.total_count > 0
    assert len(result.users) > 0


@pytest.mark.asyncio
async def test_search_users_fields(client: Cookpad):
    result = await client.search_users("test", per_page=1)
    user = result.users[0]
    assert isinstance(user, User)
    assert user.id > 0
    assert user.name
    assert user.cookpad_id


# --- search_keywords ---


@pytest.mark.asyncio
async def test_search_keywords(client: Cookpad):
    result = await client.search_keywords("カレ")
    assert isinstance(result, dict)
    assert "search_query" in result


@pytest.mark.asyncio
async def test_search_keywords_empty(client: Cookpad):
    result = await client.search_keywords("")
    assert isinstance(result, dict)


# --- get_search_history ---


@pytest.mark.asyncio
async def test_get_search_history(client: Cookpad):
    result = await client.get_search_history()
    assert isinstance(result, dict)
    assert "result" in result


# --- context manager ---


@pytest.mark.asyncio
async def test_context_manager():
    async with Cookpad() as client:
        results = await client.search_recipes("test", per_page=1)
        assert len(results.recipes) >= 0


@pytest.mark.asyncio
async def test_without_context_manager():
    """Client should auto-create httpx client if not using context manager."""
    client = Cookpad()
    results = await client.search_recipes("test", per_page=1)
    assert isinstance(results, SearchResponse)
