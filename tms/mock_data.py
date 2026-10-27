from __future__ import annotations

from datetime import datetime, timezone

from tms.models import (
    Priority,
    TestCase,
    TestCaseStatus,
    TestCaseVersion,
    TestStep,
)


def _steps(
    *items: tuple[str, str, str | None],
) -> list[TestStep]:
    return [
        TestStep(
            number=number,
            action=action,
            expected_result=expected,
            test_data=data,
        )
        for number, (action, expected, data) in enumerate(items, start=1)
    ]


def _case(
    *,
    case_id: str,
    title: str,
    description: str,
    priority: Priority,
    status: TestCaseStatus,
    tags: list[str],
    component: str,
    owner: str,
    preconditions: list[str],
    steps: list[TestStep],
    version: int,
    changelog: str,
    created_at: datetime,
    updated_at: datetime,
) -> TestCase:
    return TestCase(
        id=case_id,
        title=title,
        description=description,
        priority=priority,
        status=status,
        tags=tags,
        preconditions=preconditions,
        steps=steps,
        version=TestCaseVersion(
            number=version,
            updated_at=updated_at,
            updated_by="qa.lead@example.test",
            changelog=changelog,
        ),
        created_at=created_at,
        updated_at=updated_at,
        owner=owner,
        component=component,
    )


def _utc(year: int, month: int, day: int, hour: int = 9) -> datetime:
    return datetime(year, month, day, hour, tzinfo=timezone.utc)


MOCK_TEST_CASES: tuple[TestCase, ...] = (
    _case(
        case_id="TMS-1001",
        title="Successful login with standard user",
        description=(
            "A registered customer can authenticate with valid credentials and "
            "is redirected to the product catalogue."
        ),
        priority=Priority.HIGH,
        status=TestCaseStatus.APPROVED,
        tags=["authentication", "smoke", "login"],
        component="Authentication",
        owner="qa.auth@example.test",
        preconditions=["A standard user account exists and is active."],
        steps=_steps(
            (
                "Open the login page.",
                "The login form is displayed.",
                None,
            ),
            (
                "Enter a valid username and password.",
                "Both fields contain the supplied values.",
                "standard_user / valid password",
            ),
            (
                "Click Login.",
                "The product catalogue is displayed and the user menu is visible.",
                None,
            ),
        ),
        version=3,
        changelog="Clarified post-login expected result.",
        created_at=_utc(2025, 11, 4),
        updated_at=_utc(2026, 1, 15),
    ),
    _case(
        case_id="TMS-1002",
        title="Locked user cannot log in",
        description=(
            "A locked account receives an explicit error and remains on the login page."
        ),
        priority=Priority.HIGH,
        status=TestCaseStatus.APPROVED,
        tags=["authentication", "negative", "login"],
        component="Authentication",
        owner="qa.auth@example.test",
        preconditions=["A locked user account exists."],
        steps=_steps(
            (
                "Enter the locked user's credentials.",
                "The credentials are accepted into the form.",
                "locked_out_user / valid password",
            ),
            (
                "Click Login.",
                "An error explaining that the user is locked out is displayed.",
                None,
            ),
            (
                "Inspect the current URL.",
                "The login page URL is unchanged.",
                None,
            ),
        ),
        version=2,
        changelog="Added URL assertion.",
        created_at=_utc(2025, 11, 6),
        updated_at=_utc(2026, 1, 14),
    ),
    _case(
        case_id="TMS-1003",
        title="Invalid password shows authentication error",
        description=(
            "An invalid password for an existing login is rejected without "
            "revealing whether the username exists."
        ),
        priority=Priority.MEDIUM,
        status=TestCaseStatus.APPROVED,
        tags=["authentication", "negative", "login"],
        component="Authentication",
        owner="qa.auth@example.test",
        preconditions=["A standard user account exists."],
        steps=_steps(
            (
                "Enter a valid username and an invalid password.",
                "The login form contains the supplied username.",
                "standard_user / invalid password",
            ),
            (
                "Click Login.",
                "A generic username-or-password error is displayed.",
                None,
            ),
            (
                "Read the error message.",
                "The message does not confirm that the username exists.",
                None,
            ),
        ),
        version=2,
        changelog="Added account-enumeration check.",
        created_at=_utc(2025, 11, 7),
        updated_at=_utc(2026, 1, 12),
    ),
    _case(
        case_id="TMS-1004",
        title="Add a product to the cart",
        description=(
            "A customer can add a catalogue product to the cart and sees the "
            "cart badge update."
        ),
        priority=Priority.CRITICAL,
        status=TestCaseStatus.APPROVED,
        tags=["cart", "smoke"],
        component="Cart",
        owner="qa.cart@example.test",
        preconditions=["The customer is logged in and on the catalogue."],
        steps=_steps(
            (
                "Select a product and click Add to cart.",
                "The product is added and the cart badge shows one item.",
                "Sauce Labs Backpack",
            ),
            (
                "Open the cart.",
                "The selected product is listed once.",
                None,
            ),
        ),
        version=4,
        changelog="Updated cart badge expectation.",
        created_at=_utc(2025, 10, 20),
        updated_at=_utc(2026, 1, 20),
    ),
    _case(
        case_id="TMS-1005",
        title="Remove a product from the cart",
        description=(
            "A customer can remove a cart item and the cart badge is hidden "
            "when the cart becomes empty."
        ),
        priority=Priority.HIGH,
        status=TestCaseStatus.APPROVED,
        tags=["cart", "regression"],
        component="Cart",
        owner="qa.cart@example.test",
        preconditions=["The cart contains exactly one product."],
        steps=_steps(
            (
                "Click Remove on the cart item.",
                "The item disappears from the cart.",
                None,
            ),
            (
                "Inspect the cart badge.",
                "The cart badge is no longer displayed.",
                None,
            ),
        ),
        version=2,
        changelog="Added empty-badge assertion.",
        created_at=_utc(2025, 10, 22),
        updated_at=_utc(2026, 1, 11),
    ),
    _case(
        case_id="TMS-1006",
        title="Checkout with a valid payment method",
        description=(
            "A customer completes checkout with valid shipping and payment "
            "details and receives an order confirmation."
        ),
        priority=Priority.CRITICAL,
        status=TestCaseStatus.APPROVED,
        tags=["checkout", "payment", "smoke"],
        component="Checkout",
        owner="qa.checkout@example.test",
        preconditions=["The cart contains at least one product."],
        steps=_steps(
            (
                "Open checkout and enter valid shipping details.",
                "The checkout form accepts the shipping details.",
                "Test Street 1 / 12345 / Test City",
            ),
            (
                "Enter a valid payment method and click Finish.",
                "The order is accepted.",
                "Visa ending 4242",
            ),
            (
                "Read the confirmation page.",
                "A confirmation message and order total are displayed.",
                None,
            ),
        ),
        version=5,
        changelog="Added confirmation-total check.",
        created_at=_utc(2025, 9, 30),
        updated_at=_utc(2026, 1, 21),
    ),
    _case(
        case_id="TMS-1007",
        title="Checkout with a declined card",
        description=(
            "A declined payment keeps the checkout page open and shows a "
            "recoverable error."
        ),
        priority=Priority.HIGH,
        status=TestCaseStatus.APPROVED,
        tags=["checkout", "payment", "negative"],
        component="Checkout",
        owner="qa.checkout@example.test",
        preconditions=["The cart contains one product and valid shipping data."],
        steps=_steps(
            (
                "Enter a declined card and click Finish.",
                "The payment is rejected with a readable error.",
                "Declined test card",
            ),
            (
                "Inspect the checkout page.",
                "The checkout page remains open and the cart is unchanged.",
                None,
            ),
        ),
        version=3,
        changelog="Added cart-preservation assertion.",
        created_at=_utc(2025, 10, 1),
        updated_at=_utc(2026, 1, 18),
    ),
    _case(
        case_id="TMS-1008",
        title="Product search returns matching items",
        description=(
            "The catalogue search filters products by a case-insensitive title "
            "fragment."
        ),
        priority=Priority.MEDIUM,
        status=TestCaseStatus.APPROVED,
        tags=["catalog", "search"],
        component="Catalog",
        owner="qa.catalog@example.test",
        preconditions=["The customer is on the catalogue page."],
        steps=_steps(
            (
                "Enter a product-name fragment in the search field.",
                "The search field contains the fragment.",
                "backpack",
            ),
            (
                "Submit the search.",
                "Only products whose titles match the fragment are displayed.",
                None,
            ),
        ),
        version=2,
        changelog="Clarified case-insensitive matching.",
        created_at=_utc(2025, 12, 2),
        updated_at=_utc(2026, 1, 9),
    ),
    _case(
        case_id="TMS-1009",
        title="Search with no results shows an empty state",
        description=(
            "A search that matches no products displays a clear empty state "
            "instead of an empty grid."
        ),
        priority=Priority.LOW,
        status=TestCaseStatus.DRAFT,
        tags=["catalog", "search", "empty-state"],
        component="Catalog",
        owner="qa.catalog@example.test",
        preconditions=["The customer is on the catalogue page."],
        steps=_steps(
            (
                "Search for a value that cannot match a product.",
                "No product cards are rendered.",
                "zzzz-no-such-product",
            ),
            (
                "Inspect the results area.",
                "A no-results message is displayed.",
                None,
            ),
        ),
        version=1,
        changelog="Initial draft for empty-state coverage.",
        created_at=_utc(2026, 1, 5),
        updated_at=_utc(2026, 1, 5),
    ),
    _case(
        case_id="TMS-1010",
        title="Password reset sends a reset message",
        description=(
            "A user can request a password reset and receives a confirmation "
            "without exposing the reset token in the UI."
        ),
        priority=Priority.HIGH,
        status=TestCaseStatus.APPROVED,
        tags=["authentication", "email", "login"],
        component="Authentication",
        owner="qa.auth@example.test",
        preconditions=["A standard user account exists."],
        steps=_steps(
            (
                "Open the password reset form and enter the account email.",
                "The form accepts the email address.",
                "standard_user@example.test",
            ),
            (
                "Submit the reset request.",
                "A neutral confirmation message is displayed.",
                None,
            ),
            (
                "Inspect the confirmation message.",
                "No password or reset token is displayed in the UI.",
                None,
            ),
        ),
        version=2,
        changelog="Added token-exposure check.",
        created_at=_utc(2025, 12, 10),
        updated_at=_utc(2026, 1, 16),
    ),
    _case(
        case_id="TMS-1011",
        title="Update the profile display name",
        description=(
            "A customer can update the profile display name and sees the new "
            "value after saving."
        ),
        priority=Priority.MEDIUM,
        status=TestCaseStatus.DEPRECATED,
        tags=["profile", "regression"],
        component="Profile",
        owner="qa.profile@example.test",
        preconditions=["The customer is logged in."],
        steps=_steps(
            (
                "Open the profile and change the display name.",
                "The new display name is accepted into the field.",
                "Updated Name",
            ),
            (
                "Save the profile.",
                "A success message is displayed and the new name is visible.",
                None,
            ),
        ),
        version=1,
        changelog="Deprecated after profile redesign.",
        created_at=_utc(2025, 8, 14),
        updated_at=_utc(2026, 1, 3),
    ),
    _case(
        case_id="TMS-1012",
        title="API login returns a bearer token",
        description=(
            "The authentication API returns a bearer token and expiry metadata "
            "for valid credentials."
        ),
        priority=Priority.HIGH,
        status=TestCaseStatus.APPROVED,
        tags=["api", "authentication", "login", "contract"],
        component="Authentication API",
        owner="qa.api@example.test",
        preconditions=["The authentication service is available."],
        steps=_steps(
            (
                "Send a POST /auth/login request with valid credentials.",
                "The response status is 200.",
                "standard_user / valid password",
            ),
            (
                "Inspect the response body.",
                "The body contains access_token, token_type=bearer and expires_in.",
                None,
            ),
            (
                "Inspect the response headers.",
                "No credentials or token values are reflected in error headers.",
                None,
            ),
        ),
        version=3,
        changelog="Added token_type and expiry assertions.",
        created_at=_utc(2025, 12, 18),
        updated_at=_utc(2026, 1, 19),
    ),
)


def get_mock_cases() -> list[TestCase]:
    """Return defensive copies so callers cannot mutate the fixture data."""

    return [case.model_copy(deep=True) for case in MOCK_TEST_CASES]


def get_mock_case(case_id: str) -> TestCase | None:
    for case in MOCK_TEST_CASES:
        if case.id == case_id:
            return case.model_copy(deep=True)
    return None


__all__ = ["MOCK_TEST_CASES", "get_mock_case", "get_mock_cases"]
