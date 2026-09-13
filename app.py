import streamlit as st
import requests
import pandas as pd

API_URL = "https://800rayj76a.execute-api.us-east-1.amazonaws.com/expenses"
# --------------------------------
# Page configuration
# --------------------------------

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)



# --------------------------------
# Functions
# --------------------------------

def add_expense(amount, category, description, date):

    expense = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": str(date)
    }

    response = requests.post(
        API_URL,
        json=expense
    )

    return response


def get_expenses():

    response = requests.get(API_URL)

    if response.status_code == 200:
        return response.json()

    return []

def delete_expense(expense_id):

    url = f"{API_URL}/{expense_id}"

    response = requests.delete(url)

    return response

# --------------------------------
# Title
# --------------------------------

st.title("💰 Expense Tracker")

st.write("Track and manage your daily expenses")


# --------------------------------
# Add Expense
# --------------------------------

st.header("Add Expense")

col1, col2 = st.columns(2)


with col1:

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=100.0
    )

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Shopping",
            "Entertainment",
            "Bills",
            "Other"
        ]
    )


with col2:

    description = st.text_input(
        "Description",
        placeholder="e.g. Lunch"
    )

    date = st.date_input("Date")


if st.button("➕ Add Expense"):

    if amount <= 0:

        st.error("Please enter an amount greater than ₹0.")

    elif description == "":

        st.error("Please enter a description.")

    else:

        response = add_expense(
        amount,
        category,
        description,
        date
)

        if response.status_code == 201:

            st.success("Expense added successfully!")
            st.rerun()

        else:

            st.error(
            f"Failed to add expense: {response.text}"
    )

# --------------------------------
# Get expenses from API
# --------------------------------

expenses = get_expenses()

# --------------------------------
# Dashboard
# --------------------------------

st.header("Dashboard")

total_expenses = sum(
    float(expense["amount"])
    for expense in expenses
)


transaction_count = len(expenses)


if transaction_count > 0:

    average_expense = (
        total_expenses / transaction_count
    )

else:

    average_expense = 0


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Expenses",
        f"₹{total_expenses:,.2f}"
    )


with col2:

    st.metric(
        "Transactions",
        transaction_count
    )


with col3:

    st.metric(
        "Average Expense",
        f"₹{average_expense:,.2f}"
    )


# --------------------------------
# Spending by Category
# --------------------------------

st.header("Spending by Category")


category_totals = {}


for expense in expenses:

    category = expense["category"]

    amount = float(expense["amount"])

    if category not in category_totals:

        category_totals[category] = 0

    category_totals[category] += amount


if category_totals:

    chart_data = pd.DataFrame(
        list(category_totals.items()),
        columns=["Category", "Amount"]
    )

    chart_data = chart_data.set_index("Category")

    st.bar_chart(chart_data)

else:

    st.info(
        "Add expenses to see your spending chart."
    )


# --------------------------------
# Recent Expenses
# --------------------------------

st.header("Recent Expenses")


if not expenses:

    st.info("No expenses added yet.")

else:

    for expense in expenses:

        col1, col2, col3, col4, col5 = st.columns(
            [1.5, 2, 3, 2, 1]
        )

        with col1:
            st.write(expense["date"])

        with col2:
            st.write(expense["category"])

        with col3:
            st.write(expense["description"])

        with col4:
            st.write(
                f"₹{float(expense['amount']):,.2f}"
            )

        with col5:

            if st.button(
        "🗑️",
        key=expense["expense_id"]
    ):

                response = delete_expense(
                expense["expense_id"]
        )

                if response.status_code == 200:
                    st.success("Expense deleted!")
                    st.rerun()

                else:
                    st.error(
                    f"Failed to delete expense: {response.text}"
            )