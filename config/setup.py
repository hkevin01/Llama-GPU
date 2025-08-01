#!/usr/bin/env python3
"""
Setup script for Llama-GPU package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="llama-gpu",
    version="1.0.0",
    author="Kevin",
    author_email="your.email@example.com",
    description="A high-performance GPU-accelerated inference library for LLaMA models",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/hkevin01/Llama-GPU",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "gpu": [
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "torchaudio>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llama-gpu-benchmark=scripts.benchmark:main",
            "llama-gpu-monitor=scripts.monitor_resources:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.sh"],
    },
    keywords="llama, gpu, inference, machine learning, ai, transformers, pytorch",
    project_urls={
        "Bug Reports": "https://github.com/hkevin01/Llama-GPU/issues",
        "Source": "https://github.com/hkevin01/Llama-GPU",
        "Documentation": "https://github.com/hkevin01/Llama-GPU/tree/main/docs",
    },
) 