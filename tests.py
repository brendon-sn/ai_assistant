"""
Simple test script that exercises the project's tools and agent.

This script is intentionally defensive: the agent test may fail if
LLM credentials are not configured. Tool tests are local and should
work without network access (except currency rates if you switch to
an external API).
"""
from tools import calculator, currency_converter, date_time
from agent import create_agent, process_question

def test_calculator():
    print("🧮 Testando Calculator...")
    casos = [
        ("2 + 2", "4"),
        ("128 * 46", "5888"),
        ("100 / 5", "20"),
        ("2 ** 10", "1024"),
        ("(10 + 5) * 3", "45"),
        ("sqrt of 144", "12"),
    ]

    for expr, esperado in casos:
        out = calculator(expr)
        ok = esperado in out
        print(f"  {'✅' if ok else '❌'} {expr} -> {out}")

    # edge cases
    print(f"  ⚠️ Divisão por zero: {calculator('10 / 0')}")
    print(f"  ⚠️ Entrada inválida: {calculator('10 + abc')}")
    print()


def test_currency():
    print("� Testando CurrencyConverter...")
    casos = [
        "100 USD to BRL",
        "50 EUR to USD",
    ]
    for c in casos:
        out = currency_converter(c)
        print(f"  {c} -> {out}")
    print()


def test_date_time():
    print("📅 Testando DateTime...")
    print(f"  date -> {date_time('date')}")
    print(f"  time -> {date_time('time')}")
    print()


def test_agent():
    print("🤖 Testando Agent (pode falhar se as credenciais não estiverem configuradas)...")
    try:
        agent_executor = create_agent()
        # calculator routed via identify_tool
        r1 = process_question("What is 128 times 46?", agent_executor)
        print(f"  Q: What is 128 times 46? -> success={r1.get('success')} response={r1.get('response')}")

        # general question (LLM)
        r2 = process_question("Who was Albert Einstein?", agent_executor)
        print(f"  Q: Who was Albert Einstein? -> success={r2.get('success')} response snippet={str(r2.get('response'))[:120]}")
    except Exception as e:
        print(f"  ❌ Agent test failed: {e}")
    print()


if __name__ == '__main__':
    print("=" * 70)
    print("🧪 EXECUTANDO TESTS")
    print("=" * 70)
    print()

    test_calculator()
    test_currency()
    test_date_time()
    test_agent()

    print("=" * 70)
    print("✅ TESTS FINISHED")
    print("=" * 70)