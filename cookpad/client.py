from __future__ import annotations

import json
import uuid
from typing import Any, Literal

import httpx

from .constants import (
    API_HOST,
    BASE_URL,
    DEFAULT_COUNTRY,
    DEFAULT_LANGUAGE,
    DEFAULT_PROVIDER_ID,
    DEFAULT_TIMEZONE_ID,
    DEFAULT_TIMEZONE_OFFSET,
    DEFAULT_TOKEN,
    DEFAULT_USER_AGENT,
    SUPPORTED_SEARCH_TYPES,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)
from .types import (
    CommentsResponse,
    Recipe,
    SearchResponse,
    UsersResponse,
    parse_comments_response,
    parse_recipe,
    parse_search_response,
    parse_users_response,
)


class Cookpad:
    """Cookpad API async client.

    Usage::

        async with Cookpad() as client:
            results = await client.search_recipes("カレー")
            for recipe in results.recipes:
                print(recipe.title)
    """

    def __init__(
        self,
        *,
        token: str = DEFAULT_TOKEN,
        country: str = DEFAULT_COUNTRY,
        language: str = DEFAULT_LANGUAGE,
        timezone_id: str = DEFAULT_TIMEZONE_ID,
        timezone_offset: str = DEFAULT_TIMEZONE_OFFSET,
        user_agent: str = DEFAULT_USER_AGENT,
        provider_id: str = DEFAULT_PROVIDER_ID,
    ) -> None:
        self._token = token
        self._country = country
        self._language = language
        self._timezone_id = timezone_id
        self._timezone_offset = timezone_offset
        self._user_agent = user_agent
        self._provider_id = provider_id
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Cookpad:
        self._client = httpx.AsyncClient()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _headers(self) -> dict[str, str]:
        return {
            "Host": API_HOST,
            "Authorization": f"Bearer {self._token}",
            "X-Cookpad-Country-Selected": self._country,
            "X-Cookpad-Timezone-Id": self._timezone_id,
            "X-Cookpad-Provider-Id": self._provider_id,
            "X-Cookpad-Timezone-Offset": self._timezone_offset,
            "X-Cookpad-Guid": str(uuid.uuid4()).upper(),
            "Accept-Encoding": "gzip",
            "Accept-Language": self._language,
            "Accept": "*/*",
            "User-Agent": self._user_agent,
        }

    async def _request(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if self._client is None:
            self._client = httpx.AsyncClient()

        resp = await self._client.get(
            f"{BASE_URL}{path}", headers=self._headers(), params=params
        )

        if resp.status_code == 401:
            raise AuthenticationError("Authentication failed")
        if resp.status_code == 404:
            raise NotFoundError(f"Not found: {path}")
        if resp.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        if resp.status_code >= 400:
            raise APIError(
                f"API error ({resp.status_code}): {resp.text}", resp.status_code
            )

        return resp.json()

    # --- Recipe search ---

    async def search_recipes(
        self,
        query: str,
        *,
        page: int = 1,
        per_page: int = 30,
        order: Literal["recent", "popular", "date"] = "recent",
        must_have_cooksnaps: bool = False,
        minimum_cooksnaps: int = 0,
        must_have_photo_in_steps: bool = False,
        included_ingredients: str = "",
        excluded_ingredients: str = "",
    ) -> SearchResponse:
        """Search recipes by keyword."""
        params: dict[str, Any] = {
            "query": query,
            "page": page,
            "per_page": per_page,
            "order": order,
            "must_have_cooksnaps": str(must_have_cooksnaps).lower(),
            "minimum_number_of_cooksnaps": minimum_cooksnaps,
            "must_have_photo_in_steps": str(must_have_photo_in_steps).lower(),
            "from_delicious_ways": "false",
            "search_source": "recipe.search.typed_query",
            "supported_types": SUPPORTED_SEARCH_TYPES,
        }
        if included_ingredients:
            params["included_ingredients"] = included_ingredients
        if excluded_ingredients:
            params["excluded_ingredients"] = excluded_ingredients

        data = await self._request("/search_results", params)
        return parse_search_response(data)

    # --- Recipe detail ---

    async def get_recipe(self, recipe_id: int) -> Recipe:
        """Get full recipe detail by ID."""
        data = await self._request(f"/recipes/{recipe_id}")
        return parse_recipe(data["result"])

    # --- Similar recipes ---

    async def get_similar_recipes(
        self,
        recipe_id: int,
        *,
        page: int = 1,
        per_page: int = 30,
    ) -> list[Recipe]:
        """Get similar recipes for a given recipe."""
        data = await self._request(
            f"/recipes/{recipe_id}/similar_recipes",
            {"page": page, "per_page": per_page},
        )
        return [parse_recipe(r) for r in data.get("result", [])]

    # --- Comments ---

    async def get_comments(
        self,
        recipe_id: int,
        *,
        limit: int = 20,
        after: str = "",
        label: str = "cooksnap",
    ) -> CommentsResponse:
        """Get comments (cooksnaps) for a recipe."""
        data = await self._request(
            f"/recipes/{recipe_id}/comments",
            {"limit": limit, "after": after, "label": label},
        )
        return parse_comments_response(data)

    # --- User search ---

    async def search_users(
        self,
        query: str,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> UsersResponse:
        """Search users by keyword."""
        data = await self._request(
            "/users",
            {"query": query, "page": page, "per_page": per_page},
        )
        return parse_users_response(data)

    # --- Search suggestions ---

    async def search_keywords(self, query: str = "") -> dict[str, Any]:
        """Get search keyword suggestions."""
        data = await self._request("/search_keywords", {"query": query})
        return data.get("result", {})

    # --- Search history ---

    async def get_search_history(
        self, local_history: list[str] | None = None
    ) -> dict[str, Any]:
        """Get search history / trending keywords."""
        history = json.dumps(local_history or [])
        data = await self._request(
            "/search_history", {"local_search_history": history}
        )
        return data
