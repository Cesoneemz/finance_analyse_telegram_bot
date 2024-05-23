from pydantic import BaseModel
from .database import DatabaseManager

from typing import Dict, List, Tuple

class Category(BaseModel):
    codename: str
    name: str
    aliases: List[str] | None

class Categories:
    def __init__(self, categories: List[Category]) -> None:
        self.manager: DatabaseManager = DatabaseManager()
        self.categories: List[Category] = categories

    @classmethod
    async def create_instance(cls):
        instance = cls(categories=[])
        instance.categories = await instance._load_categories()
        return instance

    async def _fetch_categories_from_db(self) -> List[Tuple]:
        categories: List[Tuple] = await self.manager.fetchall(
            "category", "codename name aliases".split()
        )
        return categories

    async def _load_categories(self) -> List[Category]:
        categories: List[Tuple] = await self._fetch_categories_from_db()
        if categories != -1:
            return self._fill_aliases(categories)
    
    def _fill_aliases(self, categories: List[Dict]) -> List[Category]:
        categories_result: List = []
        for category in categories:
            aliases: List = category["aliases"].split(",")
            aliases: List = list(filter(None, map(str.strip, aliases)))
            aliases.append(category["codename"])
            aliases.append(category["name"])
            categories_result.append(Category(
                codename=category['codename'],
                name=category['name'],
                aliases=aliases
            ))
        return categories_result
    
    async def get_all_categories(self) -> List[Category]:
        return self.categories
    
    async def get_category(self, category_name: str) -> Category:
        finded = None
        other_category = None
        for category in self.categories:
            if category.codename == "other":
                other_category = category
            for alias in category.aliases:
                if category_name in alias:
                    finded = category
        if not finded:
            finded = other_category
        return finded
