import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csv_file_validator",
    version="0.0.1",
    author="datahappy1",
    author_email="",
    description="csv file validation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datahappy1/csv_file_validator",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
