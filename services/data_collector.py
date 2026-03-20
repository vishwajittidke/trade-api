import asyncio
import logging
import httpx
from duckduckgo_search import DDGS

log = logging.getLogger(__name__)


async def fetch_market_data(sector):
    """
    Searches DuckDuckGo for news + web results about the sector,
    also tries to scrape a couple of gov/industry sites for extra context.
    Returns a list of text snippets to feed into Gemini.
    """
    log.info(f"Collecting data for: {sector}")

    # fire all searches at once
    results = await asyncio.gather(
        asyncio.to_thread(_search_news, sector),
        asyncio.to_thread(_search_web, sector),
        _scrape_extra_sources(sector),
        return_exceptions=True,
    )

    collected = []
    for r in results:
        if isinstance(r, list):
            collected.extend(r)
        elif isinstance(r, Exception):
            log.warning(f"One data source failed: {r}")

    # if everything failed, at least give the AI some context
    if not collected:
        collected = [
            f"Live data sources unavailable. Provide general analysis "
            f"for {sector} sector in India based on your knowledge."
        ]

    log.info(f"Got {len(collected)} data points for {sector}")
    return collected


def _search_news(sector):
    """DuckDuckGo news search"""
    items = []
    try:
        ddg = DDGS()
        for r in ddg.news(f"{sector} India market trade opportunities", max_results=8):
            items.append(
                f"[NEWS] {r.get('title', '')}\n"
                f"  {r.get('body', '')}\n"
                f"  Source: {r.get('source', '?')} | Date: {r.get('date', '?')} | URL: {r.get('url', '')}"
            )
    except Exception as e:
        log.error(f"News search failed: {e}")
        raise
    return items


def _search_web(sector):
    """DuckDuckGo text search across multiple queries"""
    queries = [
        f"{sector} sector India trade opportunities export import 2026",
        f"{sector} India market analysis trends",
        f"{sector} India industry growth investment",
    ]
    items = []
    try:
        ddg = DDGS()
        for q in queries:
            for r in ddg.text(q, max_results=5):
                items.append(
                    f"[WEB] {r.get('title', '')}\n"
                    f"  {r.get('body', '')}\n"
                    f"  URL: {r.get('href', '')}"
                )
    except Exception as e:
        log.error(f"Web search failed: {e}")
        raise
    return items


async def _scrape_extra_sources(sector):
    """try to grab some info from IBEF and Invest India"""
    urls = [
        f"https://www.ibef.org/industry/{sector}",
        f"https://www.investindia.gov.in/sector/{sector}",
    ]
    items = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for url in urls:
            try:
                resp = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; TradeAPI/1.0)"
                })
                if resp.status_code != 200:
                    continue

                html = resp.text

                # pull out <title> tag
                t1, t2 = html.find("<title>"), html.find("</title>")
                title = html[t1+7:t2].strip() if t1 != -1 and t2 != -1 else ""

                # pull out meta description
                marker = 'name="description" content="'
                idx = html.find(marker)
                desc = ""
                if idx != -1:
                    start = idx + len(marker)
                    desc = html[start:html.find('"', start)].strip()

                if title or desc:
                    items.append(f"[SCRAPE] {title}\n  {desc}\n  Source: {url}")
            except Exception:
                pass  # scraping is best-effort, don't care if it fails
    return items
