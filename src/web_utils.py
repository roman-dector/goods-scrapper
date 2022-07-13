from aiohttp import ClientSession
from fake_useragent import UserAgent


async def get_html_page(session: ClientSession, url: str, user_agent: UserAgent, headers: dict = {}) -> str:
    async with session.get(
        url=url,
        # timeout=1,
        headers={'user-agent': user_agent.random, **headers},
    ) as resp:
        return await resp.text(encoding="utf-8")
