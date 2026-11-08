import requests
import os 
from dotenv import load_dotenv
load_dotenv()

webhook_url = os.getenv("webhook_url")

mcp_result = {
    "employee_id": 101,
    "start_date": "2026-11-12",
    "end_date": "2026-11-14",
    "reason": "Personal work",
    "status": "Pending"
}

try:
    response = requests.post(
        webhook_url,
        json=mcp_result,
        timeout=20
    )

    print("HTTP Status:", response.status_code)
    print("Response:", response.text)

except requests.exceptions.RequestException as error:
    print("Connection failed:", error)