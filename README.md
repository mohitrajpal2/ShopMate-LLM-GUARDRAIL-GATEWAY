# ShopMate-LLM-GUARDRAIL-GATEWAY

Fill in .env — JWT_SECRET and GEMINI_API_KEY are required

pip install -r requirements.txt + python -m spacy download en_core_web_lg

pytest tests/ -v — all guardrail tests run without Gemini (mocked at input layer)

uvicorn main:app --reload to start the server


