# cf-view

## Exploration & plotting GUI for netCDF & Met Office format data

### Overview

**cf-view is a Graphical User Interface (GUI) for earth science and aligned
research which supports the exploration, analysis and plotting of netCDF
and Met Office format (PP or fields) data.**

It is intended to be an updated
replacement and improvement on
the [xconv+](https://ncas-cms.github.io/xconv-doc/html/index.html) tool,
using the power of:

* Python ([PyQt](https://www.riverbankcomputing.com/software/pyqt/)) for the GUI;
* [cf-plot](https://github.com/NCAS-CMS/cf-plot)
  (building on top of
  [matplotlib](https://matplotlib.org/) and
  [Cartopy](https://scitools.org.uk/cartopy/docs/latest/)) for the plotting;
* [cf-python](https://ncas-cms.github.io/cf-python/) for the data
  reading, processing and analysis; and
* [cfdm](https://ncas-cms.github.io/cfdm/) for the underlying data model.

It is designed to be a useful tool for environmental, earth
and aligned sciences, for example to facilitate climate and meteorological
research. cf-view is developed and maintained by the
[NCAS-CMS](https://cms.ncas.ac.uk/index.html) group, part of
[NCAS](https://ncas.ac.uk/).


![cf-view screenshot preview](media/cfview-screenshot-preview-1.png "Preview of the cf-view GUI")


### Documentation

For now, please see the static cf-view documentation hosted at 
[https://ajheaps.github.io/cf-view](https://ajheaps.github.io/cf-view)
(`https://ajheaps.github.io/cf-view`), noting that soon the canonical
location for the full documentation will be moved to be under the NCAS-CMS
organisation space, at `https://ncas-cms.github.io/cf-view/build/index.html`
(these pages do not currently exist).


### Quickstart

After installing (see below), start cf-view through the command line via
running:

```
cfview
```

or if you wish to start working with a specific file, add a positional
argument:

```
cfview <file>
```

where `<file>` is the path to the netCDF, Met Office PP or fields file.

*Note:* when starting cf-view for the first time, it might take twenty or
so seconds to start while matplotlib does some initialisation work.


### Installation

There are two main ways to install cf-view: through a package manager, or
by downloading and running a dedicated installation script.


#### Installation by package manager

You can use `pip` with `conda` (or similar package managers such
as `mamba`) as follows.

To use `pip`, run:

```bash
pip install cf-python cf-plot cf-view
```

In future you will be able to install cf-view and all of its dependencies
fully with `conda`, but for now only the dependencies are installable
this way, like so:

```bash
conda install -c ncas -c conda-forge cf-python cf-plot udunits2
```

and you must use e.g. `pip` to install the cf-view library itself.


#### Installation by download script

Alternatively, to install cf-view with its required dependencies, you can
download from source. For Linux, run:

```bash
wget http://gws-access.jasmin.ac.uk/public/ncas_climate/ajh/cfview_install/cfview_install.sh
```

or for Mac, instead run:

```bash
curl -O -L http://gws-access.jasmin.ac.uk/public/ncas_climate/ajh/cfview_install/cfview_install.sh
```

and then install by running the `cfview_install.sh` script, for example with:

```bash
bash cfview_install.sh
```

#### Further installation information

More detail about installation is provided on the
[installation page](https://ajheaps.github.io/cf-view/download.html)
(`https://ajheaps.github.io/cf-view/download.html`)
of the documentation.


### Contributing

Everyone is welcome to contribute to cf-view in the form
of bug reports, documentation, code, design proposals, and more.

Contributing guidelines will be added to the repository shortly.


### Help: Issues, Questions, Feature Requests, etc.

For any queries, see the
[guidance page](https://ajheaps.github.io/cf-view/issues.html)
(`https://ajheaps.github.io/cf-view/issues.html`).
