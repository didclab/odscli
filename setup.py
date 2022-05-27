from setuptools import setup, find_packages

setup(

        name ='ods-cmdline',

        version ='1.0.0',

        author ='Admin OneDataShare',

        author_email ='admin@onedatashare.org',

        description ='Demo Package for CLI',

        packages = find_packages(),

        entry_points ={

            'console_scripts': [

                'main = cmdline:main'

            ]

        },

        classifiers =(

            "Programming Language :: Python :: 3",

            "Operating System :: OS Independent",

        ),


        zip_safe = False
)
