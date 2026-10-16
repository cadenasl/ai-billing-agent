from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()
class GroundednessResult(BaseModel):
    grounded: bool = Field(
        description=(
            "True if all factual claims in the answer "
            "are supported by the tool responses."
        )
    )

    reason: str = Field(
        description="Explain why the answer passed or failed."
    )


judge_model = ChatOpenAI(
    model="gpt-6-luna",
)

structured_judge = judge_model.with_structured_output(
    GroundednessResult,method="function_calling"
)


JUDGE_PROMPT = """
You are an independent evaluator for a billing investigation agent.

Your task is to determine whether the agent's final answer
is grounded in the provided tool responses.

Rules:
1. Treat the tool responses as the only source of factual evidence.
2. Every factual claim in the answer must be supported by that evidence
   or by straightforward arithmetic using the evidence.
3. Do not assume missing information.
4. Do not infer causes that the tool responses do not establish.
5. If the agent correctly states that information is unavailable,
   that is grounded.
6. If the answer contains any unsupported factual claim,
   return grounded=false.
7. Explain your decision briefly.

When evaluating numerical claims:
- Verify arithmetic carefully using the tool responses.
- For tiered electricity rates, apply each rate only to
  the usage within that tier.
- Do not apply the higher-tier rate to all usage.
- If the answer's calculations reconcile with the tool data,
  do not mark it ungrounded.
- Include base charges, previous balances, and fees
  when verifying total bill amounts.
- Use the rate-plan thresholds returned by the tools
  rather than assuming fixed thresholds.

Ignore writing style and formatting.
Do not judge whether the answer is helpful or complete.
Do not use outside knowledge.
"""


def evaluate_groundedness(question, answer, tool_responses)-> GroundednessResult:
    response = structured_judge.invoke([
        SystemMessage(content=JUDGE_PROMPT),
        HumanMessage(
            content=(
                f"Question:\n{question}\n\n"
                f"Tool responses:\n{tool_responses}\n\n"
                f"Agent answer:\n{answer}"
            )
        ),
    ])
    if isinstance(response, dict):
        response = GroundednessResult(**response)
    return response
  
  
if __name__ == "__main__":
    result = evaluate_groundedness(
        question="Why did C003's bill increase?",
        answer=(
            "C003's bill increased because of a $5 late-payment "
            "penalty caused by a missed payment."
        ),
        tool_responses=[
            {
                "tool_name": "get_billing_info",
                "content": (
                    '{"customer_id": "C003", '
                    '"billing_month": "2026-07", '
                    '"fees": 5.00}'
                ),
            }
        ],
    )

    print("Grounded:", result.grounded)
    print("Reason:", result.reason)