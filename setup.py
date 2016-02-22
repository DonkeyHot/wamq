#!/usr/bin/env python
from __future__ import print_function

from setuptools import setup, find_packages
import wamqd

deps = ['yowsup2', 'stomp.py']

setup(
    name='wamqd',
    version=wamqd.__version__,
    author=wamqd.__author__,
    url='https://gitrepo.theeurasia.kz/eurasia/wamqd',
    install_requires=deps,
    scripts=['bin/wamqd', 'bin/wamqdrun'],
    data_files=[('etc', ['etc/default-wamqd.conf'])],
    author_email='vadim.o.isaev@gmail.com',
    description='Whatsap to MQ services mapper daemon',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 1 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)
