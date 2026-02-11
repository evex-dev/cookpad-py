"""Unit tests for type parsing functions.

These tests don't hit the API - they test parsing logic with mock data.
Run with: pytest tests/test_types.py -v
"""

from __future__ import annotations

from cookpad.types import (
    Comment,
    CommentsResponse,
    Image,
    Ingredient,
    Recipe,
    SearchResponse,
    Step,
    User,
    UsersResponse,
    parse_comment,
    parse_image,
    parse_ingredient,
    parse_recipe,
    parse_search_response,
    parse_step,
    parse_user,
    parse_users_response,
    parse_comments_response,
)


def test_parse_image():
    data = {
        "type": "images/image",
        "id": "12345",
        "filename": "photo.jpg",
        "alt_text": "A photo",
        "url": "https://example.com/photo.jpg",
    }
    img = parse_image(data)
    assert isinstance(img, Image)
    assert img.url == "https://example.com/photo.jpg"
    assert img.id == "12345"
    assert img.filename == "photo.jpg"
    assert img.alt_text == "A photo"


def test_parse_image_minimal():
    img = parse_image({})
    assert img.url == ""
    assert img.id == ""


def test_parse_ingredient():
    data = {
        "type": "ingredient",
        "id": 100,
        "name": "鶏もも肉",
        "quantity": "200g",
        "headline": False,
        "sanitized_name": "鶏もも肉",
    }
    ing = parse_ingredient(data)
    assert isinstance(ing, Ingredient)
    assert ing.name == "鶏もも肉"
    assert ing.quantity == "200g"
    assert ing.id == 100


def test_parse_step():
    data = {
        "type": "step",
        "id": 1,
        "description": "Cut the vegetables.",
        "attachments": [],
    }
    step = parse_step(data)
    assert isinstance(step, Step)
    assert step.description == "Cut the vegetables."
    assert step.image_url is None


def test_parse_step_with_image():
    data = {
        "type": "step",
        "id": 2,
        "description": "Fry it.",
        "attachments": [{"image": {"url": "https://example.com/step.jpg"}}],
    }
    step = parse_step(data)
    assert step.image_url == "https://example.com/step.jpg"


def test_parse_user():
    data = {
        "type": "user",
        "id": 12345,
        "name": "TestUser",
        "profile_message": "Hello",
        "recipe_count": 10,
        "follower_count": 5,
        "followee_count": 3,
        "cookpad_id": "cook_12345",
        "href": "https://cookpad.com/jp/users/12345",
        "image": {"url": "https://example.com/avatar.jpg"},
    }
    user = parse_user(data)
    assert isinstance(user, User)
    assert user.id == 12345
    assert user.name == "TestUser"
    assert user.image_url == "https://example.com/avatar.jpg"
    assert user.recipe_count == 10


def test_parse_user_null_profile():
    data = {"id": 1, "name": "X", "profile_message": None}
    user = parse_user(data)
    assert user.profile_message == ""


def test_parse_recipe_summary():
    data = {
        "type": "search_results/recipe",
        "id": 99999,
        "title": "テストレシピ",
        "story": "おいしい",
        "serving": "2人分",
        "cooking_time": None,
        "published_at": "2026-01-01T00:00:00Z",
        "hall_of_fame": True,
        "cooksnaps_count": 42,
        "image": {"url": "https://example.com/recipe.jpg"},
        "ingredients": [
            {"name": "卵", "quantity": "2個", "id": 1},
        ],
        "user": {"id": 1, "name": "Chef"},
    }
    recipe = parse_recipe(data)
    assert isinstance(recipe, Recipe)
    assert recipe.id == 99999
    assert recipe.title == "テストレシピ"
    assert recipe.hall_of_fame is True
    assert recipe.cooksnaps_count == 42
    assert recipe.image_url == "https://example.com/recipe.jpg"
    assert len(recipe.ingredients) == 1
    assert recipe.user is not None
    assert recipe.user.name == "Chef"


def test_parse_recipe_full_detail():
    data = {
        "id": 100,
        "title": "Full Recipe",
        "story": "A story",
        "serving": "4人分",
        "advice": "Some advice",
        "bookmarks_count": 10,
        "view_count": 500,
        "comments_count": 3,
        "href": "https://cookpad.com/jp/recipes/100",
        "country": "JP",
        "language": "ja",
        "premium": False,
        "steps": [
            {"id": 1, "description": "Step 1", "attachments": []},
            {"id": 2, "description": "Step 2", "attachments": []},
        ],
        "ingredients": [],
    }
    recipe = parse_recipe(data)
    assert recipe.advice == "Some advice"
    assert recipe.bookmarks_count == 10
    assert len(recipe.steps) == 2
    assert recipe.steps[0].description == "Step 1"
    assert recipe.href == "https://cookpad.com/jp/recipes/100"


def test_parse_comment():
    data = {
        "type": "comment",
        "id": 555,
        "body": "Looks great!",
        "created_at": "2026-01-01T00:00:00Z",
        "label": "cooksnap",
        "cursor": "abc123",
        "likes_count": 3,
        "replies_count": 1,
        "user": {"id": 1, "name": "Commenter"},
        "image": {"url": "https://example.com/snap.jpg"},
    }
    comment = parse_comment(data)
    assert isinstance(comment, Comment)
    assert comment.id == 555
    assert comment.body == "Looks great!"
    assert comment.cursor == "abc123"
    assert comment.user is not None
    assert comment.image_url == "https://example.com/snap.jpg"


def test_parse_search_response():
    data = {
        "result": [
            {"type": "search_results/premium_banner", "result": []},
            {"type": "search_results/title", "title": "新着順"},
            {"type": "search_results/recipe", "id": 1, "title": "Recipe 1"},
            {"type": "search_results/recipe", "id": 2, "title": "Recipe 2"},
        ],
        "extra": {
            "total_count": 100,
            "links": {"prev": None, "next": {"href": "...", "page": 2}},
        },
    }
    resp = parse_search_response(data)
    assert isinstance(resp, SearchResponse)
    assert len(resp.recipes) == 2
    assert resp.recipes[0].id == 1
    assert resp.recipes[1].id == 2
    assert resp.total_count == 100
    assert resp.next_page == 2
    assert resp.raw == data


def test_parse_search_response_empty():
    data = {"result": [], "extra": {"total_count": 0, "links": {}}}
    resp = parse_search_response(data)
    assert resp.recipes == []
    assert resp.total_count == 0
    assert resp.next_page is None


def test_parse_comments_response():
    data = {
        "result": [
            {"id": 1, "body": "Nice", "cursor": "cur1"},
            {"id": 2, "body": "Great", "cursor": "cur2"},
        ]
    }
    resp = parse_comments_response(data)
    assert isinstance(resp, CommentsResponse)
    assert len(resp.comments) == 2
    assert resp.next_cursor == "cur2"


def test_parse_comments_response_empty():
    resp = parse_comments_response({"result": []})
    assert resp.comments == []
    assert resp.next_cursor is None


def test_parse_users_response():
    data = {
        "result": [
            {"id": 1, "name": "User1"},
            {"id": 2, "name": "User2"},
        ],
        "extra": {
            "total_count": 50,
            "links": {"next": {"page": 2}},
        },
    }
    resp = parse_users_response(data)
    assert isinstance(resp, UsersResponse)
    assert len(resp.users) == 2
    assert resp.total_count == 50
    assert resp.next_page == 2
