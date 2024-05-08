.. _version_3.2:
version 3.2 changes
*******************



0. Map popup changes
=====================


- clean up code for npstere and spstere sensitivity
- rotated option doesn't make it into the plotting code
- rotated option to be insensitive when data is not in rotated coordinates
- map resolution drop added to map options 


::

    Changed



1. Colour bar extensions don't work
===================================

No code for colour bar extensions - levs_extend_min and levs_extend_max were missing.


::

    Code added
    
    
   
2. Code to remove auxiliary coordinates removed
===============================================

Change code to remove extra auxiliary coodinates as this is no longer needed - remove_aux=False


::

    Done
    
    
3. Colour scale code changes
============================

The colour scale code was changed:

- change to viridis - colour scale doesn't change
- output code is cscale='inferno' rather than scale='inferno'

::

    Done   
    
    
    
4. contour levels - bug with nlevs definition as a boolean               
==========================================================

There was a bug in the contour levels code with nlevs definition as a boolean               

::

    Fixed  
    
    
    
5. Maps  - user configuration and saving  
========================================

Maps  - user configuration and saving options added to map popup.


::

    Done      
    
    
    
6. Contour levels  - user configuration and saving     
==================================================

Contour levels  - user configuration and saving options added to map popup.

::

    Done    
    
    
    
7. Colour scale - user configuration and saving         
===============================================

Colour scale - user configuration and saving options added to map popup.  

::

    Done   
    
    
    
8. New sections for user settings to be scrollable
==================================================

New sections for user settings to be scrollable.

::

    Done      
    
    
    
9. New sections for user settings to be visible after clicking a checkbox
=========================================================================

New sections for user settings to be visible after clicking a checkbox.

::

    Done    
    
    
    
10. Defaults file code rewrite
==============================

Defaults file code rewrite to use dictionaries for user defined map, contour level and colour scale options.

::

    Done      
    
    
    
11. Issues with cf-python 3.14.0 investigated
=============================================

Issues with cf-python 3.14.0 were investigated.  These mostly seemed related to the version of netCDF4 with 1.6.1 causing issues.  With a fresh install a few weeks later the issues had gone away so it is assumed that this was fixed somewhere in conda.


::

    Investigated
   

    
12. Check all menus look okay and adjust spacing if necessary         
=============================================================

Check all menus and adjust with hbox.addStretch(1) as required   

::

    Done      
   
                      
      
13. New property popup window to properties popup needs recoding
================================================================

The new property popup window to properties popup needed recoding.

::

    Done      
                       
                      
    
14. Doc strings for all routines
================================

Doc strings were added for all routines.

::

    Done      
   
                      

15. Make a plot code - rework map settings
==========================================

Rework code for making a plot: map settings
Use dictionaries for working out settings and code generation.


::

    Done      
                       
                      
     
16. Make a plot code - rework colour settings
=============================================

Rework code for making a plot: map settings
Use dictionaries for working out settings and code generation.


::

    Done      
                        
                      
                      
     
17. Make a plot code - rework contour level settings
====================================================

Rework code for making a plot: map settings
Use dictionaries for working out settings and code generation.

::

    Done      
                 

     
18. netCDF file with no fields but doesn't produce a sensible error
===================================================================

A netCDF file with no fields but doesn't produce a sensible error.

::

    Corrected    
                        
                      
                      
19. Update cfview interpolation code
====================================

Update interpolation to use a sequence of Coordinate instances.  This changed in cf-python at version 3.14.1.

- g = f.regrids({'longitude': lons, 'latitude': lats}, method=method)
- becomes
- g = f.regrids([lats, lons], method=method)
                      

::

    Done                        



20. Changes to cope better with dodgy data
==========================================

Changes to various parts of cfview were made to cope better with some dodgy data found in cn134a.pl1m_195006-195006.nc

- cannot read - cf-python issue with a dodgy 7th field - no data
- cf-view now has an issue with this data
- find_dim_names - have five domain axes and four coordinates
- change loop to check for coordinate type to go over coords rather than daxes
- field 5 fails as the data is dodgy - subspace fails in plot routine - add an exception test


::

    Done   

                      
                  
21. Remove references to plotvars.stored collapses and plotvars.stored dimensions
=================================================================================

Remove references to plotvars.stored collapses and plotvars.stored dimensions.
These are now plotvars.stored['f0']['collapses'] and plotvars.stored['f0']['axes']

::

    Done                         
                      


22. Field search code update
============================

Field search code update.  A new field gets lost internally and doesn't display as expected.

::

    Done   



23. Stray print removal
=======================

A stray print statement was removed.

::

    Done   


24. Stray print removal - and again
===================================

A stray print statement was removed.

::

    Done   


25. Support for 2D lon-lat data added
=====================================

Support for 2D lon-lat data contouring and blockfill was added.


::

    Done   








