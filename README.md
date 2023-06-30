# EZTask 

# BUILT-IN
- Python 3.11;
- FastAPI + SQLAlchemy + Pydantic + Alembic;
- PostgreSQL (psycopg2 + asyncpg);
- Pytest;
- Redis;
- FastAPI-cache (based on Redis).
- 
# NOTICE
- Authorization process doesn't work correctly on standard Swagger-docs app page, because by default Swagger authorization form includes _'**username**'_ and _'**password**'_ fields, but currently app use **email** instead of username. So, if you'll try to authorize by email using username field, you'll get an error, because authorization functions (checking form data, creating JWT Bearer Token, etc.) are expecting for _'**email**'_ form field.
- By this reason, you can test Auth-funcs just using Postman, etc.