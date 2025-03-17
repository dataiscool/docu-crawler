from setuptools import setup, find_packages

setup(
    name="docu-crawler",
    version="0.1.1",
    description="Documentation Web Crawler that converts HTML to Markdown",
    author="Fillipi Bittencourt",
    author_email="fahbittencourt@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "google-cloud-storage>=2.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "docu-crawler=src.cli:run",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
)