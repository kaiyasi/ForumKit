from setuptools import setup, find_packages

setup(
    name="anon-campus-platform",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "pydantic>=2.4.2",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.23",
        "psycopg2-binary>=2.9.9",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "alembic>=1.12.1",
        "redis>=5.0.1",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=0.4.0",
        "python-dotenv>=1.0.0",
        "pydantic-settings>=2.0.3",
    ],
) 