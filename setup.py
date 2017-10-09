from setuptools import setup, find_packages

setup(
    name='pymongokeyset',
    version='1.0.0',
    keywords=('keyset', 'pymongo'),
    description='offset-free (skip-free) paging for pymongo',
    author='ocavue',
    author_email='ocavue@gmail.com',
    url='https://github.com/ocavue/pymongokeyset',
    license='MIT License',
    packages=find_packages(),
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
)
