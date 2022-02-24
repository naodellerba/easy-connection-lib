import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jeeachinto",
    version="0.0.1",
    author="IISS Luigi Dell' Erba",
    author_email="me@domysh.com",
    install_requires=[],
    description="Use connect to hosts in an easier way",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/naodellerba/jeeachinto",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
)
