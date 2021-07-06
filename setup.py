from setuptools import setup


REQUIREMENTS = [
    "pandas>=1.3.0",
    "fastparquet>=0.6.0",  # to load parquet files
    "typer>=0.3.2",  # CLI
    "fastapi>=0.63.0",  # HTTP API
    "psycopg2>=2.8.6",  # PostgreSQL
    "uvicorn>=0.13.3",  # HTTP
]

setup(
    name="voucher_selection",
    version="0.0.1",
    packages=["voucher_selection"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": ["voucher_selection=voucher_selection.cli:app"],
    },
)
