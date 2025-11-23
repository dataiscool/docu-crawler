from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), 
          encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="docu-crawler",
    version="0.1.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dataiscool/docu-crawler",
    description="Lightweight web crawler library that converts HTML to Markdown",
    author="Fillipi Bittencourt",
    author_email="fahbittencourt@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
    ],
    extras_require={
        "yaml": ["pyyaml>=6.0"],  # Only needed for YAML config file support
        "gcs": ["google-cloud-storage>=2.0.0"],
        "s3": ["boto3>=1.26.0"],
        "azure": ["azure-storage-blob>=12.0.0"],
        "sftp": ["paramiko>=3.0.0"],
        "async": ["aiohttp>=3.8.0", "aiofiles>=23.0.0"],
        "all": [
            "pyyaml>=6.0",
            "google-cloud-storage>=2.0.0",
            "boto3>=1.26.0",
            "azure-storage-blob>=12.0.0",
            "paramiko>=3.0.0",
            "aiohttp>=3.8.0",
            "aiofiles>=23.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "docu-crawler=src.cli:run",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.9",
    keywords=[
        "web crawler",
        "html to markdown",
        "documentation crawler",
        "content extraction",
        "python crawler",
        "web scraping",
        "markdown converter",
        "documentation tool",
        "html parser",
        "website crawler",
        "content migration",
    ],
)