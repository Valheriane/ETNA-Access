# Authentication Process

## API Routes

### Authentication

#### POST /login

This route allows user authentication and returns a JWT token to access the protected features of the application.

##### Example requests with test users:

**Test User 1 (Permission 1)**
```json
{
    "email": "emma.sano@example.com",
    "password": "DrakenILoveYou!"
}
```

**Test User 2 (Permission 2)**
```json
{
    "email": "licorne.unebelle@example.com",
    "password": "UneBelleLicorne!"
}
```

**Test User 3 (Permission 3)**
```json
{
    "email": "erwin.smith@example.com",
    "password": "ShinZuSasagewo!"
}
```

**Test User 4 (Permission 4)**
```json
{
    "email": "keisuke.baji@example.com",
    "password": "1erDivisionToman!"
}
```

##### Possible Responses:

**Success**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.ZRa2b97d2n4FJhqlWVtRnlq4iQyFrT46AaFZDr2q6uw"
}
```

**Error** (wrong credentials)
```json
{
  "msg": "Bad email or password"
}
```

### Authentication Process Flow

When a user attempts to log in, the following happens behind the scenes:

1. **The user sends a request**:
   - A `POST` HTTP request is made to `/login`, providing the email and password in the request body.

2. **Information verification**:
   - The server retrieves this information and looks up the email in the database.
   - If the user does not exist or the password is incorrect, an error response is returned (`401 Unauthorized`).

3. **Token generation**:
   - If the credentials are valid, the server generates a JWT (`access_token`) containing several pieces of user information, such as:
     - Their `id_user`
     - Their `first_name`
     - Their permission level
     - Their `id_company` (if they belong to a company)

4. **Response sent back**:
   - The server returns the token along with useful user details.
   - The client application can then use this token to access secured routes.

### Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant S as Flask Server
    participant DB as Database

    U->>S: Send POST /login request (email, password)
    S->>S: Extract request information
    S->>DB: Check if user exists
    DB-->>S: Database response
    alt Invalid user
        S->>U: Return {"message": "Invalid credentials"} (401)
    else Valid user
        S->>S: Verify password
        alt Incorrect password
            S->>U: Return {"message": "Invalid credentials"} (401)
        else Correct password
            S->>S: Create JWT token
            S->>U: Return {"access_token": ..., "user_id": ..., "first_name": ..., "permissions": ..., "company_id": ...} (200)
        end
    end
```

### Summary

Authentication follows a simple exchange: the user sends credentials, the server validates them, and if everything is correct, it provides a JWT token. This token is then used to access protected routes without needing to log in again for each request.

In case of failure (wrong credentials, user not found), the server returns an error to prevent unauthorized access.

This approach ensures secure and efficient authentication for the application.
