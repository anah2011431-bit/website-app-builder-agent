from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Website App Builder Agent",
    description="Build websites and apps from natural language prompts",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class BuildRequest(BaseModel):
    prompt: str
    tone: str = "modern"
    style: str = "light"

# Response model
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

# ==================== UTILITY FUNCTIONS ====================

def classify_prompt(prompt: str) -> str:
    """Detect app type from prompt."""
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
    """Extract city name from prompt."""
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
    """Fetch city geocoding data from Nominatim."""
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
                "display_name": data.get("display_name", city)
            }
    except Exception as e:
        logger.warning(f"Failed to fetch city data for {city}: {e}")
    
    return {"city": city}

def get_weather(lat: float, lon: float) -> str:
    """Fetch weather from Open-Meteo."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            temp = current.get("temperature_2m", "N/A")
            return f"{temp}°C"
    except Exception as e:
        logger.warning(f"Failed to fetch weather: {e}")
    
    return "N/A"

def generate_app_spec(prompt: str, app_type: str, tone: str, style: str) -> dict:
    """Generate app specification based on type."""
    
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

# ==================== API ENDPOINTS ====================

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Backend is running"}

@app.post("/api/build", response_model=BuildResponse, tags=["Builder"])
async def build_app(request: BuildRequest):
    """
    Build an app spec from a prompt.
    
    This endpoint:
    1. Classifies the prompt to detect app type
    2. Extracts location if available
    3. Fetches optional weather data
    4. Generates app spec based on template
    
    Returns a structured response with pages, sections, and metadata.
    """
    
    if not request.prompt or len(request.prompt.strip()) < 5:
        raise HTTPException(status_code=400, detail="Prompt must be at least 5 characters")
    
    # Classify app type
    app_type = classify_prompt(request.prompt)
    logger.info(f"Classified prompt as: {app_type}")
    
    # Extract city and fetch optional data
    city = extract_city(request.prompt)
    location = None
    
    if city:
        city_data = get_city_data(city)
        weather = "N/A"
        
        if "lat" in city_data and "lon" in city_data:
            weather = get_weather(city_data["lat"], city_data["lon"])
        
        location = {
            "city": city_data.get("city", city),
            "weather": weather
        }
        logger.info(f"Enriched with location: {location}")
    
    # Generate app spec
    spec = generate_app_spec(request.prompt, app_type, request.tone, request.style)
    
    response = BuildResponse(
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
    
    logger.info(f"Generated spec for: {response.title}")
    return response

@app.get("/api/templates", tags=["Templates"])
async def list_templates():
    """List available app templates."""
    return {
        "templates": [
            {
                "id": "landing-page",
                "name": "Landing Page",
                "description": "Modern conversion-focused homepage",
            },
            {
                "id": "dashboard",
                "name": "Analytics Dashboard",
                "description": "Real-time metrics and visualizations",
            },
            {
                "id": "portfolio",
                "name": "Portfolio",
                "description": "Showcase your work and experience",
            },
            {
                "id": "ecommerce",
                "name": "E-Commerce",
                "description": "Online store and product catalog",
            },
            {
                "id": "blog",
                "name": "Blog",
                "description": "Content publishing platform",
            },
            {
                "id": "app",
                "name": "Web App",
                "description": "Interactive web application",
            },
        ]
    }

# ==================== ROOT ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": "Website App Builder Agent",
        "version": "0.1.0",
        "docs": "/docs",
        "api": "/api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
