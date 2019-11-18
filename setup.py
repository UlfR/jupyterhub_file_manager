import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jupyterhub_file_manager",
    version="0.0.1",
    author="Frontier.kz",
    author_email="gs@frontier.kz",
    description="jupyterhub file manager",
    long_description="jupyterhub file manager",
    long_description_content_type="text/markdown",
    url="https://frontier.kz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache",
        "Operating System :: PySpark",
    ],
)
