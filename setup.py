import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
with open("_version.py", encoding='utf-8') as f:
    version = f.read().strip().split(" = ")[1][1:-1]

setuptools.setup(
    name="odscli",
    version=version,
    author="OneDataShare",
    author_email="onedatashare@gmail.com",
    description="The onedatashare.org cli",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/didclab/odscli",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'ods = odscli.odscli:main'
        ]
    },
    install_requires=requirements,
    python_requires=">=3.9",
)
