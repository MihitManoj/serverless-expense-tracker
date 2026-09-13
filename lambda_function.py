import json
import boto3
import uuid
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Expenses")


def lambda_handler(event, context):

    method = event.get("requestContext", {}).get(
        "http", {}
    ).get("method")

    # GET - Fetch all expenses
    if method == "GET":

        response = table.scan()
        expenses = response.get("Items", [])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(expenses, default=str)
        }

    # POST - Add expense
    elif method == "POST":

        body = json.loads(event.get("body", "{}"))

        expense = {
            "expense_id": str(uuid.uuid4()),
            "amount": Decimal(str(body["amount"])),
            "category": body["category"],
            "description": body["description"],
            "date": body["date"]
        }

        table.put_item(Item=expense)

        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Expense added successfully",
                "expense": expense
            }, default=str)
        }

    # DELETE - Delete expense
    elif method == "DELETE":

        expense_id = event.get(
            "pathParameters", {}
        ).get("id")

        if not expense_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Expense ID is required"
                })
            }

        table.delete_item(
            Key={"expense_id": expense_id}
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Expense deleted successfully"
            })
        }

    else:

        return {
            "statusCode": 405,
            "body": json.dumps({
                "message": "Method not allowed"
            })
        }