

# Permission Management in the SSO  

The SSO uses a permission system to manage user data access based on their permission level and the company they belong to. Permissions are assigned to different users according to their role and their relationship with other users within the application.  

## Permission Levels  

### Permission 1 and 2: Limited access to personal information  
Users with a permission level of 1 or 2 can only access their own information. This means the user cannot view other users' information, only their own.  
- **Permission 1 users**: Independent or individual users.  
- **Permission 2 users**: Basic users who belong to a company.  

- **Condition**: The user can access their information if the target user ID (target_user_id) matches their own user ID (user_id_from_token).  

### Permission 3: Access to users within the same company  
Users with a permission level of 3 can access information of users within the same company, provided that the target user's permission level is below 7.  

- **Conditions**:  
  - The user can always access their own information.  
  - The user can view the information of other members of their company if the target company ID (target_company_id) matches their own (company_id_from_token).  
  - Access is restricted to users with a permission level lower than 7.  

### Permission 4: Extended access to users within the same company  
Users with a permission level of 4 have broader access to members of the same company.  

- **Condition**: The user can access information of other members of their company if the target company ID matches their own.  

### Permission 5: Limited access based on specific rules  
Users with a permission level of 5 have specific and restricted access and belong to **ETNA-Sea-Robots**.  

- **Conditions**:  
  - The user can view their own information.  
  - The user **cannot** access members of their own company.  
  - The user **can** access information of members from other companies but not from their own.  

### Permission 6: Specific access for managers  
Users with a permission level of 6 have specific access to members of their company but cannot view users with higher permissions. They belong to **ETNA-Sea-Robots** and are **managers**.  

- **Conditions**:  
  - The user can always access their own information.  
  - The user can view members of their company with a permission level lower than 7.  
  - The user **cannot** view members with a permission level equal to or higher than 7.  

### Permission 7 or higher: Full access to all data  
Users with a permission level of 7 or higher have full access to all data in the application. They belong to **ETNA-Sea-Robots** and are **directors**.  

- **Condition**: The user can access all information without restriction.  

## Access Rules Summary  

| Permission Level | Description                                  | Authorized Access                             |  
|-----------------|---------------------------------------------|---------------------------------------------|  
| 1, 2           | Access only to personal information        | Only personal information                   |  
| 3             | Access to users within the same company     | Company members with permission < 7        |  
| 4             | Extended access to users within the company | All company members                        |  
| 5             | Limited access based on specific rules     | Other companies, but not their own         |  
| 6             | Specific access for managers              | Company members with permission < 7        |  
| 7 or higher   | Full access to all data                   | All information                            |  

## Conclusion  
The SSO permission management system precisely defines which users can access what information based on their permission level and the company they belong to. These rules ensure a fine-grained access control while allowing flexibility for specific roles such as managers.  

