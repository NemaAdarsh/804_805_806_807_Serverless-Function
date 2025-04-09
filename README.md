uvicorn app.main:app --reload

curl -X POST "http://127.0.0.1:8000/invoke/2c9534e4-3a6c-4833-91cd-b8829b600874" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"number\": 6}"

