from setuptools import setup 

setup(name='optimizelyAPI',
      version='0.3',
      description='Optimizely REST and Event API client package',
      packages=['optimizelyAPI'],
      author='Peter Katsos',
      autor_email='peterlouiskatsos@gmail.com',
      install_requires=[
          'numpy',
          'pandas',
          'bravado'
      ],
      zip_safe=False)