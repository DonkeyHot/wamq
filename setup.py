#!/usr/bin/env python
from __future__ import print_function

from setuptools import setup, find_packages
import wamq

deps = ['yowsup2', 'stomp.py']

setup(
    name='wamq',
    version=wamq.__version__,
    author=wamq.__author__,
    url='https://gitrepo.theeurasia.kz/eurasia/wamq',
    tests_require=[],
    install_requires=deps,
    scripts=['bin/wamq', 'bin/wamqd'],
    data_files=[('etc', ['etc/default-wamq.conf'])],
    # cmdclass={'test': PyTest},
    author_email='vadim.o.isaev@gmail.com',
    description='Whatsap to MQ services mapper',
    # long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    # test_suite='',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 1 - Beta',
        'Natural Language :: English',
        # 'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    # extras_require={
    #    'testing': ['pytest'],
    # }
)
