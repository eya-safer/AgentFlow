from google.genai import types
from backend.app.tools.notification_tools import prepare_notification
from backend.app.core.config import settings
from backend.app.agents.prompts import SYSTEM_INSTRUCTION
from backend.app.services.llm_service import get_gemini_client

from backend.app.tools.order_tools import get_order_status
from backend.app.tools.customer_tools import (
    get_customer_info,
    get_customer_orders
)

# 1. Describe the tool that Gemini can use
ORDER_STATUS_FUNCTION = types.FunctionDeclaration(
    name="get_order_status",
    description="Retrieve the status and details of a customer's order using its ID.",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "order_id": {
                "type": "integer",
                "description": "The unique ID of the order."
            }
        },
        "required": ["order_id"]
    }
)

CUSTOMER_INFO_FUNCTION = types.FunctionDeclaration(
    name="get_customer_info",
    description="Retrieve the personal information of a customer using their customer ID.",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "integer",
                "description": "The unique ID of the customer."
            }
        },
        "required": ["customer_id"]
    }
)


CUSTOMER_ORDERS_FUNCTION = types.FunctionDeclaration(
    name="get_customer_orders",
    description="Retrieve all orders belonging to a specific customer using their customer ID.",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "integer",
                "description": "The unique ID of the customer."
            }
        },
        "required": ["customer_id"]
    }
)

NOTIFICATION_FUNCTION = types.FunctionDeclaration(
    name="prepare_notification",
    description=(
        "Prepare an email notification for a customer. "
        "This tool only creates a draft requiring human approval. "
        "It never sends the notification."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "integer",
                "description": "The ID of the customer."
            },
            "message": {
                "type": "string",
                "description": "The notification message to prepare."
            }
        },
        "required": ["customer_id", "message"]
    }
)

# 2. Group the available function declarations
AGENT_TOOLS = [
    types.Tool(
        function_declarations=[
            ORDER_STATUS_FUNCTION,
            CUSTOMER_INFO_FUNCTION,
            CUSTOMER_ORDERS_FUNCTION,
            NOTIFICATION_FUNCTION]
    )
]


TOOL_REGISTRY = {
    "get_order_status": {
        "function": get_order_status,
        "arguments": {
            "order_id": int
        }
    },
    "get_customer_info": {
        "function": get_customer_info,
        "arguments": {
            "customer_id": int
        }
    },
    "get_customer_orders": {
        "function": get_customer_orders,
        "arguments": {
            "customer_id": int
        }
    },
    "prepare_notification": {
        "function": prepare_notification,
        "arguments": {
            "customer_id": int,
            "message": str
        }
    }
}



MAX_TOOL_CALLS = 5


def run_business_agent(user_message: str, db,history: list[dict] | None = None):

    client = get_gemini_client()

    # 1. Prepare the conversation
    conversation = []

# Ajouter l'historique précédent.
    for message in history or []:
        role = message.get("role")
        content = message.get("content")

        if role not in ["user", "assistant"]:
            continue

        if not isinstance(content, str) or not content.strip():
            continue

        gemini_role = "model" if role == "assistant" else "user"

        conversation.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=content)]
            )
        )

    # Ajouter le nouveau message de l'utilisateur.
    conversation.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        )
    )

    tool_names = []
    tool_results = []
    total_tool_calls = 0

    # 2. Allow Gemini to call tools multiple times
    for iteration in range(MAX_TOOL_CALLS):

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=conversation,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=AGENT_TOOLS,
                temperature=0.2
            )
        )

        # 3. If Gemini has no more tools to call,
        # return its final answer
        if not response.function_calls:

            if len(tool_results) == 1:
                tool_used = tool_names[0]
                tool_result = tool_results[0]
            else:
                tool_used = tool_names
                tool_result = tool_results

            return {
                "success": True,
                "tool_used": tool_used if tool_names else None,
                "tools_used": tool_names,
                "tool_result": tool_result if tool_results else None,
                "tool_results": tool_results,
                "response": response.text
            }

        # 4. Keep Gemini's response in the conversation
        model_content = response.candidates[0].content
        conversation.append(model_content)

        function_response_parts = []

        # 5. Execute every requested tool
        for function_call in response.function_calls:

            total_tool_calls += 1

            if total_tool_calls > MAX_TOOL_CALLS:
                return {
                    "success": False,
                    "message": "Maximum number of tool calls reached.",
                    "tools_used": tool_names,
                    "tool_results": tool_results
                }

            tool_name = function_call.name

            # Check whether the tool exists
            if tool_name not in TOOL_REGISTRY:
                return {
                    "success": False,
                    "message": f"Unknown tool requested: {tool_name}"
                }

            tool_config = TOOL_REGISTRY[tool_name]
            tool_function = tool_config["function"]
            expected_arguments = tool_config["arguments"]

            # Retrieve arguments from Gemini
            arguments = dict(function_call.args or {})

            # Check for unexpected arguments
            unexpected_arguments = (
                set(arguments) - set(expected_arguments)
            )

            if unexpected_arguments:
                return {
                    "success": False,
                    "message": "Unexpected tool arguments.",
                    "arguments": list(unexpected_arguments)
                }

            # Validate required arguments
            for argument_name, expected_type in expected_arguments.items():

                value = arguments.get(argument_name)

                if expected_type is int:
                    valid = (
                        isinstance(value, int)
                        and not isinstance(value, bool)
                    )

                elif expected_type is str:
                    valid = (
                        isinstance(value, str)
                        and bool(value.strip())
                    )

                else:
                    valid = isinstance(value, expected_type)

                if not valid:
                    return {
                        "success": False,
                        "message": f"Invalid argument: {argument_name}"
                    }

            # Execute the Python tool
            tool_result = tool_function(
                **arguments,
                db=db
            )

            tool_names.append(tool_name)
            tool_results.append({
                "tool": tool_name,
                "result": tool_result
            })

            # Prepare the result for Gemini
            function_response_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_result}
                )
            )

        # 6. Send all tool results back to Gemini
        tool_content = types.Content(
            role="user",
            parts=function_response_parts
        )

        conversation.append(tool_content)

    # 7. Stop if the maximum number of iterations is reached
    return {
        "success": False,
        "message": "Agent reached the maximum number of tool iterations.",
        "tools_used": tool_names,
        "tool_results": tool_results
    }
