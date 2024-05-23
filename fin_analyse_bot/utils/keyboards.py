from enum import Enum

from aiogram.utils.keyboard import ReplyKeyboardBuilder

class Action(str, Enum):
    categories = "Категории"
    today = "Сегодня"
    month = "Месяц"

builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
for action in Action:
    builder.button(
        text=action.value.title()
    )
