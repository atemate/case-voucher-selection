from setuptools import setup


REQUIREMENTS = [
    "pandas>=1.3.0",
    "fastparquet>=0.6.0",
    "typer>=0.3.2",
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
