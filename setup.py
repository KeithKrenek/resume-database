# setup.py
from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="resume-database",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-cov>=4.1.0",
            "black>=23.3.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",  # Type checking
            "pylint>=2.17.0"  # Code analysis
        ],
        "pdf": [
            "reportlab>=4.0.0"  # PDF generation
        ]
    },
    python_requires=">=3.7",
    author="Your Name",
    author_email="your.email@example.com",
    description="A database system for managing professional experience entries",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KeithKrenek/resume-database",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: Markup",
        "Intended Audience :: End Users/Desktop",
    ],
    entry_points={
        'console_scripts': [
            'resume-db=src.cli:main',  # CLI tool entry point
        ],
    }
)