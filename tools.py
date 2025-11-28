from langchain.tools import Tool
from datetime import datetime
import os
import ast
import operator as op
import re


# Allowed operators mapping for safe evaluation
_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}


def _eval_ast(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        oper = _ALLOWED_OPERATORS.get(type(node.op))
        if oper is None:
            raise ValueError("Unsupported operator")
        return oper(left, right)
    if isinstance(node, ast.UnaryOp):
        operand = _eval_ast(node.operand)
        oper = _ALLOWED_OPERATORS.get(type(node.op))
        if oper is None:
            raise ValueError("Unsupported unary operator")
        return oper(operand)
    raise ValueError("Unsupported expression element")


def _normalize_expression(text: str) -> str:
    """Try to convert natural-language math into a python expression.

    Examples: '128 times 46' -> '128 * 46', '2 to the power of 8' -> '2 ** 8'
    """
    t = text.lower()
    # basic replacements
    replacements = {
        "times": "*",
        "x": "*",
        "multiplied by": "*",
        "divided by": "/",
        "over": "/",
        "plus": "+",
        "minus": "-",
        "to the power of": "**",
        "power of": "**",
        "^": "**",
        "%": "%",
    }
    for k, v in replacements.items():
        t = t.replace(k, v)

    # extract the longest contiguous sequence of digits/operators/parentheses
    matches = re.findall(r"[\d\.\s\+\-\*\/\%\(\)\^]+", t)
    if matches:
        # pick the longest match (heuristic)
        expr = max(matches, key=len).strip()
    else:
        expr = t

    # collapse multiple spaces
    expr = re.sub(r"\s+", " ", expr)
    return expr


def calculator(expression: str) -> str:
    """Safely evaluate a mathematical expression using AST parsing.

    This function first tries to normalize natural-language math into a
    Python expression, then parses and evaluates it with a whitelist of
    AST nodes/operators.
    """
    try:
        expr = _normalize_expression(expression)
        if not expr:
            return "Error: No mathematical expression found."

        # parse expression
        node = ast.parse(expr, mode="eval").body
        result = _eval_ast(node)
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed"
    except (SyntaxError, ValueError):
        return "Error: Invalid or unsupported mathematical expression"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


def currency_converter(entry: str) -> str:
    """Convert currency using fixed example rates.

    Args:
        entry: string in the format "100 USD to BRL"

    Returns:
        Converted amount or an error message.
    """
    try:
        rates = {
            "USD": {"BRL": 5.33, "EUR": 0.86},
            "BRL": {"USD": 1/5.33, "EUR": 1/6.19},
            "EUR": {"USD": 1/0.86, "BRL": 6.19}
        }

        parts = entry.split()
        if len(parts) != 4 or parts[2].lower() != "to":
            return "Error: invalid format. Use: '100 USD to BRL'."

        amount = float(parts[0])
        from_curr = parts[1].upper()
        to_curr = parts[3].upper()

        if from_curr not in rates:
            return f"Error: source currency '{from_curr}' not supported."
        if to_curr not in rates[from_curr]:
            return f"Error: target currency '{to_curr}' not supported."

        rate = rates[from_curr][to_curr]
        result = amount * rate
        return f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}"
    except ValueError:
        return "Error: invalid number."
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def date_time(query: str) -> str:
    """Return current date/time based on query.

    Args:
        query: 'date', 'time', or 'date and time'

    Returns:
        Formatted date/time string.
    """
    now = datetime.now()
    q = query.lower().strip()

    if "date" in q and "time" in q:
        return now.strftime("Date and Time: %d/%m/%Y %H:%M:%S")
    elif "date" in q:
        return now.strftime("Date: %d/%m/%Y")
    elif "time" in q:
        return now.strftime("Time: %H:%M:%S")
    else:
        return now.strftime("Now: %d/%m/%Y %H:%M:%S")


calculator_tool = Tool(
    name="Calculator",
    func=calculator,
    description="""
    Useful to answer math questions and perform calculations.
    Input must be a valid mathematical expression.
    Examples: '2 + 2', '128 * 46', '100 / 5', '2 ** 8', '(10 + 5) * 3'
    Supports: +, -, *, /, **, parentheses.
    """
)

currency_tool = Tool(
    name="CurrencyConverter",
    func=currency_converter,
    description="""
    Useful to convert amounts between currencies.
    Input format: 'AMOUNT FROM to TO'
    Examples: '100 USD to BRL', '50 EUR to USD'
    """
)

date_time_tool = Tool(
    name="DateTime",
    func=date_time,
    description="""
    Useful to get current date and/or time.
    Input examples: 'date', 'time', 'date and time'
    """
)

all_tools = [
    calculator_tool,
    currency_tool,
    date_time_tool,
]