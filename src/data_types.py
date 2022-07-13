from itertools import product
from typing import TypeAlias, NamedTuple
from dataclasses import dataclass


ShopName: TypeAlias = str
ProductName: TypeAlias = str
ProductItemLink: TypeAlias = str


@dataclass(slots=True)
class Shop:
    id: int
    name: ShopName


@dataclass(slots=True, frozen=True)
class ProductItem:
    shop_name: ShopName
    product_name: ProductName
    url: ProductItemLink


class ItemForScrap(NamedTuple):
    id: int
    url: str
    shop_id: int
    shop_name: ShopName


class PricesForSave(NamedTuple):
    selling_price: str
    net_price: str
    id: int


class ScrappedPrices(NamedTuple):
    selling_price: str
    net_price: str


@dataclass(slots=True, frozen=True)
class InfoForDb:
    shop_names: list[ShopName]
    product_names: list[ProductName]
    product_item_links: list[ProductItemLink]


@dataclass(slots=True, frozen=True)
class ProductItemForResultSheet:
    shop_name: ShopName
    product_name: ProductName
    product_item_link: ProductItemLink
    selling_price: str
    net_price: str