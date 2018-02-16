from setuptools import find_packages
from setuptools import setup

NAME = 'django-msg'
VERSION = '0.1.0'
SUMMARY = 'Django util package for send email and sms messages'

setup(
    name=NAME,
    version=VERSION,
    description=SUMMARY,
    url='https://github.com/jroslaniec/django-msg',
    author='Jędrzej Rosłaniec',
    author_email='jedr.ros@gmail.com',
    license='MIT',
    install_requires=['django >= 2.0.0', 'django-jsonfield >= 1.0.0'],
    extras_require={
        'celery': ['celery >= 4.0.0'],
        'boto3': ['boto3 >= 1.0.0'],
        'twilio': ['twilio >= 6.0.0'],
        'all': ['celery >= 4.0.0', 'boto3 >= 1.0.0', 'twilio >= 6.0.0'],
    },
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    keywords=('django', 'messages', 'email', 'sms', 'notifications'),
    packages=find_packages(exclude=[
        'examples',
        'docs',
        'tests*',
    ]),
)
