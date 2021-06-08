from distutils.core import setup, Extension
from distutils.command.build import build

packages     = ["cf"]

setup(name = "cf-view",
      long_description = "GUI for viewing CF files",
      version      = "2.0.1",
      description  = "GUI for viewing CF files",
      author       = "Andy Heaps",
      maintainer   = "Andy Heaps",
      maintainer_email  = "andy.heaps@ncas.ac.uk",
      author_email = "andy.heaps@ncas.ac.uk",
      url          = "http://ajheaps.github.io/cf-view",
      download_url = "https://github.com/ajheaps/CF-View",
      platforms    = ["Linux"],
      install_requires = ["cf-python >= 3.8.0",
                          "cf-plot >= 3.1.6",
                          "pyqt >= 5.5.0",
                          ],
      keywords     = ["cf","netcdf","data","science",
                      "oceanography","meteorology","climate"],
      scripts      = ["cfview"]
  )


