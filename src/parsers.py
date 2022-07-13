import asyncio
import aiohttp

from bs4 import BeautifulSoup
from aiohttp import ClientSession
from fake_useragent import UserAgent

from web_utils import get_html_page
from data_types import ItemForScrap, PricesForSave, ScrappedPrices, ShopName


'''
css-168eikn   ->    css-1oh8fze   ->   css-17ctnp | css-1i90gmp + css-1bdwabt

'''


def find_span_by_class(soup, class_name: str):
    return soup.find('span', class_=class_name)


def form_prices(selling_price: str, net_price: str):
    return ScrappedPrices(
        selling_price=selling_price,
        net_price=net_price,
    )


def get_prices_from_dubai_store_product_card(soup: BeautifulSoup):
    if price_box := soup.find('h3', class_='main-price'):
        if price_old := price_box.find('span', class_='price-old'):
            price_old = 'AED' + ' ' + price_old.text[3:]
        else:
            price_old = None

        if current_price := price_box.find('span', class_='price-new'):
            current_price = 'AED' + ' ' + current_price.text[3:]
        else:
            current_price = None
        
        return form_prices(current_price, price_old)

    return form_prices(None, None)




def get_prices_from_carrefour_product_card(soup: BeautifulSoup) -> ScrappedPrices:
    if price := soup.find('h2', class_='css-17ctnp'):
        if bracket_indx := price.text.find('('):
            return form_prices(price.text[:bracket_indx].strip(), None)
        return form_prices(price.text.strip(), None)

    if price := soup.find('h2', class_='css-1i90gmp'):
        if bracket_indx := price.text.find('('):
            row_price = price.text[:bracket_indx].strip()
            prices = row_price.split('AED')
            return form_prices('AED' + prices[1], 'AED' + prices[2])
    
    return form_prices(None, None)


def get_prices_from_amazon_product_card(soup: BeautifulSoup) -> ScrappedPrices:
    if price := find_span_by_class(soup, 'basisPrice'):
        row_net_price = price.find('span', class_='a-offscreen').text.strip()
        net_price = row_net_price[:3] + ' ' + row_net_price[3:]
    else:
        net_price = None

    if price := soup.find('span', id='sns-base-price'):
        if bracket_indx := price.text.find('('):
            return form_prices(price.text[:bracket_indx].strip(), net_price)
        return form_prices(price.text.strip(), net_price)

    if price := find_span_by_class(soup, 'a-price'):
        row_price = price.find('span', class_='a-offscreen').text.strip()
        return form_prices(row_price[:3] + ' ' + row_price[3:], net_price)

    if price_whole := find_span_by_class(soup, 'a-price-whole'):
        price_fractions = tuple(i.text.strip()
                                for i in price_whole.parent.findChildren())
        selling_price = f'{price_fractions[0]} {price_fractions[1].strip(".")}.{price_fractions[3]}'
        return form_prices(selling_price, net_price)

    if price := find_span_by_class(soup, 'a-color-price'):
        return form_prices(price.text.strip(), net_price)

    return form_prices(None, None)


def get_prices_from_shop(soup: BeautifulSoup, shop_name: ShopName) -> ScrappedPrices:
    match shop_name:
        case 'Amazon.ae':
            return get_prices_from_amazon_product_card(soup)
        case 'Carrefour UAE':
            return get_prices_from_carrefour_product_card(soup)
        case 'DubaiStore':
            return get_prices_from_dubai_store_product_card(soup)
        case _:
            pass


async def get_prices_for_product_item(
    session: ClientSession,
    scrap_item: ItemForScrap,
    user_agent: UserAgent
) -> PricesForSave:
    html_page = await get_html_page(session=session, url=scrap_item.url, user_agent=user_agent)
    page_soup = BeautifulSoup(html_page, 'lxml')

    if not (scrapped_prices := get_prices_from_shop(page_soup, scrap_item.shop_name)):
        with open('./logs.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f"{scrap_item.id}\n")
        return



    return PricesForSave(
        id=scrap_item.id,
        selling_price=scrapped_prices.selling_price,
        net_price=scrapped_prices.net_price
    )


if __name__ == "__main__":
    async def main():
        ua = UserAgent()
        async with aiohttp.ClientSession() as session:
            html_page = await get_html_page(
                session=session,
                url='https://www.carrefouruae.com/mafuae/en/root-maf-category/nonfood-navigation-category/electronics-appliances/tvs-projectors/receiver-satellite-accessories/xiaomi-mi-box-s-black-with-4k-hdr-android-tv-streaming-media-player-google-assistant-remote-official-international-version/p/6941059603283?offerCode=2383113',
                user_agent=ua,
            )
            page_soup = BeautifulSoup(html_page, 'lxml')
            print('Done!')
            print(get_prices_from_carrefour_product_card(page_soup))
    
    asyncio.run(main())
