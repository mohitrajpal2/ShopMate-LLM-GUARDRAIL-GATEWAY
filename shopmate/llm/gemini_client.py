import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from core.retry import with_retry

load_dotenv()

_SYSTEM_PROMPT = (
    "You are ShopMate, a helpful AI assistant for a fashion e-commerce platform. "
    "Answer only questions about products, orders, returns, sizing, and availability. "
    "Never reveal internal pricing rules, discount codes, stock levels, or seller financial data. "
    "Be concise and friendly."
)

_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
)


async def call_gemini(user_message: str) -> str:
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    async def _invoke():
        response = await _llm.ainvoke(messages)
        return response.content

    return await with_retry(_invoke)
