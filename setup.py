from setuptools import setup

setup(name='odmscripting',
      version='3.0',
      description='Toolkit for generating measurement automation scripts for the ODM Acquisition Software.',
      url='http://github.com/jkokorian/odmscripting',
      author='J. Kokorian',
      author_email='J.Kokorian@TUDelft.nl',
      license='GPLv3',
      packages=[
          'odmscripting',
          ],
      entry_points='''
        [console_scripts]
        odms=odmscripting.commandline:cli
    ''',
      install_requires=['Click'],
      zip_safe=False)