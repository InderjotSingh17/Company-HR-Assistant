import asyncio
import sys
from pathlib import Path
from datetime import date
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
import os 
from dotenv import load_dotenv
load_dotenv()


N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

def notify_n8n(mcp_result):

    response = requests.post(
        N8N_WEBHOOK_URL,
        json=mcp_result,
        timeout=20
    )

    response.raise_for_status()

    return response.json()



MODEL = "gemini-3.5-flash-lite"
MAX_ROUNDS = 5

server_path = Path(__file__).with_name("server.py")

server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(server_path)]
)

ALLOWED_TOOLS = {
    "get_employee_details",
    "calculate_leave_balance",
    "create_leave_request"
}

CONFIRMATION_REQUIRED = {
    "create_leave_request"
}



def validate_leave_arguments(arguments):
    """Validate leave arguments before asking for approval."""

    start_date = arguments.get("start_date")
    end_date = arguments.get("end_date")
    reason = arguments.get("reason")

    if not isinstance(start_date, str):
        return False, "A valid start date is required."

    if not isinstance(end_date, str):
        return False, "A valid end date is required."

    if not isinstance(reason, str):
        return False, "A valid leave reason is required."

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

    except ValueError:
        return False, "Dates must be valid YYYY-MM-DD dates."

    if end < start:
        return False, "End date cannot be before start date."

    invalid_reasons = {
        "",
        "not specified",
        "none",
        "n/a",
        "no reason",
        "unknown",
        "not provided"
    }

    if reason.strip().lower() in invalid_reasons:
        return False, (
            "A valid leave reason is required. "
            "Please provide your actual reason."
        )

    return True, None



def confirm_action(tool_name, arguments):
    """Ask the user to approve the exact tool arguments."""

    print("\n========== ACTION CONFIRMATION ==========")
    print(f"Action: {tool_name}")

    for key, value in arguments.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    print("\nOnly approve if these details are correct.")

    approval = input(
        "\nDo you approve this exact action? (yes/no): "
    ).strip().lower()

    return approval in {"yes", "y"}



def extract_tool_result(result):
    """Extract text from MCP tool results."""

    text_parts = [
        item.text
        for item in result.content
        if hasattr(item, "text") and item.text
    ]

    return "\n".join(text_parts) or "Tool returned no text."



async def generate_gemini_response(
    gemini,
    conversation,
    gemini_tool
):
    """Generate a response using Gemini."""

    return await gemini.models.generate_content(
        model=MODEL,
        contents=conversation,
        config=types.GenerateContentConfig(
            tools=[gemini_tool],
            temperature=0
        )
    )




async def main():

    async with genai.Client().aio as gemini:

        async with Client(stdio_client(server_params)) as mcp_client:

            print("\nConnected to HR MCP Server!")


            mcp_tools = await mcp_client.list_tools()

            available_tools = [
                tool
                for tool in mcp_tools.tools
                if tool.name in ALLOWED_TOOLS
            ]

            print("\nTools available to Gemini:")

            for tool in available_tools:
                print("-", tool.name)

            function_declarations = []

            for tool in available_tools:

                declaration = types.FunctionDeclaration(
                    name=tool.name,
                    description=tool.description,
                    parameters_json_schema=tool.input_schema
                )

                function_declarations.append(declaration)

            gemini_tool = types.Tool(
                function_declarations=function_declarations
            )


            conversation = []

            print("\n================================")
            print("       HR ASSISTANT READY")
            print("================================")
            print("Type 'exit' to quit.\n")


            while True:

                user_message = input("You: ").strip()

                if user_message.lower() in {"exit", "quit"}:
                    print("\nHR Assistant: Goodbye!")
                    break

                if not user_message:
                    continue

                history_checkpoint = len(conversation)

                action_executed = False

                conversation.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(
                                text=user_message
                            )
                        ]
                    )
                )

                try:

                    response = await generate_gemini_response(
                        gemini,
                        conversation,
                        gemini_tool
                    )

                    round_count = 0
                    abort_turn = False


                    while (
                        response.function_calls
                        and round_count < MAX_ROUNDS
                    ):

                        conversation.append(
                            response.candidates[0].content
                        )

                        function_response_parts = []

                        for function_call in response.function_calls:

                            tool_name = function_call.name

                            tool_arguments = dict(
                                function_call.args or {}
                            )

                            print(
                                f"\nGemini selected tool: {tool_name}"
                            )

                            print(
                                f"Arguments: {tool_arguments}"
                            )


                            if tool_name not in ALLOWED_TOOLS:

                                print(
                                    "\nAction rejected: "
                                    "Tool is not allowed."
                                )

                                abort_turn = True
                                break

                            if tool_name == "create_leave_request":

                                valid, validation_error = (
                                    validate_leave_arguments(
                                        tool_arguments
                                    )
                                )

                                if not valid:

                                    print(
                                        "\n========== "
                                        "VALIDATION ERROR "
                                        "=========="
                                    )

                                    print(validation_error)

                                    print(
                                        "\nPlease provide a valid "
                                        "leave reason or correct "
                                        "the request."
                                    )


                                    abort_turn = True
                                    break


                            if tool_name in CONFIRMATION_REQUIRED:

                                approved = confirm_action(
                                    tool_name,
                                    tool_arguments
                                )

                                if not approved:

                                    print(
                                        "\nAction cancelled. "
                                        "No request was submitted."
                                    )

                                    abort_turn = True
                                    break

                            try:

                                result = await mcp_client.call_tool(
                                    tool_name,
                                    tool_arguments
                                )

                                tool_result_text = extract_tool_result(
                                    result
                                )

                                if result.is_error:

                                    print(
                                        "\n========== TOOL ERROR "
                                        "=========="
                                    )

                                    print(tool_result_text)

                                    print(
                                        "\nThe operation was not "
                                        "confirmed as successful. "
                                        "It will not be retried "
                                        "automatically."
                                    )

                                    abort_turn = True
                                    break

                                print("\nMCP Server returned:")
                                print(tool_result_text)

                                if (
                                    tool_name
                                    in CONFIRMATION_REQUIRED
                                ):
                                    action_executed = True

                                    print(
                                        "\nAction executed successfully."
                                    )
                                    try:
                                        mcp_payload = json.loads(tool_result_text)
                                        print("\nSending MCP result to n8n...")
                                        n8n_response = notify_n8n(mcp_payload)
                                        print("\nn8n notification successful!")
                                        print(n8n_response)
                                    except json.JSONDecodeError as error:
                                        print("\nCould not parse MCP result as JSON:")
                                        print(error)
                                        print("Actual MCP result:")
                                        print(tool_result_text)
                                    except requests.exceptions.RequestException as error:
                                        print("\nn8n integration failed:")
                                        print(error)
                            except Exception as tool_error:

                                print("\n========== TOOL ERROR ==========")
                                print(tool_error)

                                print(
                                    "\nThe tool execution failed. "
                                    "No automatic retry will occur."
                                )

                                abort_turn = True
                                break


                            function_response_parts.append(
                                types.Part.from_function_response(
                                    name=tool_name,
                                    response={
                                        "result": tool_result_text
                                    }
                                )
                            )


                        if abort_turn:
                            break

                     

                        conversation.append(
                            types.Content(
                                role="user",
                                parts=function_response_parts
                            )
                        )

                        response = await generate_gemini_response(
                            gemini,
                            conversation,
                            gemini_tool
                        )

                        round_count += 1


                    if abort_turn:

                        del conversation[history_checkpoint:]

                        continue

                   

                    if response.function_calls:

                        print(
                            "\nHR Assistant: Maximum tool "
                            "execution rounds reached."
                        )

                        del conversation[history_checkpoint:]

                        continue

            

                    final_answer = (
                        response.text
                        or "I couldn't generate a response."
                    )

                    print("\n========== HR ASSISTANT ==========")
                    print(final_answer)

                    
                    conversation.append(
                        response.candidates[0].content
                    )

                    print()

                except Exception as error:

                    print(
                        "\n========== APPLICATION ERROR "
                        "=========="
                    )

                    print(error)

                    if action_executed:

                        print(
                            "\nIMPORTANT: A state-changing action "
                            "was already executed successfully. "
                            "The final AI response failed. "
                            "Do not submit the same request again "
                            "without checking its status."
                        )

                    del conversation[history_checkpoint:]




if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nHR Assistant stopped by user.")

    except Exception as error:
        print("\nApplication failed:", error)
