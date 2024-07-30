# Daily Expenses Sharing Application

## Description
This is a backend service for a daily expenses sharing application. Users can add expenses and split them among participants using exact amounts, percentages, or equal splits. The application also allows generating and downloading balance sheets.

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Shr1ramN/expense_calculator.git
2. Create a Virtual Environment
On Windows:

bash
Copy code
python -m venv venv
On macOS/Linux:

bash
Copy code
python3 -m venv venv
3. Activate the Virtual Environment
On Windows:

bash
Copy code
venv\Scripts\activate
On macOS/Linux:

bash
Copy code
source venv/bin/activate
4. Install the Dependencies
bash
Copy code
pip install -r requirements.txt
5. Set Up Environment Variables
Create a .env file in the project root directory.
Add the following line to the .env file (adjust as necessary):
dotenv
Copy code
MONGO_URI=mongodb://localhost:27017/yourdatabase
6. Run the Application
bash
Copy code
uvicorn app.main:app --reload
API Endpoints
User Endpoints
Create a New User
URL: /users/
Method: POST
Request Body:
json
Copy code
{
  "id": "user1",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "mobile": "123-456-7890"
}
Response:
json
Copy code
{
  "id": "user1",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "mobile": "123-456-7890"
}
Get a Single User
URL: /users/{user_id}
Method: GET
Response:
json
Copy code
{
  "id": "user1",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "mobile": "123-456-7890"
}
Expense Endpoints
Add a New Expense
URL: /expenses/
Method: POST
Request Body:
json
Copy code
{
  "id": "e1",
  "payer": "user1",
  "amount": 120.0,
  "participants": ["user1", "user2", "user3"],
  "split_method": "equal",
  "splits": {}
}
Response:
json
Copy code
{
  "id": "e1",
  "payer": "user1",
  "amount": 120.0,
  "participants": ["user1", "user2", "user3"],
  "split_method": "equal",
  "splits": {
    "user1": {"user2": 40.0, "user3": 40.0},
    "user2": {"user1": 40.0, "user3": 40.0},
    "user3": {"user1": 40.0, "user2": 40.0}
  }
}
Download Balance Sheet
URL: /expenses/download
Method: GET
Response: CSV file download
csv
Copy code
User ID,Balance
user1,0.0
user2,0.0
user3,0.0
Get Total Amount to be Paid by a User
URL: /expenses/{user_id}
Method: GET
Response:
json
Copy code
{
  "user_id": "user1",
  "balance": 0.0
}
Get All Expenses
URL: /expenses/
Method: GET
Response:
json
Copy code
[
  {
    "id": "e1",
    "payer": "user1",
    "amount": 120.0,
    "participants": ["user1", "user2", "user3"],
    "split_method": "equal",
    "splits": {
      "user1": {"user2": 40.0, "user3": 40.0},
      "user2": {"user1": 40.0, "user3": 40.0},
      "user3": {"user1": 40.0, "user2": 40.0}
    }
  }
]
