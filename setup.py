# setup.py
"""
Setup script for CrawlerX
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crawlerx",
    version="1.0",
    author="Pwned Bytes",
    description="High-performance terminal-based web crawler for security reconnaissance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pwnedbytes/crawlerx",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.8.0",
        "aiofiles>=0.8.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "colorama>=0.4.4",
    ],
    entry_points={
        "console_scripts": [
            "crawlerx=crawlerx:main",
        ],
    },
)
