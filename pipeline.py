import logging

from services.data_collector import fetch_market_data
from services.ai_analyzer import analyze_with_ai
from services.formatter import format_markdown
from utils.validator import validate_markdown
from utils.cache import get_cache, set_cache

log = logging.getLogger(__name__)


async def run_pipeline(sector):
    """main pipeline: check cache -> collect data -> AI analysis -> format -> cache"""
    key = f"sector:{sector.lower()}"

    # return cached if available
    cached = get_cache(key)
    if cached:
        log.info(f"Cache hit for {sector}")
        return cached

    # collect real market data
    log.info(f"Starting pipeline for {sector}")
    data = await fetch_market_data(sector)

    if not data:
        raise Exception(f"Couldn't collect any data for {sector}")

    # run through gemini
    try:
        ai_result = await analyze_with_ai(sector, data)
    except Exception as e:
        raise Exception(f"AI analysis failed: {e}")

    # check if output looks reasonable (just a warning, don't block)
    if not validate_markdown(ai_result):
        log.warning(f"AI output for {sector} might be missing some sections")

    result = format_markdown(ai_result, sector=sector)
    set_cache(key, result)
    log.info(f"Pipeline done for {sector}")
    return result
