from setuptools import setup

setup(
    name='froggy',
    version='0.1.1',    
    description='Froggy friend!',
    url='',
    author='2sleepy4u',
    author_email='riccardo.zancan00@gmail.com',
    license='BSD 2-clause',
    packages=['froggy'],
    package_data={
        'froggy': ['/images/frog.png'],
    },
    install_requires=[ "PyQt5"
                      , "randfacts"
                      , "ollama"
                      ],
    entry_points={
        'console_scripts': [
            'froggy=froggy.main:main',  # Adjust as needed
        ],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
