# Company HR Assistant — MCP + n8n Integration

An AI-powered HR assistant built using **Python, Gemini, Model Context Protocol (MCP), and n8n**. The project demonstrates how an AI assistant can interact with HR tools through MCP while using n8n for workflow automation, validation, and notifications.

## 🚀 Overview

The Company HR Assistant allows users to interact with HR functionalities through a Gemini-powered AI client.

The application uses MCP to expose HR tools, resources, and prompts to the AI client. Once a leave request is successfully created, the Python client sends the result to an n8n webhook, where the request is processed through an automated workflow.

The project also includes independent webhook and bridge testing scripts to verify communication between Python and n8n.

## 🏗️ Architecture

```mermaid
flowchart TD
    A[User] --> B[Gemini AI Client]
    B --> C[MCP Client]
    C --> D[MCP Server]

    D --> E[HR Tools]
    D --> F[HR Resources]
    D --> G[HR Prompts]

    E --> H[Leave Request Created]
    H --> I[Human Approval]
    I --> J[Python HTTP Request]
    J --> K[n8n Webhook]

    K --> L[Extract Request Data]
    L --> M{Validate Request}

    M -->|Valid| N[Send Email]
    M -->|Invalid| O[Return 400 Response]

    N --> P[Return 200 Response]
```

## 🛠️ Tech Stack

| Technology                   | Purpose                                                    |
| ---------------------------- | ---------------------------------------------------------- |
| Python                       | Core application logic                                     |
| Google Gemini                | AI-powered interaction                                     |
| Model Context Protocol (MCP) | Standardized communication between AI clients and HR tools |
| n8n                          | Workflow automation and orchestration                      |
| Requests                     | HTTP communication with n8n webhooks                       |
| python-dotenv                | Environment variable management                            |
| Git & GitHub                 | Version control                                            |

## ✨ Features

### 1. Gemini-Powered HR Assistant

- Interacts with users through a natural language interface.
- Identifies relevant HR tools based on user requests.
- Uses Gemini to process requests and generate responses.

### 2. MCP Server

Exposes HR functionality through MCP.

**Available tools:**

- `get_employee_details` — Retrieves employee information.
- `calculate_leave_balance` — Retrieves the remaining leave balance.
- `create_leave_request` — Creates a leave request.

**Additional MCP capabilities:**

- HR leave policy resource.
- Leave eligibility explanation prompt.

### 3. Human-in-the-Loop Approval

- Requires explicit user confirmation before executing leave-request creation.
- Prevents the application from executing the protected action without approval.

### 4. Client-Side Validation

- Validates leave request arguments.
- Checks date formats.
- Ensures the end date is not earlier than the start date.
- Rejects empty or placeholder reasons.

### 5. n8n Workflow Automation

After successful leave-request creation, the Python client sends the MCP result to an n8n webhook.

The n8n workflow:

1. Receives the incoming HTTP POST request.
2. Extracts employee and leave-request information.
3. Validates required fields.
4. Checks whether the request status is `Pending`.
5. Routes valid requests to the email notification node.
6. Returns an HTTP 200 response for successful processing.
7. Returns an HTTP 400 response for invalid requests.

### 6. Independent Testing Scripts

Two additional scripts are included:

- `test_webhook.py` — Tests the HR leave-request webhook independently.
- `mcp_n8n_bridge_test.py` — Tests the Python-to-n8n bridge using an MCP-style result payload.

## 📁 Project Structure

```text
Company-HR-MCP-Server/
│
├── server.py
├── client.py
│
├── test_webhook.py
├── mcp_n8n_bridge_test.py
│
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
│
└── README.md
```

| File                     | Description                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| `server.py`              | Defines the MCP server, HR tools, resource, and prompt.                                          |
| `client.py`              | Connects Gemini with the MCP server and handles tool execution, approval, and n8n communication. |
| `test_webhook.py`        | Independently tests the HR leave-request webhook.                                                |
| `mcp_n8n_bridge_test.py` | Tests the Python-to-n8n integration.                                                             |
| `requirements.txt`       | Contains project dependencies.                                                                   |
| `.env`                   | Stores API keys and webhook configuration.                                                       |

## 📚 Learning Outcomes

This project applies the following MCP and n8n concepts through a working HR automation application.

MCP Implementation

- **MCP Server:** Built a Python-based MCP server exposing HR functionality.
- **Tools:** Implemented `get_employee_details`, `calculate_leave_balance`, and `create_leave_request`.
- **Resources:** Exposed HR leave policies through an MCP resource.
- **Prompts:** Implemented a reusable leave eligibility explanation prompt.
- **MCP Client:** Established communication between the Python client and MCP server using STDIO transport.
- **LLM Tool Calling:** Integrated Google Gemini to identify and execute relevant MCP tools.
- **Human-in-the-Loop:** Implemented explicit user confirmation before executing leave-request creation.
- **Input Validation:** Added client-side validation for tool arguments, dates, and leave reasons.
- **Tool Result Handling:** Extracted MCP tool responses and handled execution errors.
- **MCP-to-Workflow Integration:** Forwarded successful MCP tool results to n8n through HTTP requests.

n8n Implementation

- **Webhook Trigger:** Created HTTP webhook endpoints to receive data from Python applications.
- **HTTP Request Integration:** Sent JSON payloads from Python to n8n using POST requests.
- **Data Mapping:** Used the Edit Fields node to extract and map incoming employee and leave-request fields.
- **Conditional Logic:** Configured the IF node with multiple AND conditions to validate incoming requests.
- **Workflow Branching:** Routed valid and invalid requests through separate execution paths.
- **Email Automation:** Integrated the Send Email node into the successful execution branch.
- **Webhook Responses:** Used Respond to Webhook nodes to return HTTP 200 for successful processing and HTTP 400 for validation failures.
- **Workflow Testing:** Tested webhook execution using both test and production webhook configurations as applicable.

## 🔮 Future Improvements

- Implement persistent employee and leave-request storage.
- Add employee authentication and role-based authorization.
- Introduce remote MCP transport using Streamable HTTP.
- Add webhook authentication and secure communication.
- Implement retry mechanisms and structured error handling.
- Maintain an audit log of leave-request operations.
- Deploy the MCP server and integrate it with a remote MCP client.

## 👨‍💻 Author

**Inderjot Singh**

- GitHub: [InderjotSingh17](https://github.com/InderjotSingh17)
- LinkedIn: [Inderjot Singh](https://www.linkedin.com/in/inderjot-singh-0471a6237)

---

⭐ If you find this project interesting, feel free to explore the repository and share your feedback.

**Built with Python, Gemini, MCP, and n8n.**
