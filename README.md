# ShopBot

Rule-based e-commerce chatbot built with Python and FastAPI.

## What it does
- Product search and price filters ("shoes under 3000")
- Order status lookup
- Answers for shipping, returns, payments, offers and sizes

## API
`POST /chat` with `{"message": "hello"}` returns `{"reply": "..."}`

## Run locally
    pip install -r requirements.txt
    uvicorn main:app --reload

Then open http://localhost:8000
