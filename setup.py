from setuptools import setup, find_packages

setup(
    name="git-commit-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
    ],
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'git-commit-bot=main:main',  # Points to root main.py
        ],
    },
    python_requires=">=3.7",
)
