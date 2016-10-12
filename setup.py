from distutils.core import setup, Extension
from distutils.command.build import build

version      = '1.0.4'
packages     = ['cf']





setup(name = "cf-view",
      long_description = 'GUI for viewing CF files',
      version      = version,
      description  = "GUI for viewing CF files",
      author       = "Andy Heaps",
      maintainer   = "Andy Heaps",
      maintainer_email  = "andy.heaps@ncas.ac.uk",
      author_email = "andy.heaps@ncas.ac.uk",
      url          = "http://ajheaps.github.io/cf-view",
      download_url = "https://github.com/ajheaps/CF-View",
      platforms    = ["Linux"],
      keywords     = ['cf','netcdf','data','science',
                      'oceanography','meteorology','climate'],
      scripts      = ['cfview']
  )


