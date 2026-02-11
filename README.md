# cookpad-py

Cookpad の非公式 Python クライアント。
iPhone 版アプリの API を解析して作った。

Support: [discord.gg/evex](https://discord.gg/evex)

## インストール

```bash
pip install cookpad
```

## 使い方
一部の引数とかは、認証済みのtokenじゃないと動かないので注意

```python
import asyncio
from cookpad import Cookpad

async def main():
    async with Cookpad() as client:
        # レシピ検索
        results = await client.search_recipes("カレー")
        for recipe in results.recipes:
            print(f"{recipe.title} (つくれぽ: {recipe.cooksnaps_count})")

        # レシピ詳細
        recipe = await client.get_recipe(25410768)
        print(recipe.title)
        for step in recipe.steps:
            print(f"  - {step.description}")

asyncio.run(main())
```

## API

### `Cookpad(*, token, country, language, ...)`

クライアント作成。引数は全部オプショナル。デフォルトで anonymous token 使うからそのまま動く。

```python
# デフォルト (日本語・匿名)
client = Cookpad()

# カスタム
client = Cookpad(
    token="your_token",
    country="JP",
    language="ja",
    user_agent="custom-ua/1.0",
)
```

### `search_recipes(query, *, page, per_page, order, ...)`

レシピ検索。`SearchResponse` を返す。

```python
results = await client.search_recipes(
    "鶏むね肉",
    order="popular",              # "recent" | "popular" | "date"
    must_have_cooksnaps=True,     # つくれぽありのみ
    minimum_cooksnaps=10,         # つくれぽ10件以上
    included_ingredients="卵",    # 含む材料
    excluded_ingredients="牛乳",  # 除外する材料
    page=1,
    per_page=30,
)

print(f"全 {results.total_count} 件")
for recipe in results.recipes:
    print(f"  {recipe.title}")

# 次のページがあるか
if results.next_page:
    page2 = await client.search_recipes("鶏むね肉", page=results.next_page)
```

### `get_recipe(recipe_id)`

レシピ詳細を取得。`Recipe` を返す。

```python
recipe = await client.get_recipe(25410768)
print(recipe.title)
print(recipe.story)
print(recipe.advice)
print(f"材料 ({recipe.serving}):")
for ing in recipe.ingredients:
    print(f"  {ing.name}: {ing.quantity}")
print("手順:")
for step in recipe.steps:
    print(f"  {step.description}")
```

### `get_similar_recipes(recipe_id, *, page, per_page)`

似てるレシピ一覧。

```python
similar = await client.get_similar_recipes(25410768)
for recipe in similar:
    print(recipe.title)
```

### `get_comments(recipe_id, *, limit, after, label)`

つくれぽ・コメント取得。

```python
comments = await client.get_comments(18510866, limit=10)
for comment in comments.comments:
    print(f"{comment.user.name}: {comment.body}")

# ページネーション (カーソルベース)
if comments.next_cursor:
    more = await client.get_comments(18510866, after=comments.next_cursor)
```

### `search_users(query, *, page, per_page)`

ユーザー検索。

```python
users = await client.search_users("test")
for user in users.users:
    print(f"{user.name} (レシピ数: {user.recipe_count})")
```

### `search_keywords(query)`

検索サジェスト。

```python
suggestions = await client.search_keywords("カレ")
```

### `get_search_history(local_history)`

検索履歴・トレンドキーワード。

```python
history = await client.get_search_history()
```

## 型

レスポンスは全部 dataclass でパース済み。IDE の補完が効く。

- `Recipe` - レシピ (id, title, story, serving, ingredients, steps, ...)
- `Ingredient` - 材料 (name, quantity)
- `Step` - 手順 (description, image_url)
- `User` - ユーザー (id, name, recipe_count, ...)
- `Comment` - コメント/つくれぽ (body, user, image_url, ...)
- `Image` - 画像 (url, filename, alt_text)
- `SearchResponse` - 検索結果 (recipes, total_count, next_page, raw)
- `CommentsResponse` - コメント一覧 (comments, next_cursor)
- `UsersResponse` - ユーザー一覧 (users, total_count, next_page)

`SearchResponse.raw` で API の生レスポンス (dict) にもアクセスできる。

## 例外

```python
from cookpad import CookpadError, AuthenticationError, NotFoundError, RateLimitError, APIError

try:
    recipe = await client.get_recipe(99999999)
except NotFoundError:
    print("レシピが見つからない")
except RateLimitError:
    print("レート制限")
except CookpadError as e:
    print(f"なんかエラー: {e}")
```

## ライセンス

MIT
