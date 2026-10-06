"""
Project Manifest Generator

Converts AppSpec to ProjectManifest using deterministic templates.
Supports 6 app types with controlled, safe project generation.

Key behavior:
- The manifest ID is unique per generation
- The project STRUCTURE (pages, sections, components) is deterministic
  and based solely on app_type
- AppSpec hero_headline and hero_text are preserved in the manifest description
- No arbitrary source code or Ollama content is included
- This is a controlled, reproducible project representation layer
"""

from typing import Optional, Dict, Any, List
import uuid
import logging

from backend.project.models import (
    ProjectManifest,
    ProjectPage,
    ProjectSection,
    ProjectComponent,
    ProjectTheme,
    ProjectNavigation,
)
from backend.project.validator import ProjectValidator, ValidationError

logger = logging.getLogger(__name__)


class ProjectGenerator:
    """Generates deterministic ProjectManifest from AppSpec."""

    # Deterministic template structure for each app type
    TEMPLATES = {
        "landing-page": {
            "pages": [
                {"id": "home", "name": "Home", "path": "/"},
                {"id": "features", "name": "Features", "path": "/features"},
                {"id": "pricing", "name": "Pricing", "path": "/pricing"},
                {"id": "contact", "name": "Contact", "path": "/contact"},
            ],
            "sections": ["hero", "features", "testimonials", "cta"],
            "components": {
                "hero": ["heading", "subheading", "cta-button"],
                "features": ["feature-card", "feature-list"],
                "testimonials": ["testimonial-card"],
                "cta": ["call-to-action-button"],
            },
            "nav_items": ["Home", "Features", "Pricing", "Contact"],
        },
        "portfolio": {
            "pages": [
                {"id": "home", "name": "Home", "path": "/"},
                {"id": "gallery", "name": "Gallery", "path": "/gallery"},
                {"id": "about", "name": "About", "path": "/about"},
                {"id": "contact", "name": "Contact", "path": "/contact"},
            ],
            "sections": ["featured-work", "testimonials", "bio", "cta"],
            "components": {
                "featured-work": ["work-card", "image-gallery"],
                "testimonials": ["testimonial-card"],
                "bio": ["bio-section"],
                "cta": ["contact-button"],
            },
            "nav_items": ["Home", "Gallery", "About", "Contact"],
        },
        "dashboard": {
            "pages": [
                {"id": "overview", "name": "Overview", "path": "/"},
                {"id": "analytics", "name": "Analytics", "path": "/analytics"},
                {"id": "settings", "name": "Settings", "path": "/settings"},
                {"id": "export", "name": "Export", "path": "/export"},
            ],
            "sections": ["metrics", "charts", "tables", "filters"],
            "components": {
                "metrics": ["metric-card", "kpi-widget"],
                "charts": ["line-chart", "bar-chart", "pie-chart"],
                "tables": ["data-table"],
                "filters": ["filter-widget", "date-picker"],
            },
            "nav_items": ["Overview", "Analytics", "Settings", "Export"],
        },
        "ecommerce": {
            "pages": [
                {"id": "home", "name": "Home", "path": "/"},
                {"id": "products", "name": "Products", "path": "/products"},
                {"id": "cart", "name": "Cart", "path": "/cart"},
                {"id": "checkout", "name": "Checkout", "path": "/checkout"},
            ],
            "sections": ["hero", "featured", "categories", "trust"],
            "components": {
                "hero": ["banner", "search-bar"],
                "featured": ["product-card", "product-grid"],
                "categories": ["category-filter", "category-list"],
                "trust": ["trust-badge", "review-summary"],
            },
            "nav_items": ["Home", "Products", "Cart", "Checkout"],
        },
        "blog": {
            "pages": [
                {"id": "home", "name": "Home", "path": "/"},
                {"id": "posts", "name": "Posts", "path": "/posts"},
                {"id": "about", "name": "About", "path": "/about"},
                {"id": "subscribe", "name": "Subscribe", "path": "/subscribe"},
            ],
            "sections": ["featured", "latest-posts", "categories", "newsletter"],
            "components": {
                "featured": ["featured-post-card"],
                "latest-posts": ["post-card", "post-list"],
                "categories": ["category-tag", "category-list"],
                "newsletter": ["newsletter-signup"],
            },
            "nav_items": ["Home", "Posts", "About", "Subscribe"],
        },
        "app": {
            "pages": [
                {"id": "dashboard", "name": "Dashboard", "path": "/"},
                {"id": "features", "name": "Features", "path": "/features"},
                {"id": "settings", "name": "Settings", "path": "/settings"},
                {"id": "help", "name": "Help", "path": "/help"},
            ],
            "sections": [
                "ui-components",
                "forms",
                "data-tables",
                "notifications",
            ],
            "components": {
                "ui-components": ["button", "input", "dropdown", "modal"],
                "forms": ["form", "input-field", "checkbox", "radio"],
                "data-tables": ["table", "pagination"],
                "notifications": ["alert", "toast", "notification"],
            },
            "nav_items": ["Dashboard", "Features", "Settings", "Help"],
        },
    }

    @classmethod
    def from_appspec(
        cls,
        appspec: Dict[str, Any],
        generation_mode: str = "deterministic",
    ) -> Optional[ProjectManifest]:
        """
        Convert an AppSpec to a ProjectManifest.

        Validates the AppSpec and generates a controlled ProjectManifest
        using deterministic templates for the app_type.

        Args:
            appspec: Dictionary with title, app_type, theme, style, pages, sections, etc.
            generation_mode: "deterministic" or "ollama" (informational/tracking only)

        Returns:
            ProjectManifest if conversion succeeds, None if validation fails.
            
        Notes:
            - The manifest ID is unique per generation (random UUID)
            - The project structure (pages, sections, components) is deterministic
              based on app_type only
            - AppSpec hero_headline/hero_text are preserved in the manifest description
            - No arbitrary code is generated
        """
        try:
            # Validate the AppSpec first
            ProjectValidator.validate_appspec(appspec)

            app_type = appspec.get("app_type", "landing-page")

            # Retrieve template or reject (validator already checked app_type)
            template = cls.TEMPLATES.get(app_type)
            if not template:
                # This should never happen due to validator, but defensive
                raise ValidationError(
                    f"Unsupported app_type '{app_type}'"
                )

            # Generate unique manifest ID
            manifest_id = f"manifest-{uuid.uuid4().hex[:12]}"

            # Extract theme from AppSpec
            theme_str = appspec.get("theme", "modern light")
            style_str = appspec.get("style", "light")

            # Parse theme name from string (e.g., "modern light" -> "modern")
            theme_name = (
                theme_str.split()[0] if theme_str else "modern"
            )

            theme = ProjectTheme(
                name=theme_name,
                style=style_str,
            )

            # Build navigation from template
            navigation = ProjectNavigation(
                items=template["nav_items"],
            )

            # Build pages and sections from deterministic template
            pages = []
            for page_def in template["pages"]:
                page_sections = []

                # Add sections for this page from template
                for section_name in template["sections"]:
                    section_id = section_name.replace(" ", "-")
                    components = []

                    # Add components for this section from template
                    for comp_type in template["components"].get(
                        section_name, []
                    ):
                        components.append(
                            ProjectComponent(
                                component_type=comp_type,
                                name=comp_type.replace("-", " ").title(),
                            )
                        )

                    page_sections.append(
                        ProjectSection(
                            section_id=section_id,
                            name=section_name.replace("-", " ").title(),
                            components=components,
                        )
                    )

                pages.append(
                    ProjectPage(
                        page_id=page_def["id"],
                        name=page_def["name"],
                        path=page_def["path"],
                        sections=page_sections,
                        title=page_def["name"],
                    )
                )

            # Preserve AppSpec hero content in manifest description
            description = (
                f"{appspec.get('hero_headline', '')} - "
                f"{appspec.get('hero_text', '')}"
            ).strip()

            # Create and return the manifest
            manifest = ProjectManifest(
                manifest_id=manifest_id,
                app_type=app_type,
                title=appspec.get("title", "Untitled Project"),
                description=description if description else None,
                theme=theme,
                navigation=navigation,
                pages=pages,
                generation_mode=generation_mode,
            )

            logger.info(
                f"Generated ProjectManifest "
                f"(id={manifest.manifest_id}, app_type={app_type}, "
                f"pages={len(pages)}, generation_mode={generation_mode})"
            )

            return manifest

        except ValidationError as e:
            logger.error(f"AppSpec validation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"ProjectManifest generation failed: {e}")
            return None

    @classmethod
    def get_supported_app_types(cls) -> List[str]:
        """Return the list of supported app types."""
        return sorted(list(cls.TEMPLATES.keys()))

    @classmethod
    def is_supported_app_type(cls, app_type: str) -> bool:
        """Check if an app type is supported."""
        return app_type in cls.TEMPLATES
