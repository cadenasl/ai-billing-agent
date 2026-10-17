import logging
import time

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

from app.agent import agent
from app.api.schemas import InvestigateRequest, InvestigateResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/investigate", response_model=InvestigateResponse)
def investigate(request: InvestigateRequest) -> InvestigateResponse:
    start = time.perf_counter()
    status = "failed"
    try:
        result = agent.invoke({
            "messages": [
                HumanMessage(
                    content=f"Customer ID: {request.customer_id}\n{request.query}"
                )
            ]
        })
        answer = result["messages"][-1].text()
        status = "completed"
    except Exception:
        logger.exception("Billing agent invocation failed")
        raise HTTPException(
            status_code=503,
            detail="Billing investigation service unavailable",
        )
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "event=billing_investigation_finished status=%s duration_ms=%.0f",
            status,
            duration_ms,
        )
    return InvestigateResponse(
        customer_id=request.customer_id,
        answer=answer,
    )
