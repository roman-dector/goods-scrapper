from typing import Iterator
from sqlite3 import Connection, Cursor, connect

from aiosqlite import (
        Connection as ConnectionAsync,
        connect as connect_async
    )

from data_types import (
        InfoForDb,
        ProductItem,
        ProductItemForResultSheet,
        Shop,
        ShopName,
        ProductName,
        PricesForSave,
        ItemForScrap,
    )
from config import DB_PATH, EXCEL_INPUT_PATH


def load_shops_to_db(cursor: Cursor, shops: Iterator[ShopName]) -> None:
    cursor.executemany(
        'insert into shop(name) values (?)',
        tuple((s,) for s in shops)
    )


def load_products_to_db(cursor: Cursor, products: Iterator[ProductName]) -> None:
    cursor.executemany(
        'insert into product(name) values (?)',
        tuple((p,) for p in products)
    )


def load_product_items_to_db(cursor: Cursor, product_items: Iterator[ProductItem]) -> None:
    for item in product_items:
        cursor.execute(
            "select id from shop where name is ?",
            (item.shop_name,)
        )
        shop_id = cursor.fetchone()[0]

        cursor.execute(
            "select id from product where name is ?",
            (item.product_name,)
        )
        product_id = cursor.fetchone()[0]

        url = None if item.url.startswith(
            '-') or item.url == None else item.url

        cursor.execute(
            "insert into product_item(product_id, shop_id, url) values (?,?,?)",
            (product_id, shop_id, url)
        )


def clear_db(cursor: Cursor) -> None:
    cursor.execute('delete from shop;')
    cursor.execute('delete from product;')
    cursor.execute('delete from product_item;')


def load_data_to_db(info_for_db: InfoForDb, mode: str = None) -> None:
    connection: Connection = connect(DB_PATH)
    cursor: Cursor = connection.cursor()

    if mode == 'r':
        clear_db(cursor)

    load_shops_to_db(cursor, info_for_db.shop_names)
    load_products_to_db(cursor, info_for_db.product_names)
    load_product_items_to_db(cursor, info_for_db.product_item_links)

    connection.commit()
    connection.close()


async def select_shops_from_db(connection: ConnectionAsync) -> tuple[Shop]:
    resp = await connection.execute_fetchall('select id, name from shop')
    return tuple(Shop(id=i[0], name=i[1]) for i in resp)


async def select_products_from_db(connection: ConnectionAsync) -> tuple[Shop]:
    resp = await connection.execute_fetchall('select id, name from product;')
    return tuple(Shop(id=i[0], name=i[1]) for i in resp)


async def select_shop_name(connection: ConnectionAsync, shop_id: int) -> str:
    response = await connection.execute_fetchall('select name from shop where id is ?;', (shop_id,))
    return response[0][0]


async def select_product_items(connection: ConnectionAsync, shop_id: int) -> tuple[ItemForScrap]:
    shop_name = await select_shop_name(connection, shop_id)
    resp = await connection.execute_fetchall('''
select product_item.id, url
from product_item
where url is not null and product_item.shop_id is ?;
''', (shop_id,))

    return tuple(ItemForScrap(id=i[0], url=i[1], shop_name=shop_name, shop_id=shop_id) for i in resp)


async def write_prices_to_db(prices_for_save: PricesForSave) -> None:
    async with connect_async(DB_PATH) as connection:
        await connection.execute('''
update product_item
set selling_price = ?, net_price = ?
where id is ?;
''', (prices_for_save.selling_price,
    prices_for_save.net_price,
    prices_for_save.id)
    )

        await connection.commit()


async def get_items_scrap_from_db() -> Iterator[ItemForScrap]:
    async with connect_async(DB_PATH) as connection:
        shops = await select_shops_from_db(connection)

        for shop in shops:
            if shop.name not in ('Noon', 'Mumzworld'):
                for item in await select_product_items(connection, shop.id):
                    yield item


async def get_product_items_for_result_sheet(connection: ConnectionAsync) -> tuple[ProductItemForResultSheet]:
    table_selection = await connection.execute_fetchall('''
with tmp_table as (
    select
        s.name as shop_name,
        pi.url,
        pi.selling_price,
        pi.net_price,
        pi.product_id
    from product_item pi
    inner join shop s on pi.shop_id = s.id
)

select
     t.shop_name,
     pt.name as product_name,
     t.url,
     t.selling_price,
     t.net_price
from tmp_table t
inner join product pt on t.product_id = pt.id;
'''
    )
    return tuple(ProductItemForResultSheet(
        shop_name=item[0],
        product_name=item[1],
        product_item_link=item[2],
        selling_price=item[3],
        net_price=item[4],
    ) for item in table_selection)



if __name__ == '__main__':
    connection = connect(DB_PATH)
    print(select_shops_from_db(connection))
