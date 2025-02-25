from setuptools import setup, find_packages

setup(
    name='EmotiAI',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'spacy==3.8.4',
        'tensorflow==2.18.0',
        'mlflow==2.20.2',
        'loguru==0.7.3',
        'apache-airflow==2.10.5'
    ],
    entry_points={
        'console_scripts': [
            # Define command-line scripts here
            # 'your_command=your_package.module:function',
        ],
    },
)
