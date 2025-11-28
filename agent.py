from config import llm
from langchain.agents import AgentExecutor, create_react_agent
from tools import all_tools
from prompt import prompt
import re

def create_agent():
    """Create and return a LangChain agent configured with available tools."""
    agent = create_react_agent(llm, all_tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )

    return agent_executor

def identify_tool(question: str):
    """Detect whether the question should be handled by a tool and return the tool name."""
    lower = question.lower()
    # Currency detection: expect a pattern like '100 USD to BRL'
    if re.search(r"\b\d+(?:\.\d+)?\s+[A-Za-z]{3}\s+to\s+[A-Za-z]{3}\b", question, re.IGNORECASE):
        return "CurrencyConverter"

    # Calculator detection: require digits and at least one operator or keywords like 'times', 'plus'
    if re.search(r"\d+\s*(?:\+|\-|\*|/|\^|\*\*|times|plus|minus|divided|over)\s*\d+", lower):
        return "Calculator"

    if any(keyword in lower for keyword in ["date", "time", "today", "now"]):
        return "DateTime"

    return None

def process_question(question: str, agent_executor: AgentExecutor) -> dict:
    """Process a question: either call a tool directly or invoke the agent."""
    try:
        tool_name = identify_tool(question)
        if tool_name:
            for tool in all_tools:
                if tool.name == tool_name:
                    result = tool.func(question)
                    return {"success": True, "response": result, "tool_used": tool_name}

        response = agent_executor.invoke({"input": question})
        return {"success": True, "response": response["output"], "input": response.get("input")}
    except Exception as e:
        err_str = str(e)
        if "403" in err_str or "Unauthorized" in err_str or "access_denied" in err_str:
            message = (
                "Authorization error when accessing the LLM provider (403 - Unauthorized).\n"
                "Check your API key and environment variables (API_KEY, API_BASE, AZURE_DEPLOYMENT).\n"
                "In PowerShell: $env:API_KEY = 'YOUR_KEY' or use setx to persist.\n"
                "Also confirm endpoint and model permissions."
            )
            return {"success": False, "response": message, "error": err_str}

        return {"success": False, "response": f"Sorry, an error occurred while processing your question: {err_str}", "error": err_str}

if __name__ == "__main__":
    print("🤖 Starting multi-tool assistant tests...")
    print("=" * 70)

    agent_executor = create_agent()

    test_questions = [
        "What is 128 times 46?",
        "Calculate 2 to the power of 10",
        "Who was Albert Einstein?",
        "What is artificial intelligence?",
        "100 USD to BRL",
        "What is the date today?",
        "What time is it now?",
    ]

    for i, q in enumerate(test_questions, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/{len(test_questions)}")
        print(f"{'='*70}")
        print(f"❓ Question: {q}")
        print(f"{'='*70}")

        result = process_question(q, agent_executor)

        if result.get("success"):
            print(f"\n✅ Answer: {result['response']}\n")
        else:
            print(f"\n❌ Error: {result['response']}\n")