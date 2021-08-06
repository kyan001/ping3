import setuptools

with open('README.md') as f:
    long_desc = f.read()

setuptools.setup(
    name='ping3',
    description='A pure python3 version of ICMP ping implementation using raw socket.',
    long_description=long_desc,
    long_description_content_type='text/markdown',
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
    ],
    keywords='python3 ping icmp socket tool',
    packages=["ping3"],
    python_requires='>=3',
    install_requires=[],
    extras_require={
        'dev': ['build', 'twine', 'pycodestyle'],
    },
    package_data={},
    data_files=[],
    entry_points={
        'console_scripts': ['ping3=ping3.command_line:main'],
    },
)
