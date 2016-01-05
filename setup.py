from distutils.core import setup, Extension
from distutils.command.build import build

version      = '0.6.12'
packages     = ['cf']





setup(name = "cfview",
      long_description = 'GUI for viewing CF files',
      version      = version,
      description  = "GUI for viewing CF files",
      author       = "Andy Heaps",
      maintainer   = "Andy Heaps",
      maintainer_email  = "a.j.heaps@reading.ac.uk",
      author_email = "a.j.heaps@reading.ac.uk",
      url          = "http://climate.ncas.ac.uk/~andy/cfview_sphinx/_build/html/#",
      download_url = "https://github.com/ajheaps/CF-View",
      platforms    = ["Linux"],
      keywords     = ['cf','netcdf','data','science',
                      'oceanography','meteorology','climate'],
      scripts      = ['cfview']
  )


