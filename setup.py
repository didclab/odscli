from setuptools import setup, find_packages

setup(

        name ='odscli',

        version ='1.0.0',

        author ='Admin OneDataShare',

        author_email ='admin@onedatashare.org',

        description ='Demo Package for CLI',

        packages = find_packages(),

        entry_points ={

            'console_scripts': [

                'odscli = onedatashare.onedatashare:main'

            ]

        },

        classifiers =(

            "Programming Language :: Python :: 3",

            "Operating System :: OS Independent",

        ),
        install_requires = [
            "requests",
            "pandas",
            "docopt",
            "tabulate",
            "python-dateutil",
            "pytimeparse",
            "pprintpp",
            "plotext"
        ],


        zip_safe = False
)
