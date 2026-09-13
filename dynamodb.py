import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Expenses")

expense = {
    "expense_id": str(uuid.uuid4()),
    "amount": 500,
    "category": "Food",
    "description": "Lunch",
    "date": datetime.now().strftime("%Y-%m-%d")
}

table.put_item(Item=expense)

print("Expense added successfully!")
print(expense)