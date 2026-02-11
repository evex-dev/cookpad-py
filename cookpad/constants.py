from __future__ import annotations

BASE_URL = "https://global-api.cookpad.com/v32"
API_HOST = "global-api.cookpad.com"

DEFAULT_TOKEN = "54ccbf3be26f7d3d3c1e068d53032e98e3ff992d49979f8e120b323910f0b942"
DEFAULT_USER_AGENT = "com.cookpad/2026.7.0; iOS/26.2.1; iPhone17,3; ; ja_JP;"
DEFAULT_COUNTRY = "JP"
DEFAULT_LANGUAGE = "ja"
DEFAULT_TIMEZONE_ID = "Asia/Tokyo"
DEFAULT_TIMEZONE_OFFSET = "+09:00"
DEFAULT_PROVIDER_ID = "8"

SUPPORTED_SEARCH_TYPES = ",".join([
    "search_results/recipe",
    "search_results/visual_guides",
    "search_results/spelling_suggestion",
    "search_results/title",
    "search_results/add_recipe_prompt",
    "search_results/premium_recipe_carousel",
    "search_results/premium_recipe_promotion",
    "search_results/library_recipes",
    "search_results/delicious_ways",
    "search_results/popular_promo_recipe",
    "search_results/premium_banner",
])
