#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIDoc Forge - Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="apidoc-forge",
    version="1.0.0",
    author="APIDoc Forge Team",
    author_email="",
    description="Intelligent API Documentation Generator & Sync Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/apidoc-forge",
    py_modules=["apidoc_forge"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "apidoc-forge=apidoc_forge:main",
            "apidocforge=apidoc_forge:main",
        ],
    },
    keywords="api documentation generator python ast docstring markdown html openapi",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/apidoc-forge/issues",
        "Source": "https://github.com/yourusername/apidoc-forge",
        "Documentation": "https://github.com/yourusername/apidoc-forge#readme",
    },
)
