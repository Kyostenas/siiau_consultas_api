from distutils.core import setup

from importlib_metadata import entry_points

def readfile(filename):
  with open(filename, 'r+') as f:
    return f.read()

setup(
  name = 'siiau-consultas-api',         
  packages = ['siiau_consultas_api'],   
  version = '0.0.0',      
  description = 'Consulta información del SIIAU de la UDG',
  long_description=readfile('README.md'),
  author = 'Benjamin Ramirez',                   
  author_email = 'chilerito12@gmail.com',      
  url = 'https://github.com/Kyostenas/siiau_consultas_api',   
  license=readfile('LICENSE'),        
  download_url = '',    
  keywords = ['console', 'cli', 'siiau', 'udg'],   
  install_requires=[
    'bs4==0.0.1',
    'click==8.0.4',
    'requests==2.27.1',
    'Unidecode==1.3.4',
    'xlwt==1.3.0',
    'beautifulsoup4==4.10.0',
    'tabulate==0.8.9',
    'alive-progress==2.3.1',
  ],
  classifiers=[
    'Intended Audience :: Developers',      
    'Intended Audience :: Students',      
    'License :: GNU Approved :: GPL License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.8',
  ],
  entry_points={
    'console_scripts': [
      'siiaucli = siiau_consultas_api:main'
    ]
  }
)