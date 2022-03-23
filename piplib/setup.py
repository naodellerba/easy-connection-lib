import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jeeachinto",
    version="0.2.0",
    author="IISS Luigi Dell' Erba",
    author_email="me@domysh.com",
    install_requires=[],
    description="Connect to hosts in an easier way",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/naodellerba/easy-connection-lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=2.7',
)
