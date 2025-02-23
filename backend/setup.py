from setuptools import setup, find_packages

setup(
    name="j-feature-store",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "motor",
        "redis",
        "kafka-python",
        "psycopg2-binary",
        "pydantic"
    ],
)
