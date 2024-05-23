import asyncio
import logging
import os
import re
import sys
from datetime import datetime
from logging import Logger
from typing import List, Match

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hbold
from asyncpg import Record
from database.categories import Categories
from database.expenses import (Expense, add_expense, delete_expense,
                               get_last_expense, get_month_statistics,
                               get_today_statistics)
from utils.keyboards import Action, builder
from utils.middlewares import AccessMiddleware

if os.getenv('DEBUG'):
    from icecream import ic


token: str | None = os.getenv('BOT_TOKEN')
user_id: str | None = os.getenv('USER_ID')
dp: Dispatcher = Dispatcher()

if os.getenv('DEBUG'):
    ic(token, user_id)

dp.message.middleware(AccessMiddleware(user_id))

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger: Logger = logging.getLogger(__name__)

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(
        "Бот для учёта и анализа финансов\n\n"
        f"Добавить расход: {hbold('250 такси')}\n\n"
        f"Сегодняшняя статистика: {hbold('/today')}\n"
        f"Статистика за месяц: {hbold('/month')}\n"
        f"Последние 10 добавленных расходов: {hbold('/last')}\n",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(Command("categories"))
@dp.message(F.text == Action.categories.value)
async def categories_list(message: types.Message):
    categories_instance: Categories = await Categories.create_instance()
    categories: List[Categories] = await categories_instance.get_all_categories()
    if categories:
        answer_message: str = "Категории трат:\n\n- " +\
                ("\n- ".join([hbold(c.name)+' ('+", ".join(c.aliases)+')' for c in categories]))
        return await message.answer(answer_message)

@dp.message(Command("delete"))
async def delete_expenses(message: types.Message):
    match: Match[str] = re.match(r"/delete\s+(\d+)$", message.text.strip())
    if not match:
        return await message.answer(f"Неверный формат команды. \n\nИспользуйте {hbold('/delete [id записи]')}")

    row_id: int = int(match.group(1))

    if os.getenv('DEBUG'):
        ic(row_id)

    if await delete_expense(row_id=row_id):
        return await message.answer('Запись о расходах была удалена')
    
    return await message.answer('Ошибка при удалении записи в базе данных')

@dp.message(Command("last"))
async def last_expense(message: types.Message):
    last_expenses: List[Expense] = await get_last_expense()
    if len(last_expenses) == 0:
        return await message.answer('Расходы ещё не были добавлены')
    
    last_expenses_rows: List[str] = [
        f"{expense.id}: {expense.amount} руб. на категории {expense.category_codename}\n"
        f"Дата: {expense.created_at.replace(microsecond=0) if expense.created_at is not None else 'Не указана'}"
        for expense in last_expenses
    ]

    return await message.answer(
        f"{hbold('Последние добавленные расходы:')}\n\n" + "\n\n".join(last_expenses_rows) + 
        f"\n\nДля удаления записи о расходах используйте команду: {hbold('/delete')}"
    )

@dp.message(Command("today"))
@dp.message(F.text == Action.today.value)
async def get_today_statistics_handler(message: types.Message):
    records: List[Record] = await get_today_statistics()

    if len(records) == 0:
        return await message.answer('Сегодня расходов не было')

    result: List = [f"Категория: {row[1].capitalize()}\n"
              f"Сумма трат: {row[0]} руб."
              for row in records]

    return await message.answer('Расходы за сегодня:\n\n' + '\n\n'.join(result))

@dp.message(Command("month"))
@dp.message(F.text == Action.month.value)
async def get_month_statistics_handler(message: types.Message):
    records: List[Record] = await get_month_statistics()

    months: List = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    
    current_month: str = months[datetime.now().month - 1]

    if os.getenv('DEBUG'):
        ic(current_month)

    if len(records) == 0:
        return await message.answer(f'За {current_month} расходов не было')
    
    result: List = [f"Категория: {row[1].capitalize()}\n"
              f"Сумма трат: {row[0]} руб."
              for row in records]

    return await message.answer(f'Расходы за {current_month}:\n\n' + '\n\n'.join(result))

@dp.message()
async def add_expenses(message: types.Message):
    if await add_expense(message.text.split('\n')):
        return await message.answer('Расход был добавлен')
    
    return await message.answer('Неверный формат сообщения')

async def main() -> None:
    bot_properties: DefaultBotProperties = DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )

    bot: Bot = Bot(token=token, default=bot_properties)

    await dp.start_polling(bot)

if __name__ == '__main__':
    logger.info('Starting bot')
    asyncio.run(main())
    logging.info('Stopping bot')
