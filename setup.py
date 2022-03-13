from distutils.core import setup
setup(
  name = 'siiau-consulta-api',         
  packages = ['siiau-consulta-api'],   
  version = '0.0.0',      
  license='GPL',        
  description = 'Consulta información del SIIAU de la UDG',   
  author = 'Benjamin Ramirez',                   
  author_email = 'chilerito12@gmail.com',      
  url = 'https://github.com/Kyostenas/siiau_consultas_api',   
  download_url = '',    
  keywords = ['console', 'cli', 'siiau', 'udg'],   
  install_requires=[
    'bs4',
    'click',
    'requests',
    'Unidecode',
    'xlwt',
    'beautifulsoup4',
    'tabulate'
  ],
  classifiers=[
    'Development Status :: 0 - Alpha',      
    'Intended Audience :: Developers',      
    'Intended Audience :: Students',      
    'Topic :: Software Development :: Build Tools',
    'License :: GNU Approved :: GPL License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'
    'Programming Language :: Python :: 3.10'
  ],
)