# 💰 Serverless Expense Tracker

A full-stack expense management application built using Python and AWS
serverless technologies. Users can add, view, and delete expenses,
configure a monthly budget, and receive email alerts when spending
exceeds their budget.

## Architecture

Streamlit → API Gateway → AWS Lambda → DynamoDB

                                ↓
                               SNS
                                ↓
                           Email Alert

GitHub → GitHub Actions → AWS OIDC → Lambda

## Features

- Add and manage expenses
- Categorize expenses
- View total and average spending
- Spending by category visualization
- User-configurable monthly budget
- Monthly budget usage tracking
- Email alerts when the budget is exceeded
- RESTful API
- Serverless AWS backend
- Automated Lambda deployment using GitHub Actions
- Secure AWS authentication using GitHub OIDC

## Technologies

### Frontend
- Python
- Streamlit

### Backend
- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB

### Notifications
- Amazon SNS

### CI/CD
- GitHub Actions
- AWS IAM
- GitHub OIDC

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/expenses` | Retrieve expenses |
| POST | `/expenses` | Add an expense |
| DELETE | `/expenses/{id}` | Delete an expense |
| GET | `/budget` | Retrieve monthly budget |
| PUT | `/budget` | Update monthly budget |

## CI/CD

The project uses GitHub Actions to automatically deploy the
Lambda function whenever changes are pushed to the `main` branch.

GitHub Actions authenticates with AWS using OpenID Connect (OIDC),
eliminating the need to store long-lived AWS access keys in GitHub.

## Running Locally

Clone the repository:

```bash
git clone <repository-url>
cd serverless-expense-tracker