import asyncio
import logging
import os
import google.generativeai as genai

log = logging.getLogger(__name__)

# setup gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    log.critical("GEMINI_API_KEY not set!")

# try these models in order if one hits rate limits
MODELS = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash"]

PROMPT = """\
You are an expert trade and financial analyst specializing in Indian markets.

RULES:
- Use ONLY the provided data below, do NOT make up statistics.
- If data is insufficient for a section, say so explicitly.
- Cite sources from the provided data.
- Focus on India-specific trade opportunities (exports, imports, FDI, partnerships).

MARKET DATA:
{data}

SECTOR: {sector}

Write a markdown report with this structure:

# Trade Opportunity Report: {sector} Sector (India)

## Summary
Executive summary of current state and key trade opportunities.

## Key Trends
3-5 bullet points on trends shaping this sector in India.

## Trade Opportunities
- Export opportunities
- Import substitution possibilities
- FDI prospects
- Partnership/collaboration opportunities

## Risks
- Regulatory risks
- Market risks
- Geopolitical factors
- Competition

## Recommendation
3-5 actionable recommendations for businesses.

## Sources
List sources used from the provided data.
"""


async def analyze_with_ai(sector, data):
    """Send data to Gemini and get back a structured markdown report.
    Tries multiple models with retries if we get rate limited."""
    
    prompt = PROMPT.format(sector=sector.title(), data="\n\n".join(data))
    last_err = None

    for model_name in MODELS:
        model = genai.GenerativeModel(model_name)
        
        for attempt in range(3):
            try:
                resp = await model.generate_content_async(prompt)
                log.info(f"Got response from {model_name} for {sector}")
                return resp.text
            except Exception as e:
                last_err = e
                err_msg = str(e)
                log.warning(f"{model_name} attempt {attempt+1} failed: {err_msg[:150]}")

                # rate limited - back off and maybe try next model
                if "429" in err_msg or "ResourceExhausted" in err_msg:
                    if attempt < 2:
                        await asyncio.sleep(2 * (2 ** attempt))
                    else:
                        break  # move to next model
                elif attempt < 2:
                    await asyncio.sleep(2 * (2 ** attempt))

    raise Exception(f"All AI models failed. Last error: {last_err}")
