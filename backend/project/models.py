"""
Project Manifest Models

Defines Pydantic models for controlled project manifest representation.
Compatible with existing AppSpec but adds structure for P3.1+ generation.

Uses Pydantic 2.9.2 with field_validator and proper type constraints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ProjectTheme(BaseModel):
    """Theme configuration for a project."""

    name: str = Field(..., min_length=1, max_length=100)
    style: str = Field(..., min_length=1, max_length=100)
    primary_color: Optional[str] = Field(
        None,
        min_length=0,
        max_length=50,
    )
    secondary_color: Optional[str] = Field(
        None,
        min_length=0,
        max_length=50,
    )

    model_config = {"extra": "forbid"}

    @field_validator("name", "style", "primary_color", "secondary_color")
    @classmethod
    def validate_no_template_injection(cls, v):
        """Reject template injection patterns."""
        if v is None:
            return v

        dangerous_patterns = ["${", "{{", "}}", "<%", "<?"]

        for pattern in dangerous_patterns:
            if pattern in v:
                raise ValueError(f"Theme values cannot contain '{pattern}'")

        return v


class ProjectNavigation(BaseModel):
    """Navigation structure for a project."""

    items: List[str] = Field(..., min_length=1, max_length=20)
    logo_text: Optional[str] = Field(
        None,
        min_length=0,
        max_length=100,
    )

    model_config = {"extra": "forbid"}

    @field_validator("items", mode="before")
    @classmethod
    def validate_items(cls, v):
        """Ensure all navigation items are valid."""
        if not isinstance(v, list):
            raise ValueError("items must be a list")

        if len(v) > 20:
            raise ValueError("items list cannot exceed 20 items")

        validated = []
        for i, item in enumerate(v):
            if not isinstance(item, str):
                raise ValueError(f"items[{i}] must be a string")

            item_stripped = item.strip()
            if not item_stripped:
                raise ValueError(f"items[{i}] cannot be empty")

            if len(item_stripped) > 100:
                raise ValueError(f"items[{i}] cannot exceed 100 characters")

            if ".." in item_stripped or item_stripped.startswith("~"):
                raise ValueError(f"items[{i}] cannot contain path traversal")

            validated.append(item_stripped)

        return validated


class ProjectComponent(BaseModel):
    """A component within a section."""

    component_type: str = Field(..., min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=0, max_length=100)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}

    @field_validator("component_type", "name")
    @classmethod
    def validate_no_paths(cls, v):
        """Reject filesystem paths and dangerous patterns."""
        if v is None:
            return v

        if ".." in v or v.startswith("~") or "/" in v or "\\" in v:
            raise ValueError("component_type/name cannot contain paths")

        if any(p in v for p in ["${", "{{", "<%"]):
            raise ValueError(
                "component_type/name cannot contain template patterns"
            )

        return v

    @field_validator("properties", mode="before")
    @classmethod
    def validate_properties(cls, v):
        """Validate and bound component properties recursively."""
        if v is None:
            return {}

        if not isinstance(v, dict):
            raise ValueError("properties must be a dictionary")

        cls._validate_dict_bounded(v, depth=3, max_size=100)

        return v

    @staticmethod
    def _validate_dict_bounded(
        obj: Any, depth: int = 3, max_size: int = 100, current_depth: int = 0
    ) -> None:
        """Recursively validate dict/list depth and size bounds."""
        if current_depth > depth:
            raise ValueError(
                f"Properties nesting exceeds maximum depth of {depth}"
            )

        if isinstance(obj, dict):
            if len(obj) > max_size:
                raise ValueError(
                    f"Dictionary size exceeds maximum of {max_size}"
                )
            for value in obj.values():
                ProjectComponent._validate_dict_bounded(
                    value,
                    depth=depth,
                    max_size=max_size,
                    current_depth=current_depth + 1,
                )
        elif isinstance(obj, list):
            if len(obj) > max_size:
                raise ValueError(
                    f"List size exceeds maximum of {max_size}"
                )
            for item in obj:
                ProjectComponent._validate_dict_bounded(
                    item,
                    depth=depth,
                    max_size=max_size,
                    current_depth=current_depth + 1,
                )


class ProjectSection(BaseModel):
    """A section within a page."""

    section_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    components: List[ProjectComponent] = Field(
        default_factory=list,
        max_length=50,
    )
    description: Optional[str] = Field(None, max_length=500)

    model_config = {"extra": "forbid"}

    @field_validator("section_id", "name")
    @classmethod
    def validate_identifiers(cls, v):
        """Validate section identifiers."""
        if not v:
            raise ValueError("section identifiers cannot be empty")

        if ".." in v or v.startswith("~") or "/" in v or "\\" in v:
            raise ValueError("section identifiers cannot contain paths")

        if any(p in v for p in ["${", "{{", "<%"]):
            raise ValueError("section identifiers cannot contain templates")

        return v


class ProjectPage(BaseModel):
    """A page within a project."""

    page_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    path: str = Field(..., min_length=1, max_length=100)
    sections: List[ProjectSection] = Field(
        default_factory=list,
        max_length=100,
    )
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)

    model_config = {"extra": "forbid"}

    @field_validator("page_id", "name")
    @classmethod
    def validate_identifiers(cls, v):
        """Validate page identifiers (not paths)."""
        if not v:
            raise ValueError("page identifiers cannot be empty")

        if ".." in v or v.startswith("~") or "/" in v or "\\" in v:
            raise ValueError(
                "page identifiers cannot contain filesystem paths"
            )

        if any(p in v for p in ["${", "{{", "<%"]):
            raise ValueError("page identifiers cannot contain templates")

        return v

    @field_validator("path")
    @classmethod
    def validate_route_path(cls, v):
        """Validate route path. Valid: /, /about, /pricing. Invalid: ../secret."""
        if not v:
            raise ValueError("path cannot be empty")

        if not v.startswith("/"):
            raise ValueError("path must start with /")

        if "\\" in v:
            raise ValueError("path cannot contain backslashes")

        if ".." in v:
            raise ValueError("path cannot contain path traversal (..)")

        if v.startswith("~"):
            raise ValueError("path cannot start with ~")

        import re

        if not re.match(r"^/[a-zA-Z0-9/_-]*$", v):
            raise ValueError(
                "path contains invalid characters. Use only alphanumeric, /, -, _"
            )

        if any(p in v for p in ["${", "{{", "<%", "`", "|", ";"]):
            raise ValueError("path cannot contain template or shell patterns")

        return v


class ProjectManifest(BaseModel):
    """Controlled project manifest. Structure is deterministic based on app_type."""

    manifest_id: str = Field(..., min_length=1, max_length=100)
    app_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    theme: ProjectTheme
    navigation: ProjectNavigation
    pages: List[ProjectPage] = Field(..., min_length=1, max_length=100)
    version: str = Field(default="1.0.0", min_length=1, max_length=50)
    generation_mode: Optional[str] = Field(
        default="deterministic",
        min_length=1,
        max_length=50,
    )

    model_config = {"extra": "forbid"}

    @field_validator("app_type")
    @classmethod
    def validate_app_type(cls, v):
        """Validate app type against allowed values."""
        allowed_types = {
            "landing-page",
            "dashboard",
            "portfolio",
            "ecommerce",
            "blog",
            "app",
        }

        if v not in allowed_types:
            raise ValueError(
                f"app_type must be one of {allowed_types}, got '{v}'"
            )

        return v

    @field_validator("title", "manifest_id")
    @classmethod
    def validate_no_template_injection(cls, v):
        """Reject template injection patterns in manifest metadata."""
        if not v:
            return v

        dangerous_patterns = ["${", "{{", "}}", "<%", "<?"]

        for pattern in dangerous_patterns:
            if pattern in v:
                raise ValueError(
                    f"Manifest values cannot contain '{pattern}'"
                )

        return v

    @field_validator("pages")
    @classmethod
    def validate_pages(cls, v):
        """Ensure pages list is valid and non-empty."""
        if not v:
            raise ValueError("manifest must have at least one page")

        return v
