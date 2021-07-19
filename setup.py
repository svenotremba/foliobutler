from setuptools import setup

setup(name='foliobutler',
	  version='0.1',
	  description='Sync your Interactive Brokers account with your Folio in Foliobutler',
	  url='https://github.com/svenotremba/foliobutler',
	  author='Sven',
	  author_email='sven@foliobutler.com',
	  license='MIT',
	  packages=['foliobutler'],
	  zip_safe=False,
	  entry_points='''
	  [console_scripts]
	  foliobutler=foliobutler:click_starter
	  '''
	  )
