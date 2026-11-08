import requests
import os 
from dotenv import load_dotenv
load_dotenv()

webhook_url = os.getenv("webhook_url")
leave_request = {
    "employee_id": 101,
    "employee_name": "Inder",
    "department": "Engineering",
    "leave_days": "2",
    "leave_type": "unpaid",
    "reason": "Personal work"
}
try:
    response = requests.post(
        webhook_url,
        json=leave_request,
        timeout=15
    )
    print("HTTP Status:", response.status_code)
    try:
        data=response.json()
    except ValueError:
        data={"message":response.text}
    if response.status_code == 200:
        print("SUCCESS:", data["message"])
        print("Status:", data.get("status"))
    elif response.status_code == 400:
        print("VALIDATION ERROR:", data)
    else:
        print("SERVER ERROR:", data)
except requests.exceptions.Timeout:
    print("Request timed out!")
except requests.exceptions.RequestException as e:
    print("Connection error:", e)