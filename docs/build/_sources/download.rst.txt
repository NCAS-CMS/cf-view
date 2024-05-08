Download/Install
****************


cf-view is available for our supported platforms of Linux and Mac OSX.  If you are using Windows then installing the Microsoft Windows Subsystem for Linux will provide Linux access on that platform.


cf-view is already installed on the following computers
=======================================================

JASMIN: source /home/users/ajh/cfview_install/bin/cfview_setup.sh

ARCHER2: source /home/n02/n02/ajh/cfview_install/bin/cfview_setup.sh

Reading RACC: source /share/apps/NCAS/cfview_install/bin/cfview_setup.sh




To install cf-view
==================

Simplified install process, download is 400MB, unpacked Python distribution is 1.5GB:

::

   Linux:   wget http://gws-access.jasmin.ac.uk/public/ncas_climate/ajh/cfview_install/cfview_install.sh
   Mac:     curl -O -L http://gws-access.jasmin.ac.uk/public/ncas_climate/ajh/cfview_install/cfview_install.sh
   
   bash cfview_install.sh




Or - make your own installation:

Download and install the latest Miniconda Python if this is not already installed. 

::

   conda update -n base -c defaults conda
   conda install -c conda-forge pip udunits2 cartopy
   pip install cf-python cf-plot cf-view


A conda-forge package for cf-view is in preparation which will simplify the install process.






To run cf-view
==============

::

   cfview <optional netCDF, Met Office PP or fields file(s)>


When starting cfview for the first time it might take twenty or so seconds to start while the Matplotlib plotting library does some initialisation.



|
|
|
|
|
|
|
| 


