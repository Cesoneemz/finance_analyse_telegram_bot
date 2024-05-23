import re
import logging
import sys
import asyncio
import datetime

from pydantic import BaseModel
from typing import List, Optional
from asyncpg import Record
from logging import Logger

from .categories import Categories
from .exceptions import NotCorrectMessage

import os

if os.getenv('DEBUG'):
    from icecream import ic

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger: Logger = logging.getLogger(__name__)

class Expense(BaseModel):
    id: Optional[int] = None
    amount: int
    category_codename: str
    created_at: Optional[datetime.datetime] = None

async def add_expense(message: str) -> bool:
    try:
        expenses_list: List[Expense] = _parse_message(message)
    except NotCorrectMessage as err:
        logger.error(f'{err}: {message}.')
        return False
    
    categories_instance: Categories = await Categories.create_instance()

    category_tasks: List[Categories] = [categories_instance.get_category(exp.category_codename) for exp in expenses_list]
    categories: List[Categories] = await asyncio.gather(*category_tasks)

    expenses_data: List[dict] = [
        {
            'amount': int(exp.amount),
            'category_codename': cat.codename,
            'created_at': exp.created_at
        } for exp, cat in zip(expenses_list, categories)
    ]

    await categories_instance.manager.insert('expenses', expenses_data)
    logger.info(f'{expenses_data} has to be inserted into table expenses')
    return True

async def delete_expense(row_id: int) -> bool:
    categories_instance: Categories = await Categories.create_instance()

    if await categories_instance.manager.delete("expenses", row_id):
         return True
    return False

async def get_last_expense() -> List[Expense]:
    categories_instance: Categories = await Categories.create_instance()

    records: List[Record] = await categories_instance.manager.execute(
         "SELECT e.id, e.amount, c.name, e.created_at "
         "FROM expenses e LEFT JOIN category c "
         "ON c.codename=e.category_codename "
         "ORDER BY created_at DESC LIMIT 10"
    )

    if not records:
        return []
    
    if os.getenv('DEBUG'):
        ic(records)
    
    last_expenses: List[Expense] = [Expense(id=row[0], 
                                    amount=row[1], 
                                    category_codename=row[2],
                                    created_at=row[3]) for row in records]

    return last_expenses


async def get_today_statistics() -> List[Record]:
    categories_instance: Categories = await Categories.create_instance()

    records: List[Record] = await categories_instance.manager.execute(
        "SELECT SUM(e.amount) as total_amount, c.name AS name "
        "FROM expenses e "
        "JOIN category c ON e.category_codename = c.codename "
        "WHERE CAST(created_at AS DATE) = CURRENT_DATE "
        "GROUP BY c.name"
    )

    if os.getenv('DEBUG'):
        ic(records)

    if not records:
        return []
    
    return records

async def get_month_statistics() -> List[Record]:
    categories_instance: Categories = await Categories.create_instance()

    records: List[Categories] = await categories_instance.manager.execute(
        "SELECT SUM(e.amount) AS total_amount, c.name AS name "
        "FROM expenses e "
        "JOIN category c ON e.category_codename = c.codename "
        "WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE) "
        "GROUP BY c.name"
    )

    if os.getenv('DEBUG'):
        ic(records)

    if not records:
        return []
    
    return records


def _parse_message(message: str) -> List[Expense]:
    expenses_list: List = []

    for expense in message: 
        regexp_result = re.match(
            r"([\d ]+) (.*)",
            expense
        )
        
        if not regexp_result \
            or not regexp_result.group(0) \
            or not regexp_result.group(1) \
            or not regexp_result.group(2):
                raise NotCorrectMessage()

        exp: Expense = Expense(
            amount=regexp_result.group(1).strip(),
            category_codename=regexp_result.group(2).strip(),
            created_at=datetime.datetime.now()
        )

        expenses_list.append(exp)


    return expenses_list