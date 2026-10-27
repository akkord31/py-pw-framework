from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestCaseStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class TestStep(BaseModel):
    __test__ = False

    model_config = ConfigDict(extra="forbid")

    number: int = Field(ge=1)
    action: str = Field(min_length=1)
    expected_result: str = Field(min_length=1)
    test_data: str | None = None


class TestCaseVersion(BaseModel):
    __test__ = False

    model_config = ConfigDict(extra="forbid")

    number: int = Field(ge=1)
    updated_at: datetime
    updated_by: str = Field(min_length=1)
    changelog: str = Field(min_length=1)


class TestCase(BaseModel):
    __test__ = False

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^TMS-\d{4}$")
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: Priority
    status: TestCaseStatus
    tags: list[str] = Field(default_factory=list)
    preconditions: list[str] = Field(default_factory=list)
    steps: list[TestStep] = Field(min_length=1)
    version: TestCaseVersion
    created_at: datetime
    updated_at: datetime
    owner: str = Field(min_length=1)
    component: str = Field(min_length=1)


class TestCasePage(BaseModel):
    __test__ = False

    model_config = ConfigDict(extra="forbid")

    items: list[TestCase]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


__all__ = [
    "Priority",
    "TestCase",
    "TestCasePage",
    "TestCaseStatus",
    "TestCaseVersion",
    "TestStep",
]
