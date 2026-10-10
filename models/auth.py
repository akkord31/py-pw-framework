from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class LoginResponse(BaseModel):
    """Flexible wrapper"""

    token: str = Field(alias="access_token")
    token_type: str = "bearer"

    model_config = {"populate_by_name": True}
