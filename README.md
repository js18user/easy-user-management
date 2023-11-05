# easy-user-management
Easy user management

The software stack for implementing the task is as follows:
- Python 3.10.9 
- Fastapi
- Asyncio
- Async/await
- Pydantic
- Asyncpg
- SQL
- Postgresql 14.5  DBaaS  or Localhost
- Logging

Statement of the problem (Technical specifications for programming)

This program implements the maintenance of a database of simple users:
- ID
- name

Main functions:
-creating a user
-deleting a user
-user search, including search by context
- update user
 
User service is possible using:
- GET
- PUT
- DELETE
- POST

This program is self-documented via Swagger
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

Return codes:
- 200 - successful completion of the request
- 400 - there are errors in the request
- 422 - Pydantic validate response (very rare)

List and functions of the presented scripts:

- main.py       the main program
- requirements.txt no comments

