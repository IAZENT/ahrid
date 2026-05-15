"""Marshmallow schemas + input sanitisation helpers."""
from __future__ import annotations

import re

import bleach
from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, validates_schema

JOB_ROLE_CHOICES = (
    "receptionist", "accountant", "hr", "it",
    "finance", "sales", "management", "other",
)

# Min 12 chars · 1 upper · 1 lower · 1 digit · 1 special.
PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$"
)

USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,32}$")


def sanitize_string(value: str | None) -> str | None:
    if value is None:
        return None
    return bleach.clean(str(value), tags=[], strip=True).strip()


VISUAL_HTML_ALLOWED_TAGS = [
    "div", "p", "span", "table", "tr", "td", "th", "thead", "tbody",
    "img", "a", "h1", "h2", "h3", "strong", "em", "br", "ul", "li",
    "button", "input", "label", "form", "style",
]
VISUAL_HTML_ALLOWED_ATTRS = {
    "*": ["class", "id", "style"],
    "a": ["href"],
    "img": ["src", "alt"],
}


def _strip_dangerous_urls(attrs, new=False):  # noqa: ARG001
    href = attrs.get((None, "href"))
    if href and href.lower().strip().startswith(("javascript:", "data:", "vbscript:")):
        return None
    return attrs


def sanitize_visual_html(raw: str | None) -> str | None:
    if raw is None or raw == "":
        return raw
    cleaned = bleach.clean(
        str(raw),
        tags=VISUAL_HTML_ALLOWED_TAGS,
        attributes=VISUAL_HTML_ALLOWED_ATTRS,
        strip=True,
        strip_comments=True,
    )
    cleaned = bleach.linkify(cleaned, callbacks=[_strip_dangerous_urls], parse_email=False)
    return cleaned


def _password_validator(value: str) -> None:
    if not PASSWORD_RE.match(value or ""):
        raise ValidationError(
            "Password must be at least 12 chars and include uppercase, "
            "lowercase, digit, and special character."
        )


class _BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE


class LoginSchema(_BaseSchema):
    identifier = fields.String(required=False, validate=validate.Length(min=1, max=254))
    email = fields.String(required=False, validate=validate.Length(min=1, max=254))
    password = fields.String(required=True, validate=validate.Length(min=1, max=200))

    @validates_schema
    def _normalise(self, data: dict, **_) -> None:
        ident = data.get("identifier") or data.get("email")
        if not ident:
            raise ValidationError({"identifier": ["identifier or email is required"]})
        data["identifier"] = ident.strip().lower()
        data.pop("email", None)
