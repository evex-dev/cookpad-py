from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Image:
    url: str
    id: str = ""
    filename: str = ""
    alt_text: str | None = None


@dataclass
class Ingredient:
    name: str
    quantity: str
    id: int = 0
    headline: bool = False
    sanitized_name: str = ""


@dataclass
class Step:
    description: str
    id: int = 0
    image_url: str | None = None


@dataclass
class User:
    id: int
    name: str
    profile_message: str = ""
    image_url: str | None = None
    recipe_count: int = 0
    follower_count: int = 0
    followee_count: int = 0
    cookpad_id: str = ""
    href: str = ""


@dataclass
class Recipe:
    id: int
    title: str
    story: str = ""
    serving: str = ""
    cooking_time: str | None = None
    published_at: str = ""
    hall_of_fame: bool = False
    cooksnaps_count: int = 0
    image_url: str | None = None
    ingredients: list[Ingredient] = field(default_factory=list)
    user: User | None = None
    # Only available in full recipe detail
    advice: str = ""
    bookmarks_count: int = 0
    view_count: int = 0
    comments_count: int = 0
    steps: list[Step] = field(default_factory=list)
    href: str = ""
    country: str = ""
    language: str = ""
    premium: bool = False


@dataclass
class Comment:
    id: int
    body: str
    created_at: str = ""
    label: str = ""
    user: User | None = None
    image_url: str | None = None
    cursor: str = ""
    likes_count: int = 0
    replies_count: int = 0


@dataclass
class SearchResponse:
    recipes: list[Recipe]
    total_count: int = 0
    next_page: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass
class CommentsResponse:
    comments: list[Comment]
    next_cursor: str | None = None


@dataclass
class UsersResponse:
    users: list[User]
    total_count: int = 0
    next_page: int | None = None


# --- パーサー ---


def parse_image(data: dict[str, Any]) -> Image:
    return Image(
        url=data.get("url", ""),
        id=str(data.get("id", "")),
        filename=data.get("filename", ""),
        alt_text=data.get("alt_text"),
    )


def parse_ingredient(data: dict[str, Any]) -> Ingredient:
    return Ingredient(
        name=data.get("name", ""),
        quantity=data.get("quantity", ""),
        id=data.get("id", 0),
        headline=data.get("headline", False),
        sanitized_name=data.get("sanitized_name", ""),
    )


def parse_step(data: dict[str, Any]) -> Step:
    image_url = None
    for att in data.get("attachments", []):
        if "url" in att:
            image_url = att["url"]
            break
        if img := att.get("image"):
            image_url = img.get("url")
            break
    return Step(
        description=data.get("description", ""),
        id=data.get("id", 0),
        image_url=image_url,
    )


def parse_user(data: dict[str, Any]) -> User:
    image_url = None
    if img := data.get("image"):
        image_url = img.get("url")
    return User(
        id=data.get("id", 0),
        name=data.get("name", ""),
        profile_message=data.get("profile_message", "") or "",
        image_url=image_url,
        recipe_count=data.get("recipe_count", 0),
        follower_count=data.get("follower_count", 0),
        followee_count=data.get("followee_count", 0),
        cookpad_id=data.get("cookpad_id", ""),
        href=data.get("href", ""),
    )


def parse_recipe(data: dict[str, Any]) -> Recipe:
    image_url = None
    if img := data.get("image"):
        image_url = img.get("url")

    user = None
    if user_data := data.get("user"):
        user = parse_user(user_data)

    ingredients = [parse_ingredient(i) for i in data.get("ingredients", [])]
    steps = [parse_step(s) for s in data.get("steps", [])]

    return Recipe(
        id=data.get("id", 0),
        title=data.get("title", ""),
        story=data.get("story", "") or "",
        serving=data.get("serving", "") or "",
        cooking_time=data.get("cooking_time"),
        published_at=data.get("published_at", ""),
        hall_of_fame=data.get("hall_of_fame", False),
        cooksnaps_count=data.get("cooksnaps_count", 0),
        image_url=image_url,
        ingredients=ingredients,
        user=user,
        advice=data.get("advice", "") or "",
        bookmarks_count=data.get("bookmarks_count", 0),
        view_count=data.get("view_count", 0),
        comments_count=data.get("comments_count", 0),
        steps=steps,
        href=data.get("href", ""),
        country=data.get("country", ""),
        language=data.get("language", ""),
        premium=data.get("premium", False),
    )


def parse_comment(data: dict[str, Any]) -> Comment:
    user = None
    if user_data := data.get("user"):
        user = parse_user(user_data)

    image_url = None
    if img := data.get("image"):
        image_url = img.get("url")

    return Comment(
        id=data.get("id", 0),
        body=data.get("body", ""),
        created_at=data.get("created_at", ""),
        label=data.get("label", ""),
        user=user,
        image_url=image_url,
        cursor=data.get("cursor", ""),
        likes_count=data.get("likes_count", 0),
        replies_count=data.get("replies_count", 0),
    )


def parse_search_response(data: dict[str, Any]) -> SearchResponse:
    recipes = [
        parse_recipe(item)
        for item in data.get("result", [])
        if item.get("type") == "search_results/recipe"
    ]

    extra = data.get("extra", {})
    total_count = extra.get("total_count", 0)

    next_page = None
    if next_link := extra.get("links", {}).get("next"):
        next_page = next_link.get("page")

    return SearchResponse(
        recipes=recipes,
        total_count=total_count,
        next_page=next_page,
        raw=data,
    )


def parse_comments_response(data: dict[str, Any]) -> CommentsResponse:
    comments = [parse_comment(c) for c in data.get("result", [])]

    next_cursor = None
    if comments and comments[-1].cursor:
        next_cursor = comments[-1].cursor

    return CommentsResponse(comments=comments, next_cursor=next_cursor)


def parse_users_response(data: dict[str, Any]) -> UsersResponse:
    users = [parse_user(u) for u in data.get("result", [])]

    extra = data.get("extra", {})
    total_count = extra.get("total_count", 0)

    next_page = None
    if next_link := extra.get("links", {}).get("next"):
        next_page = next_link.get("page")

    return UsersResponse(users=users, total_count=total_count, next_page=next_page)
