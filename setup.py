from setuptools import setup, find_packages

setup(
    name='pymongokeyset',
    version='0.0.9',
    keywords=('keyset', 'pymongo'),
    description='offset-free paging for pymongo',
    author='ocavue',
    author_email='ocavue@gmail.com',
    url='https://github.com/ocavue/pymongokeyset',
    license='MIT License',
    packages=find_packages(),
    platforms='any',
    install_requires=['pymongo>=3.3.0'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
)
