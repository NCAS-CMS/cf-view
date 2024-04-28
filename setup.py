from setuptools import setup

setup(name = "cf-view",
    long_description = "GUI for viewing CF files",
    version      = "3.3.0",
    description  = "GUI for viewing CF files",
    author       = "Andy Heaps",
    maintainer   = "Sadie Bartholomew",
    maintainer_email  = "sadie.bartholomew@ncas.ac.uk",
    url          = "http://ajheaps.github.io/cf-view",
    download_url = "https://github.com/ncas-cms/cf-view",
    platforms    = ["Linux", "MacOS"],
    license="MIT",
    install_requires = ["cf-python>=3.8.0",
                        "cf-plot>=3.1.6",
                        "PyQt6",
                        ],
    keywords     = ["cf","netcdf","data","science",
                    "oceanography","meteorology","climate"],
    scripts      = ["cfview"]
  )


