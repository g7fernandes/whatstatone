from setuptools import setup, find_namespace_packages

name = 'whatstatone'
version = 1
release = 0

setup(
    name=name,
    version=f'{version}.{release}',
    description=('Reads whatsapp history and produces statistics of massage'
                 'and words rates, correlation, cumulative message ranking'
                 'and graphs'),
    url='https://github.com/g7fernandes/whatstatone',
    python_requires='>=3.8',
    scripts=[
        'main.py'],
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'progressbar2'
    ],
    keywords='whatsapp history statistics graph ranking',
    classifiers=[
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_namespace_packages(
        include=['whatstat.*'],
        exclude=[
            '*__init__.py',
            '*c_native*'
        ])
)
