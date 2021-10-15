from setuptools import setup

setup(name = "cf-view",
    long_description = "GUI for viewing CF files",
    version      = "2.5.0",
    description  = "GUI for viewing CF files",
    author       = "Andy Heaps",
    maintainer   = "Andy Heaps",
    maintainer_email  = "andy.heaps@ncas.ac.uk",
    author_email = "andy.heaps@ncas.ac.uk",
    url          = "http://ajheaps.github.io/cf-view",
    download_url = "https://github.com/ajheaps/CF-View",
    platforms    = ["Linux", "MacOS"],
    license="MIT",
    install_requires = ["cf-python>=3.8.0",
                        "cf-plot>=3.1.6",
                        "PyQt5",
                        ],
    keywords     = ["cf","netcdf","data","science",
                    "oceanography","meteorology","climate"],
    scripts      = ["cfview"]
  )


