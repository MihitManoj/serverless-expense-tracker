import requests

url = "https://800rayj76a.execute-api.us-east-1.amazonaws.com/expenses"

expense = {
    "amount": 750,
    "category": "Food",
    "description": "Dinners",
    "date": "2026-09-13"
}

response = requests.post(url, json=expense)

print("Status code:", response.status_code)
print("Response:", response.text)