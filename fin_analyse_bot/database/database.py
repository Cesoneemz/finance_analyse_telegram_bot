import os
import asyncpg
import logging, sys

from logging import Logger

from asyncpg.exceptions import UndefinedColumnError
from asyncpg import Record, Pool

from typing import Dict, List, Tuple, Any

if os.getenv('DEBUG'):
    from icecream import ic

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger: Logger = logging.getLogger(__name__)


class DatabaseManager():

    DB_USER: str = os.getenv('DB_USER')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD')
    DB_NAME: str = os.getenv('DB_NAME')
    DB_HOST: str = os.getenv('DB_HOST')

    DB_URL: str = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

    _pool: Pool = None

    @classmethod
    async def get_pool(cls) -> Pool:
        if cls._pool is None:
            cls._pool: Pool = await asyncpg.create_pool(cls.DB_URL)
        return cls._pool
    
    async def insert(self, table: str, column_values: Dict) -> None:
        columns: str = ', '.join(column_values[0].keys())
        placeholders: str = ', '.join(f'${i+1}' for i in range(len(column_values[0])))

        query: str = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        pool: Pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.executemany(query, [tuple(item.values()) for item in column_values])

    async def fetchall(self, table: str, columns: List[str]) -> List[Tuple]:
        columns_joined: str = ', '.join(columns)

        pool: Pool = await self.get_pool()

        logger.info(f'Connect to database on host {self.DB_HOST} on database {self.DB_NAME}')

        async with pool.acquire() as conn:
            try:
                records: List[Record] = await conn.fetch(
                    f"SELECT {columns_joined} "
                    f"FROM {table}"
                )
            except UndefinedColumnError as err:
                logger.error(err)
                return []


        return [dict(record) for record in records]
    
    async def delete(self, table: str, row_id: int) -> bool:
        pool: Pool = await self.get_pool()

        if os.getenv('DEBUG'):
            ic(table, row_id)

        try:
            async with pool.acquire() as conn:
                result: Record = await conn.execute(f"DELETE FROM {table} WHERE id=$1", row_id)

            deleted_rows: int = int(result.split()[-1])

            if deleted_rows == 0:
                logger.error(f"No row found with ID {row_id} in table {table}. No rows deleted.")
                return False
            
            return True
        except Exception as err:
            logger.error(err)
            return False
        
    async def execute(self, query: str) -> bool:
        pool: Pool = await self.get_pool()

        try:
            async with pool.acquire() as conn:
                result: Any[List[Record], Record] = await conn.fetch(query)
            return result
        except Exception as err:
            logger.error(err)
            return False



            
