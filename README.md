# Expense Sharing Application
## Overview
This application allows users to add expenses and split them based on three
different methods: exact amounts, percentages, and equal splits. The
application manages user details, validates inputs, and generates downloadable balance sheets.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/kshitijv09/splitwise.git
   cd splitwise
2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
3. **Set up environment variables**

4. Running the application
   ```sh
   python manage.py runserver
## Endpoints

The following endpoints are available in this expense sharing application:

### BASEURL: http://localhost:8000

### User Service

#### `POST user/create`

Description: Create a new user

Example Request:
```json
{
    "name":"Yuji Nishida",
    "email":"yujinishida@gmail.com",
    "password":"yujinishida",
    "phone":"4567765423"
}
```
Example Response:
```json
{
    "message": "User created successfully",
    "user_id": 4
}
```
#### `GET user/get/:userId`

Description: Retrieve user details by id

Example Response:
```json
{
    "id": 2,
    "name": "Tom Cruise",
    "email": "tomcruise@gmail.com",
    "phone": "2334456778"
}
```
### Expense Service

#### `POST expense/add`

Description: Add an expense with its participants

Example Request:
```json
{
    "description": "Dinner at restaurant",
    "amount": 100.0,
    "currency": "USD",
    "date": "2024-07-28",
    "payer_id": "1",
    "payment_type": "percentage",
    "participants": [
        {"user_id": "2", "amount": 50},
        {"user_id": "3", "amount": 25},
        {"user_id": "4", "amount": 25}
    ]
}
```
Example Response:
```json
{
    "message": "Expense created successfully"
}
```
#### `GET expense/retrieve/:userId`

Description: Get individual user expenses which include entire expense payment and as a participant in an expense

Example Response:
```json
{
    "expenses": [
        {
            "expense_id": 3,
            "description": "Dinner at restaurant",
            "amount": 100.0,
            "currency": "USD",
            "date": "2024-07-28",
            "payer": "Tom Cruise",
            "payment_type": "equal",
            "amount_owed": 25.0
        },
        {
            "expense_id": 4,
            "description": "Dinner at restaurant",
            "amount": 100.0,
            "currency": "USD",
            "date": "2024-07-28",
            "payer": "Jhon Doe",
            "payment_type": "percentage",
            "amount_paid": 100.0
        }
    ],
    "total_owed": 25.0,
    "total_paid": 100.0,
    "net_owed": 75.0
}
```
#### `GET expense/retrieveAll/`

Description: Retrieves overall expenses for all users

Example Response:
```json
{
    "overall_expenses": [
        {
            "expense_id": 3,
            "description": "Dinner at restaurant",
            "amount": 100.0,
            "currency": "USD",
            "date": "2024-07-28",
            "payer": "Tom Cruise",
            "payment_type": "equal",
            "participants": [
                {
                    "user_id": 1,
                    "username": "Jhon Doe",
                    "amount": 25.0
                },
                {
                    "user_id": 2,
                    "username": "Tom Cruise",
                    "amount": 25.0
                },
                {
                    "user_id": 3,
                    "username": "John Wick",
                    "amount": 25.0
                },
                {
                    "user_id": 4,
                    "username": "Yuji Nishida",
                    "amount": 25.0
                }
            ]
        },
        {
            "expense_id": 4,
            "description": "Dinner at restaurant",
            "amount": 100.0,
            "currency": "USD",
            "date": "2024-07-28",
            "payer": "Jhon Doe",
            "payment_type": "percentage",
            "participants": [
                {
                    "user_id": 2,
                    "username": "Tom Cruise",
                    "amount": 50.0
                },
                {
                    "user_id": 3,
                    "username": "John Wick",
                    "amount": 25.0
                },
                {
                    "user_id": 4,
                    "username": "Yuji Nishida",
                    "amount": 25.0
                }
            ]
        }
    ]
}
```
#### `GET expense/getBalanceSheet/:userId`

Description: Downloads balance sheet for a user which contains individual expenses as well as overall expenses for all users

Example Response:

Type       Expense ID Description          Amount Currency Date       Payer Name Payment Type Amount Owed Amount Paid
Individual 3          Dinner at restaurant 100.0  USD      2024-07-28 Tom Cruise equal           25.0        0
Individual 4          Dinner at restaurant 100.0  USD      2024-07-28 Jhon Doe   percentage      0          100.0

Type       Expense ID Description          Amount Currency Date       Payer Name Payment Type ParticipantId  ParticipantName Amount
Overall    3          Dinner at restaurant 100.0  USD      2024-07-28 Tom Cruise equal           1           Jhon Doe        25.0
Overall    3          Dinner at restaurant 100.0  USD      2024-07-28 Tom Cruise equal          2           Harry Brook       50.0
Overall    3          Dinner at restaurant 100.0  USD      2024-07-28 Tom Cruise equal         3          Lamine Yamal        25.0



   
