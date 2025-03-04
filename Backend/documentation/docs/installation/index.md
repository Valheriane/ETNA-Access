# **Installation Guide**

## **Prerequisites**
### **Technologies Used:**
- **Flask**: Lightweight web framework for Python.
- **Flask-SQLAlchemy**: ORM for database interaction.
- **Flask-JWT-Extended**: Manages JWT tokens for access security.
- **Flask-Migrate**: Handles database migrations.
- **Faker**: Generates fake data for database seeding.

## **Installation**

### **Clone the repository**
```bash
git clone https://github.com/Valheriane/ETNA-Access.git
cd <ETNA-Access/Backend>
```

### **Set up a virtual environment**
```bash
python -m venv env
```
Using a virtual environment ensures dependency isolation and project-specific configuration.

### **Install dependencies**
```bash
pip install -r requirements.txt
```

### **Configure the environment**
Copy the `.env.sample` file to `.env` and update the variables as needed.

### **Run the application**
```bash
flask run
```
or
```bash
python main.py runserver
```

## **Application Structure**
### **Main Files:**
- **app.py**: Main entry point, initializes configurations (database, JWT, etc.).
- **models.py**: Contains SQLAlchemy models for users, permissions, and other entities.
- **main.py**: Defines API routes and namespaces.

## **Command Line Interface (CLI) Commands**

Execute these commands using Flask's CLI:
```bash
flask command_name
```

- **populate-prod-data**: Populate the database with production data.
- **populate-all**: Populate the database with all necessary data.
- **reset-db**: Reset the database and insert test data.
- **reset-db-hash**: Reset the database and insert user data with hashed passwords.

## **API Routes**
### **Authentication**
#### **POST /login**
Authenticates a user and returns a JWT token.

#### **Request Example:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
#### **Success Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.ZRa2b97d2n4FJhqlWVtRnlq4iQyFrT46AaFZDr2q6uw"
}
```
#### **Error Response:**
```json
{
  "msg": "Bad email or password"
}
```

## **API Endpoints**
The API exposes multiple namespaces for managing different system aspects:

- **/users**: User management.
- **/companies**: Company information management.
- **/permissions**: User permissions management.
- **/payments**: Payment method management.

> All endpoints are secured via JWT authentication.

## **Permissions Management**
The `check_permissions` function verifies user access rights based on their permission level, company, and action target. This ensures controlled resource access.

### **Permission Levels:**
- **Permission 1-2**: Users can only access their own data.
- **Permission 3**: Users can access data of their company members.
- **Permission 4**: Users can access company-wide information.
- **Permission 5+**: Extended access based on predefined rules.

---

This structured guide ensures smooth installation and API usage while maintaining security and proper access control.

