from setuptools import setup, find_packages

setup(
    name='DeniceOS',
    version='1.0',
    description='Build system for DeniceOS with GUI bootloader, kernel, and bootable ISO image',
    author='petrospetrosapostolou-bot',
    packages=find_packages(),
    install_requires=[
        'some-required-package', # Add required packages here
    ],
    entry_points={
        'console_scripts': [
            'deniceos-build=build_system:main', # Entry point for build command
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)