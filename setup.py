"""Setup script for Investment Workflow Evaluations."""

from setuptools import setup, find_packages
from pathlib import Path

readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="investment-workflow-evals",
    version="0.1.0",
    description="AI evaluation framework for institutional investment research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Brad Schonhoft",
    url="https://github.com/bdschi1/investment-workflow-evals",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=[
        "pyyaml>=6.0",
        "jsonschema>=4.17.0",
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "llm": [
            "anthropic>=0.18.0",
            "openai>=1.0.0",
        ],
        "studio": [
            "streamlit>=1.30.0",
            "streamlit-sortables>=0.3.0",
            "google-genai>=1.0.0",
            "pymupdf>=1.24.0",
            "pandas>=2.0.0",
            "anthropic>=0.18.0",
            "openai>=1.0.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "iwe-eval=tools.eval_runner:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=[
        "ai-training",
        "rlhf",
        "evaluation",
        "investment-research",
        "finance",
        "domain-expert",
    ],
)
