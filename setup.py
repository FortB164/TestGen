from setuptools import setup, find_packages

setup(
    name="testgen",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ollama",
        "pytest",
        "pytest-json-report"
    ],
    entry_points={
        'console_scripts': [
            'testgen=main:main',
        ],
    },
) 