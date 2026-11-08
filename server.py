from datetime import date

from mcp.server import MCPServer


mcp = MCPServer("Company HR Assistant")


employee = {
    "id": 101,
    "name": "Inder",
    "department": "Engineering",
    "remaining_leaves": 8
}

leave_requests = []


def validate_leave_request(
    start_date: str,
    end_date: str,
    reason: str
):
    """Validate leave request details."""

    if not isinstance(start_date, str):
        raise ValueError("Start date must be a string.")

    if not isinstance(end_date, str):
        raise ValueError("End date must be a string.")

    if not isinstance(reason, str):
        raise ValueError("Leave reason must be a string.")

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

    except ValueError:
        raise ValueError(
            "Dates must be valid YYYY-MM-DD dates."
        )

    if end < start:
        raise ValueError(
            "End date cannot be before start date."
        )

    cleaned_reason = reason.strip()

    invalid_reasons = {
        "",
        "not specified",
        "none",
        "n/a",
        "no reason",
        "unknown",
        "not provided"
    }

    if cleaned_reason.lower() in invalid_reasons:
        raise ValueError(
            "A valid leave reason is required. "
            "Placeholder reasons are not accepted."
        )

    return cleaned_reason


@mcp.tool()
def get_employee_details() -> dict:
    """Get the employee's basic details."""

    return employee


@mcp.tool()
def calculate_leave_balance() -> str:
    """Check the employee's remaining leave balance."""

    return (
        f"{employee['name']} has "
        f"{employee['remaining_leaves']} leaves remaining."
    )



@mcp.tool()
def create_leave_request(
    start_date: str,
    end_date: str,
    reason: str
) -> dict:
    """Submit a leave request after validation."""

    cleaned_reason = validate_leave_request(
        start_date,
        end_date,
        reason
    )

    request = {
        "employee_id": employee["id"],
        "start_date": start_date,
        "end_date": end_date,
        "reason": cleaned_reason,
        "status": "Pending"
    }
    leave_requests.append(request)
    return request

@mcp.resource("hr://policies/leave")
def get_leave_policy() -> str:
    """Provide the company's leave policy."""

    return """
    COMPANY LEAVE POLICY
    1. Employees receive 20 annual leaves.
    2. Leave requests should be submitted in advance.
    3. Approval depends on the reporting manager.
    4. Emergency leaves should be reported immediately.
    """

@mcp.prompt()
def explain_leave_eligibility(employee_name: str) -> str:
    """Create a reusable prompt for explaining leave eligibility."""

    return f"""
    You are an HR assistant.
    Explain leave eligibility to {employee_name}.
    Use the company leave policy.
    Keep the explanation simple and professional.
    """

if __name__ == "__main__":
    mcp.run()