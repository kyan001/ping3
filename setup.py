from setuptools import setup, find_packages

setup(
    name='ping3',
    version='2.1.0',
    description='A pure python3 version of ICMP ping implementation using raw socket. ',
    long_description='Ping3 is a pure python3 version of ICMP ping implementation using raw socket. Note that ICMP messages can only be sent from processes running as root.',
    url='https://github.com/kyan001/ping3',
    author='Kai Yan',
    author_email='kai@kyan001.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='python3 ping icmp socket tool',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    py_modules=["ping3", "errors", "enums"],
    python_requires='>=3',
    install_requires=[],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
)
