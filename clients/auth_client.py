from __future__ import annotations

import allure

from framework.api.base_client import BaseClient
from models.auth import LoginRequest, LoginResponse, TokenResponse


class AuthClient(BaseClient):
    @allure.step("POST /auth/login")
    def login(self, credentials: LoginRequest) -> LoginResponse:
        response = self.post("/auth/login", json=credentials.model_dump())
        return LoginResponse.model_validate(response.json())

    @allure.step("POST /auth/logout")
    def logout(self) -> None:
        self.post("/auth/logout")
        self.clear_token()

    @allure.step("POST /auth/refresh")
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        response = self.post("/auth/refresh", json={"refresh_token": refresh_token})
        return TokenResponse.model_validate(response.json())
