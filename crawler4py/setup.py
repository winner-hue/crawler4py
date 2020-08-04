#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

'''
打包crawler4py`
'''

setup(
    name="crawler4py",
    version="0.3",
    author="winner-hub",
    author_email="1344246287@qq.com",
    description=("A distributed crawler framework based on Python"),
    long_description=("A distributed crawler framework based on Python"),
    license="Apache 2.0",
    keywords="crawler4py crawler spider pyspider",
    url="https://github.com/winner-hue/crawler4py",
    packages=['crawler4py.dispatch', 'crawler4py.download', 'crawler4py.extractor', 'crawler4py.storage_dup',
              'crawler4py.util', 'crawler4py'],
    # 需要安装的依赖
    install_requires=[
        'beautifulsoup4>=4.9.1',
        'bs4>=0.0.1',
        'certifi>=2020.6.20',
        'chardet>=3.0.4',
        'DBUtils>=1.3',
        'Faker>=4.1.1',
        'gne>=0.2.1',
        'idna>=2.10',
        'lxml>=4.5.2',
        'numpy>=1.19.0',
        'pika>=1.1.0',
        'psutil>=5.7.0',
        'pymongo>=3.10.1',
        'PyMySQL>=0.9.3',
        'python-dateutil>=2.8.1',
        'PyYAML>=5.3.1',
        'redis>=3.5.3',
        'requests>=2.24.0',
        'requests-file>=1.5.1',
        'six>=1.15.0',
        'soupsieve>=2.0.1',
        'text-unidecode>=1.3',
        'tldextract>=2.2.2',
        'urllib3>=1.25.9',

    ],
    entry_points={'console_scripts': [
        'crawler4py = crawler4py.manager:main',
    ]},

    zip_safe=False
)
