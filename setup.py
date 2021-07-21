from setuptools import setup

setup(name='foliobutler',
	  version='0.41',
	  description='Sync your Interactive Brokers account with your Folio in Foliobutler',
	  url='https://github.com/svenotremba/foliobutler',
	  author='Sven',
	  include_package_data=True,
	  install_requires=[
          'setuptools',
          'click',
          'requests',
          'ib_insync',
          'python_dotenv',
      ],
	  author_email='sven@foliobutler.com',
	  license='MIT',
	  packages=['foliobutler'],
	  zip_safe=False,
	  entry_points='''
	  [console_scripts]
	  foliobutler=foliobutler:click_starter
	  '''
	  )
