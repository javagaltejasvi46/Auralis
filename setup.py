"""
Setup script for AURALIS backend
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="auralis-backend",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Medical Voice Transcription Backend with Faster-Whisper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/auralis",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10,<3.14",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "websockets>=12.0",
        "deep-translator>=1.11.4",
        "sqlalchemy>=2.0.23",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
        "requests>=2.31.0",
        "tqdm>=4.66.1",
        "pyyaml>=6.0.1",
        "typing-extensions>=4.8.0",
    ],
    extras_require={
        "whisper": [
            "faster-whisper>=1.0.0",
            "ctranslate2>=4.0.0",
            "huggingface-hub>=0.21.0",
            "tokenizers>=0.13.0",
            "av>=16.0.0",
            "numpy>=1.24.0",
            "filelock>=3.12.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "auralis-api=main:main",
            "auralis-transcribe=transcription_server:main",
        ],
    },
)
