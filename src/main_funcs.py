import asyncio
import aiohttp

from typing import Iterator

from aiosqlite import (
    connect as connect_async
)
from fake_useragent import UserAgent
from openpyxl import Workbook

from excel_handlers import create_result_sheet_header, fill_result_sheet, parce_excell_file
from db_handlers import (
    load_data_to_db,
    get_items_scrap_from_db,
    select_products_from_db,
    select_shops_from_db,
    write_prices_to_db,
    get_product_items_for_result_sheet
)
from parsers import get_prices_for_product_item
from data_types import PricesForSave
from config import DB_PATH, EXCEL_RESULT_PATH, EXCEL_INPUT_PATH


def add_new_products_for_monitoring(path_to_excell_file: str, mode='a') -> None:
    load_data_to_db(parce_excell_file(path_to_excell_file), mode=mode)


async def get_prices() -> Iterator[PricesForSave]:
    ua = UserAgent()
    async with aiohttp.ClientSession() as session:
        async for item in get_items_scrap_from_db():
            yield await get_prices_for_product_item(session, item, ua)


async def save_prices_to_db() -> None:
    async for price in get_prices():
        await write_prices_to_db(price)


async def create_result_execel_sheet() -> None:
    async with connect_async(DB_PATH) as connection:
        shops = await select_shops_from_db(connection)
        products = await select_products_from_db(connection)
        product_items_for_result_sheet = await get_product_items_for_result_sheet(connection)

    workbook = Workbook()
    worksheet = workbook.active

    create_result_sheet_header(
        worksheet=worksheet,
        shops=shops,
        products=products
    )

    fill_result_sheet(
        worksheet=worksheet,
        product_items=product_items_for_result_sheet
    )

    workbook.save(EXCEL_RESULT_PATH)



if __name__ == '__main__':
    add_new_products_for_monitoring(EXCEL_INPUT_PATH)
    asyncio.run(save_prices_to_db())
    asyncio.run(create_result_execel_sheet())
    pass
