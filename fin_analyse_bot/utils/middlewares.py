from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from typing import Dict, Any, Callable, Awaitable

class AccessMiddleware(BaseMiddleware):
    def __init__(self, user_id: int):
        self.user_id = int(user_id)
        super().__init__()                                                                            

    async def __call__(self, 
                       handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
                       event: types.Message,
                       data: Dict[str, Any]) -> Any:
        if event.from_user.id != self.user_id:
            return True
        return await handler(event, data)