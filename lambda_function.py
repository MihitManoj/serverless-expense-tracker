import boto3
import json
import uuid
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Expenses")

sns = boto3.client("sns")

MONTHLY_BUDGET = Decimal("10000")

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:803179100419:expense-budget-alerts"

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

                # Check monthly spending
        response = table.scan()
        items = response.get("Items", [])

        current_month = datetime.now().strftime("%Y-%m")

        monthly_total = sum(
            (
                item["amount"]
                for item in items
                if str(item.get("date", "")).startswith(current_month)
            ),
            Decimal("0")
        )

        # Send budget alert
        if monthly_total >= MONTHLY_BUDGET:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="Expense Budget Alert",
                Message=(
                    f"Monthly budget exceeded!\n\n"
                    f"Budget: ₹{MONTHLY_BUDGET}\n"
                    f"Current spending: ₹{monthly_total}"
                )
            )
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