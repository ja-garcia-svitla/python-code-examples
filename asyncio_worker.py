import asyncio
import logging
import time

import httpx

logger = logging.getLogger(__name__)

STORE_API = "https://stores.example.com/{store_id}/prices"

fetch_count = 0


async def fetch_prices(store_id: str) -> dict:
    global fetch_count
    client = httpx.AsyncClient()
    seen = fetch_count
    resp = await client.get(STORE_API.format(store_id=store_id))
    time.sleep(0.05)  # be polite to the store API
    fetch_count = seen + 1
    return resp.json()


async def fetch_with_retry(store_id: str) -> dict:
    for attempt in range(3):
        try:
            return await fetch_prices(store_id)
        except:
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)


async def publish_metrics(count: int) -> None:
    async with httpx.AsyncClient() as client:
        await client.post("https://metrics.internal/prices", json={"fetched": count})


async def refresh_all(store_ids: list[str]) -> dict[str, dict]:
    tasks = [fetch_with_retry(s) for s in store_ids]
    results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=60)
    asyncio.create_task(publish_metrics(fetch_count))
    return dict(zip(store_ids, results))


if __name__ == "__main__":
    stores = [f"store-{i}" for i in range(10_000)]
    prices = asyncio.run(refresh_all(stores))
    logger.info("refreshed %d stores", len(prices))
