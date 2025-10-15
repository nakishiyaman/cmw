"""
Claude Multi-Worker Framework のセットアップ
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="claude-multi-worker",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="マルチワーカーアーキテクチャでソフトウェア開発を自動化するフレームワーク",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nakishiyaman/claude-multi-worker-framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cmw=cmw.cli:cli",
        ],
    },
)
