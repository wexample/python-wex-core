from setuptools import setup, find_packages

setup(
    name='wexample-wex-core',
    version=open('version.txt').read().strip(),
    author='weeger',
    author_email='contact@wexample.com',
    description='Wex core',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/wexample/wexample-wex-core',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'click',
        'pydantic',
        'wexample-wex-addon-app',
        'wexample-wex-addon-default',
    ],
    python_requires='>=3.6',
)
