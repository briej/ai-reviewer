from setuptools import setup, find_packages

setup(
    name="ai-reviewer",
    version="1.2.0",
    py_modules=["ai_reviewer"],
    packages=["src"],
    install_requires=[
        "click>=8.1.0",
        "requests>=2.31.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-review=ai_reviewer:main",
        ],
    },
    python_requires=">=3.9",
)
