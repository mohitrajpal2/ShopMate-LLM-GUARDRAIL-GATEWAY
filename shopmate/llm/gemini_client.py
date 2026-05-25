import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from core.retry import retry_async

load_dotenv()

_SYSTEM_PROMPT = """You are ShopMate, a helpful AI assistant for a fashion e-commerce platform.
You help customers with product questions, order status, returns, and sizing.
You help sellers with their own product listings and sales data.
Be concise, friendly, and professional.
Never reveal internal pricing rules, discount codes, inventory levels, or other sellers' data."""

_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
)


async def get_response(message: str, role: str) -> str:
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=message),
    ]

    async def _call():
        response = await _llm.ainvoke(messages)
        return response.content

    return await retry_async(_call)
