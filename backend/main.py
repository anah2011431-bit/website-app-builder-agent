from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os
from typing import Optional
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Website App Builder Agent",
    description="Build websites and apps from natural language prompts",
    version="0.1.0",
)

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BuildRequest(BaseModel):
    prompt: str
    tone: str = "modern"
    style: str = "light"


class BuildResponse(BaseModel):
    title: str
    app_type: str
    theme: str
    style: str
    pages: list
    sections: list
    hero_headline: str
    hero_text: str
    location: Optional[dict] = None


def classify_prompt(prompt: str) -> str:
    lower = prompt.lower()

    if any(word in lower for word in ["dashboard", "analytics", "metrics", "chart"]):
        return "dashboard"
    if any(word in lower for word in ["portfolio", "photographer", "artist", "gallery"]):
        return "portfolio"
    if any(word in lower for word in ["ecommerce", "shop", "store", "product"]):
        return "ecommerce"
    if any(word in lower for word in ["blog", "article", "news", "post"]):
        return "blog"
    if any(word in lower for word in ["app", "mobile", "prototype"]):
        return "app"

    return "landing-page"


def extract_city(prompt: str) -> Optional[str]:
    cities = {
        "london": "London",
        "lagos": "Lagos",
        "nairobi": "Nairobi",
        "new york": "New York",
        "san francisco": "San Francisco",
        "tokyo": "Tokyo",
        "berlin": "Berlin",
        "toronto": "Toronto",
        "sydney": "Sydney",
        "paris": "Paris",
    }

    lower = prompt.lower()
    for key, value in cities.items():
        if key in lower:
            return value

    return None


def get_city_data(city: str) -> dict:
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        headers = {"User-Agent": "website-app-builder-agent"}
        response = requests.get(url, timeout=5, headers=headers)

        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return {
                "city": city,
                "lat": float(data.get("lat", 0)),
                "lon": float(data.get("lon", 0)),
                "display_name": data.get("display_name", city),
            }
    except Exception as exc:
        logger.warning(f"Failed to fetch city data for {city}: {exc}")

    return {"city": city}


def get_weather(lat: float, lon: float) -> str:
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        )
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            temperature = current.get("temperature_2m", "N/A")
            return f"{temperature}°C"
    except Exception as exc:
        logger.warning(f"Failed to fetch weather: {exc}")

    return "N/A"


def generate_app_spec(prompt: str, app_type: str, tone: str, style: str) -> dict:
    specs = {
        "landing-page": {
            "title": "Premium Landing Page",
            "theme": f"{tone} {style}",
            "pages": ["home", "features", "pricing", "contact"],
            "sections": ["hero", "features", "testimonials", "cta"],
            "hero_headline": "Build Your Digital Presence",
            "hero_text": "Launch fast. Grow faster. Convert better.",
        },
        "dashboard": {
            "title": "Analytics Dashboard",
            "theme": f"{tone} {style}",
            "pages": ["overview", "analytics", "settings", "export"],
            "sections": ["metrics", "charts", "tables", "filters"],
            "hero_headline": "Your Data, Visualized",
            "hero_text": "Real-time insights at a glance.",
        },
        "portfolio": {
            "title": "Creative Portfolio",
            "theme": f"{tone} {style}",
            "pages": ["home", "gallery", "about", "contact"],
            "sections": ["featured work", "testimonials", "bio", "cta"],
            "hero_headline": "Showcase Your Best Work",
            "hero_text": "Professional portfolio that converts.",
        },
        "ecommerce": {
            "title": "Online Store",
            "theme": f"{tone} {style}",
            "pages": ["home", "products", "cart", "checkout"],
            "sections": ["hero", "featured", "categories", "trust"],
            "hero_headline": "Shop with Confidence",
            "hero_text": "Quality products. Fast shipping.",
        },
        "blog": {
            "title": "Content Hub",
            "theme": f"{tone} {style}",
            "pages": ["home", "posts", "about", "subscribe"],
            "sections": ["featured", "latest posts", "categories", "newsletter"],
            "hero_headline": "Stories Worth Reading",
            "hero_text": "Insights, tips, and inspiration.",
        },
        "app": {
            "title": "Web App Prototype",
            "theme": f"{tone} {style}",
            "pages": ["dashboard", "features", "settings", "help"],
            "sections": ["ui components", "forms", "data tables", "notifications"],
            "hero_headline": "Powerful, Intuitive Interface",
            "hero_text": "Built for productivity.",
        },
    }

    return specs.get(app_type, specs["landing-page"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Backend is healthy"}


@app.post("/api/build", response_model=BuildResponse)
async def build_app(request: BuildRequest):
    if not request.prompt or len(request.prompt.strip()) < 5:
        raise HTTPException(status_code=400, detail="Prompt must be at least 5 characters")

    app_type = classify_prompt(request.prompt)
    city = extract_city(request.prompt)
    location = None

    if city:
        city_data = get_city_data(city)
        weather = "N/A"
        if "lat" in city_data and "lon" in city_data:
            weather = get_weather(city_data["lat"], city_data["lon"])
        location = {
            "city": city_data.get("city", city),
            "weather": weather,
        }

    spec = generate_app_spec(request.prompt, app_type, request.tone, request.style)

    return BuildResponse(
        title=spec["title"],
        app_type=app_type,
        theme=spec["theme"],
        style=request.style,
        pages=spec["pages"],
        sections=spec["sections"],
        hero_headline=spec["hero_headline"],
        hero_text=spec["hero_text"],
        location=location,
    )


@app.get("/api/templates")
async def list_templates():
    return {
        "templates": [
            {"id": "landing-page", "name": "Landing Page", "description": "Modern conversion-focused homepage"},
            {"id": "dashboard", "name": "Analytics Dashboard", "description": "Real-time metrics and visualizations"},
            {"id": "portfolio", "name": "Portfolio", "description": "Showcase your work and experience"},
            {"id": "ecommerce", "name": "E-Commerce", "description": "Online store and product catalog"},
            {"id": "blog", "name": "Blog", "description": "Content publishing platform"},
            {"id": "app", "name": "Web App", "description": "Interactive web application"},
        ]
    }


@app.get("/")
async def root():
    return {
        "name": "Website App Builder Agent",
        "version": "0.1.0",
        "docs": "/docs",
        "api": "/api",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", "8000")),
    )


# end of file
