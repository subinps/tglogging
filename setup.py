import setuptools

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setuptools.setup(
    name="tglogging",
    version="0.0.1",
    author="subinps",
    description="A python package to stream your app logs to a telegram chat in realtime.",
    long_description=readme,
    long_description_content_type="text/markdown",
    project_urls={
        "Tracker": "https://github.com/subinps/tglogging/issues",
        "Source": "https://github.com/subinps/tglogging",
    },
    license="MIT",
    url="https://github.com/subinps/tglogging",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'aiohttp',
        'nest_asyncio'
    ]
)
