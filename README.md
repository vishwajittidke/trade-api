# Trade Opportunities API 🇮🇳

A simple FastAPI service that looks up market data for Indian sectors using DuckDuckGo and then summarizes it with Google Gemini.

## setup

1. **Get a Gemini key** from [Google AI Studio](https://aistudio.google.com/apikey).
2. **Install things**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Setup env variables**: Create a `.env` file (see `.env.example`) and add your key.
   ```text
   GEMINI_API_KEY=your_key_here
   SECRET_KEY=something_random
   ```
4. **Run it**:
   ```bash
   uvicorn main:app --reload
   ```

## docker

If you have Docker, you can just do this:

1. **Build image**:
   ```bash
   docker build -t trade-api .
   ```
2. **Run it** (make sure to pass the .env):
   ```bash
   docker run -p 8000:8000 --env-file .env trade-api
   ```

## endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | No | System health check |
| `POST` | `/auth/token` | No | Get your access token |
| `GET` | `/sectors` | No | List of supported industries |
| `GET` | `/analyze/{sector}` | Yes | Run the trade analysis |

Full interactive docs available at `http://localhost:8000/docs`.

### How to use Swagger UI:
1.  Go to the `/auth/token` endpoint in the docs and click **Try it out**.
2.  Enter a username and click **Execute**.
3.  Copy the `access_token` from the response.
4.  Scroll to the top and click the 🔓 **Authorize** button.
5.  Paste your token into the **Value** field and click **Authorize**.
6.  Now you can use the `/analyze/{sector}` endpoint!
## how to use

It uses JWT tokens, so you have to "login" first to get one.

1. **Get Token**:
   ```bash
   curl -X POST http://localhost:8000/auth/token -d '{"username": "dev"}' -H "Content-Type: application/json"
   ```
   Save the `access_token` from the response.

2. **Analyze a Sector**: Use the token in the header.
   ```bash
   curl http://localhost:8000/analyze/pharmaceuticals -H "Authorization: Bearer <your_token>"
   ```
   Current sectors: `pharmaceuticals`, `technology`, `agriculture`, `banking`, `energy`, `automotive`, `textiles`, `infrastructure`, `telecommunications`, `chemicals`.

## project layout

- `main.py`: health, auth, and the main analyze endpoint.
- `pipeline.py`: orchestrates the whole flow (search -> AI -> format).
- `services/`:
  - `data_collector.py`: uses DuckDuckGo and scrapes some sites for data.
  - `ai_analyzer.py`: the Gemini logic with retries and model fallbacks.
  - `formatter.py`: just cleans up the markdown.
- `utils/`: auth, sessions, rate limiting, and caching.

## some notes
- **Auth**: JWT-based. Tokens expire in 1 hour.
- **Rate Limit**: 10 requests per minute per user.
- **Cache**: It caches results for 30 mins so we don't spam the Gemini API.
- **Sessions**: Basic in-memory session tracking.
