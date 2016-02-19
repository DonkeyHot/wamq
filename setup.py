#!/usr/bin/env python
from __future__ import print_function

from setuptools import setup, find_packages

import kz.theeurasia.whatsapp


deps = ['yowsup2']

setup(
    name='whatsapp-mq-whatsapp_mq_service',
    version=kz.theeurasia.whatsapp.__version__,
    url='https://gitrepo.theeurasia.kz/vadim.isaev/whatsapp-mq-service',
    author=kz.theeurasia.whatsapp.__author__,
    tests_require=[],
    install_requires = deps,
    scripts = ['whatsapp_mq_service.py'],
    #cmdclass={'test': PyTest},
    author_email='vadim.o.isaev@gmail.com',
    description='Whatsap to MQ whatsapp_mq_service mapper',
    #long_description=long_description,
    packages= find_packages(),
    include_package_data=True,
    platforms='any',
    #test_suite='',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 1 - Beta',
        'Natural Language :: English',
        #'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    #extras_require={
    #    'testing': ['pytest'],
    #}
)
