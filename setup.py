import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="tapsilat-py",
    version="2025.12.8.1",
    description="Client SDK for Tapsilat API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tapsilat",
    author_email="support@tapsilat.dev",
    url="https://github.com/tapsilat/tapsilat-py",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "requests>=2.25.0",
    ],
    python_requires=">=3.6",
    project_urls={
        "Source Code": "https://github.com/tapsilat/tapsilat-py",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
