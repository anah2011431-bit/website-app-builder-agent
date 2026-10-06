from typing import Any


def generate_fallback_spec(
    app_type: str,
    tone: str,
    style: str,
) -> dict[str, Any]:
    """
    Generate a deterministic AppSpec when local AI is unavailable
    or produces an invalid response.
    """

    specs = {
        "landing-page": {
            "title": "Premium Landing Page",
            "pages": ["home", "features", "pricing", "contact"],
            "sections": ["hero", "features", "testimonials", "cta"],
            "hero_headline": "Build Your Digital Presence",
            "hero_text": "Launch fast. Grow faster. Convert better.",
        },
        "dashboard": {
            "title": "Analytics Dashboard",
            "pages": ["overview", "analytics", "settings", "export"],
            "sections": ["metrics", "charts", "tables", "filters"],
            "hero_headline": "Your Data, Visualized",
            "hero_text": "Real-time insights at a glance.",
        },
        "portfolio": {
            "title": "Creative Portfolio",
            "pages": ["home", "gallery", "about", "contact"],
            "sections": ["featured work", "testimonials", "bio", "cta"],
            "hero_headline": "Showcase Your Best Work",
            "hero_text": "Professional portfolio that converts.",
        },
        "ecommerce": {
            "title": "Online Store",
            "pages": ["home", "products", "cart", "checkout"],
            "sections": ["hero", "featured", "categories", "trust"],
            "hero_headline": "Shop with Confidence",
            "hero_text": "Quality products. Fast shipping.",
        },
        "blog": {
            "title": "Content Hub",
            "pages": ["home", "posts", "about", "subscribe"],
            "sections": ["featured", "latest posts", "categories", "newsletter"],
            "hero_headline": "Stories Worth Reading",
            "hero_text": "Insights, tips, and inspiration.",
        },
        "app": {
            "title": "Web App Prototype",
            "pages": ["dashboard", "features", "settings", "help"],
            "sections": ["ui components", "forms", "data tables", "notifications"],
            "hero_headline": "Powerful, Intuitive Interface",
            "hero_text": "Built for productivity.",
        },
    }

    selected = specs.get(app_type, specs["landing-page"])

    return {
        "title": selected["title"],
        "app_type": app_type if app_type in specs else "landing-page",
        "theme": f"{tone} {style}",
        "style": style,
        "pages": selected["pages"],
        "sections": selected["sections"],
        "hero_headline": selected["hero_headline"],
        "hero_text": selected["hero_text"],
    }
