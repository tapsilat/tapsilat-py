from setuptools import find_packages, setup

setup(
    name="tapsilat-py",
    version="0.1.0",
    description="Client SDK for Tapsilat API",
    author="Tapsilat",
    author_email="-",
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
