from __future__ import annotations

import allure

from framework.api.base_client import BaseClient
from framework.api.exceptions import NotFoundError
from models.user import UserCreate, UserResponse, UserUpdate


class UsersClient(BaseClient):
    @allure.step("GET /users/{user_id}")
    def get_user(self, user_id: int) -> UserResponse:
        response = self.get(f"/users/{user_id}")
        return UserResponse.model_validate(response.json())

    @allure.step("GET /users")
    def get_users(self) -> list[UserResponse]:
        response = self.get("/users")
        return [UserResponse.model_validate(u) for u in response.json()]

    @allure.step("POST /users")
    def create_user(self, payload: UserCreate) -> UserResponse:
        response = self.post("/users", json=payload.model_dump())
        return UserResponse.model_validate(response.json())

    @allure.step("PATCH /users/{user_id}")
    def update_user(self, user_id: int, payload: UserUpdate) -> UserResponse:
        response = self.patch(f"/users/{user_id}", json=payload.model_dump(exclude_none=True))
        return UserResponse.model_validate(response.json())

    @allure.step("DELETE /users/{user_id}")
    def delete_user(self, user_id: int) -> None:
        try:
            self.delete(f"/users/{user_id}")
        except NotFoundError:
            pass
