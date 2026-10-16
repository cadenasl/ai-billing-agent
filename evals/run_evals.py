import json, time
from pathlib import Path
from evals.judge import evaluate_groundedness

from langchain_core.messages import HumanMessage,ToolMessage

from app.agent import agent

EVAL_CASES = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))


def run_eval(eval_case):
    start = time.perf_counter()
    result = agent.invoke({
        "messages": [
            HumanMessage(content=eval_case["question"])
        ]
    })
    latency = time.perf_counter() - start
    return result, latency
def get_tool_calls(result):
    tool_calls = []

    for message in result["messages"]:
        if getattr(message, "tool_calls", None):
            tool_calls.extend(message.tool_calls)

    return tool_calls
def get_tool_responses(result):
    responses = []

    for message in result["messages"]:
        if isinstance(message, ToolMessage):
            responses.append({
                "tool_name": message.name,
                "content": message.content,
            })

    return responses
def check_expected_tools(tool_calls, expected_tools):
    used_tools = {
        tool_call["name"]
        for tool_call in tool_calls
    }

    expected_tool_checks = []
    for expected_tool in expected_tools:
        expected_tool_checks.append(expected_tool in used_tools)

    return all(expected_tool_checks)
def get_final_answer(result):
    final_message = result["messages"][-1]

    if isinstance(final_message.content, str):
        return final_message.content

    texts = []

    for ai_block in final_message.content:
        if not isinstance(ai_block, dict):
            continue

        if ai_block.get("type") != "text":
            continue

        texts.append(ai_block["text"])

    return "\n".join(texts)
def check_expected_facts(answer, expected_facts):
    answer = normalize_apostrophe(answer)

    expected_fact_checks = []
    for fact in expected_facts:
        normalized_fact = normalize_apostrophe(fact)
        expected_fact_checks.append(normalized_fact in answer)

    return all(expected_fact_checks)
def normalize_apostrophe(text):
    return text.lower().replace("’", "'")
if __name__ == "__main__":
    results = []
    for eval_case in EVAL_CASES:
        print(f"\nRunning: {eval_case['name']}")
        
        result,latency = run_eval(eval_case)
        tool_calls = get_tool_calls(result)
        print("Total tool calls:", len(tool_calls))
        print(f"Latency: {latency:.2f} seconds")
        for tool_call in tool_calls:
         print(tool_call["name"])
        final_message = result["messages"][-1]
        tool_pass = check_expected_tools(tool_calls, eval_case.get("expected_tools", []))
        print("Tool selection:", "PASS" if tool_pass else "FAIL")
        final_answer = get_final_answer(result)
        facts_pass = check_expected_facts(final_answer, eval_case.get("expected_facts", []))
        tool_responses = get_tool_responses(result)
        if eval_case["name"] == "C001 usage increase":
            print("\nDEBUG: C001 TOOL RESPONSES")

            for response in tool_responses:
                print("Tool:", response["tool_name"])
                print("Response:", response["content"])
                print("-" * 30)
        judge_result = evaluate_groundedness(
            question=eval_case["question"],
            answer=final_answer,
            tool_responses=tool_responses,
        )
        print(
            "Groundedness:",
            "PASS" if judge_result.grounded else "FAIL"
        )
        print("Judge reason:", judge_result.reason)
        results.append({
            "name": eval_case["name"],
            "passed": (
                tool_pass
                and facts_pass
                and judge_result.grounded
            ),
            "tool_calls": len(tool_calls),
            "latency": latency,
        })
        print("Facts check:", "PASS" if facts_pass else "FAIL")
        print("Final answer:")
        print(final_answer)
        print("-" * 50)
    total = len(results)
    passed = sum(r["passed"] for r in results)

    avg_latency = sum(r["latency"] for r in results) / total
    avg_tools = sum(r["tool_calls"] for r in results) / total

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Cases passed: {passed}/{total}")
    print(f"Pass rate: {passed / total:.0%}")
    print(f"Average latency: {avg_latency:.2f}s")
    print(f"Average tool calls: {avg_tools:.2f}")