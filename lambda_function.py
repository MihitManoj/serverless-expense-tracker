import json
import boto3
import uuid
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("Expenses")
budget_table = dynamodb.Table("BudgetSettings")

sns = boto3.client("sns")

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:803179100419:expense-budget-alerts"


def lambda_handler(event, context):

    method = event.get("requestContext", {}).get(
        "http", {}
    ).get("method")

    path = event.get("rawPath", "")

    # =========================
    # GET BUDGET
    # =========================
    if method == "GET" and path == "/budget":

        response = budget_table.get_item(
            Key={"setting_id": "default"}
        )

        budget = response.get("Item")

        if not budget:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "monthly_budget": 0
                })
            }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(budget, default=str)
        }

    # =========================
    # PUT BUDGET
    # =========================
    elif method == "PUT" and path == "/budget":

        body = json.loads(event.get("body", "{}"))

        budget = Decimal(str(body["monthly_budget"]))

        budget_table.put_item(
            Item={
                "setting_id": "default",
                "monthly_budget": budget
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Budget updated successfully",
                "monthly_budget": budget
            }, default=str)
        }

    # =========================
    # GET EXPENSES
    # =========================
    elif method == "GET" and path == "/expenses":

        response = table.scan()

        expenses = response.get("Items", [])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(expenses, default=str)
        }

    # =========================
    # POST EXPENSE
    # =========================
    elif method == "POST" and path == "/expenses":

        body = json.loads(event.get("body", "{}"))

        expense = {
            "expense_id": str(uuid.uuid4()),
            "amount": Decimal(str(body["amount"])),
            "category": body["category"],
            "description": body["description"],
            "date": body["date"]
        }

        table.put_item(Item=expense)

        # -------------------------
        # Check user's budget
        # -------------------------

        budget_response = budget_table.get_item(
            Key={"setting_id": "default"}
        )

        budget_item = budget_response.get("Item")

        if budget_item:

            monthly_budget = Decimal(
                str(budget_item["monthly_budget"])
            )

            response = table.scan()

            items = response.get("Items", [])

            current_month = datetime.now().strftime("%Y-%m")

            monthly_total = sum(
                (
                    Decimal(str(item["amount"]))
                    for item in items
                    if str(item.get("date", "")).startswith(
                        current_month
                    )
                ),
                Decimal("0")
            )

            # -------------------------
            # Send SNS alert
            # -------------------------

            if monthly_total >= monthly_budget:

                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject="Expense Budget Alert",
                    Message=(
                        f"Monthly budget exceeded!\n\n"
                        f"Budget: ₹{monthly_budget}\n"
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

    # =========================
    # DELETE EXPENSE
    # =========================
    elif method == "DELETE" and path.startswith("/expenses/"):

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

    # =========================
    # INVALID ROUTE
    # =========================
    else:

        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Route not found",
                "method": method,
                "path": path
            })
        }