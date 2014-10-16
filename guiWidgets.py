
import pygtk
import gtk, gobject, pango
import cf
import unittest, numpy
from collections import OrderedDict


class guiFrame(gtk.Frame):
    ''' Mixin to simplify framesetup with size and label '''
    xsize,ysize=800,600
    def __init__(self,title=None,xsize=None,ysize=None):
        super(guiFrame,self).__init__()
        
        if title is not None: self.set_label(title)
        
        if xsize is not None: self.xsize=xsize
        if ysize is not None: self.ysize=ysize
        self.set_size_request(self.xsize,self.ysize)
            
class scrolledFrame(guiFrame):
    ''' Provides a scrolled window inside a frame '''
    def __init__(self,title=None,xsize=None,ysize=None):
        ''' Initialise with optional title and size '''
        super(scrolledFrame,self).__init__(title=title,xsize=xsize,ysize=ysize)
        # now set up scrolled window    
        self.sw=gtk.ScrolledWindow()
        self.sw.set_border_width(5)
        self.sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        # the following doesn't seem to get honoured, even
        # though if we get it back, it's definitely set shadow_none
        self.sw.set_shadow_type(gtk.SHADOW_NONE)
        # print 'shadow',self.sw.get_shadow_type()
        # if we have to have a frame drawn around the sw, 
        # and it seems we do, we might as well have some space around it.
       
        self.add(self.sw)
        # put a vbox in the scrolled window for content
        self.vbox=gtk.VBox()
        self.sw.add_with_viewport(self.vbox)
    def show(self):
        super(scrolledFrame,self).show_all()    
        
def smallLabel(text,size='small',wrap=True):
    ''' Convenience method for providing a small multi-line gtk.Label '''
    string="<span size='%s'>%s</span>"%(size,text)
    label=gtk.Label(string)
    label.set_use_markup(True)
    label.set_line_wrap(wrap)
    if wrap:
        label.set_justify(gtk.JUSTIFY_LEFT)
    return label
    
def smallButton(text,size='small'):
    ''' Makes a small button '''
    text="<span size='small'>%s</span>"%text
    b=gtk.Button(text)
    label=b.get_child()
    label.set_use_markup(True)
    return b
    
class myCombo(gtk.HBox):
    ''' Mixin convenience class for small combo boxes with labels '''
    def __init__(self,content,label=None,initial=None, callback=None,fontSize=8,
                 padding=2):
        ''' Initialise with content, label, callback and fontsize '''
        super(myCombo,self).__init__()
        self._model=gtk.ListStore(gobject.TYPE_STRING)
        self._box=gtk.ComboBox(self._model)
        txt=gtk.CellRendererText()
        self._box.pack_start(txt,True)
        self._box.add_attribute(txt,'text',0)
        txt.set_property('font','sans %s'%fontSize)
        if label is not None:
            mylabel=smallLabel(label)
            self.pack_start(mylabel,padding=padding,expand=False)
        if callback is not None:
            self._callback=callback
            self._box.connect('changed',self.__myComboCallback)
        self.pack_start(self._box,padding=padding,expand=True) 
        for item in content:
            self._model.append([item])
        self.content=content
        if initial is not None: self.set_value(initial)
    def set_value(self,v):
        ''' Set active value of combobox '''
        if v not in self.content:
            raise ValueError('Attempt to set combobox to non valid value')
        else:
            self._box.set_active(self.content.index(v))
    def get_value(self):
        ''' Returns value in combobox '''
        return self._model[self._box.get_active()][0]
    def __myComboCallback(self,w):
        ''' Return current value of widget as argument to the callback '''
        self._callback(w,self.get_value())
    def show(self):
        super(myCombo,self).show_all()    
        

class collapseCombo(myCombo):
    ''' Choose from the available collapse operators '''
    options=OrderedDict([(' ',None),('min','min'),('max','max'),
                         ('mid','mid_range'),('sum','sum'),('mean','mean'),
                         ('s.d.','standard_deviation'),('var','variance')])
    def __init__(self,initial='None',callback=None,fontSize='8'):
        ''' Initialise with the current value, a callback to be called if
        the value changes, and if necessary, a font size '''
        super(collapseCombo,self).__init__(
            self.options.keys(),initial=initial,callback=callback,fontSize=fontSize)
        # FIXME. I think I want the size request to be 20, but the
        # problem is that the text on the button disappears. I need
        # to shrink the container button, but I don't know how to do
        # that, yet. (Which would hopefully fix the off-centred text
        # as well.
        self._box.set_size_request(40,22)
    def get_value(self):
        ''' Override mixin method so we get the long name, after combobox
        only shows the short name. '''
        r=super(collapseCombo,self).get_value()
        return self.options[r]
    
class arrayCombo(myCombo):
    ''' Returns a labeled array combobox widget which has set_value, get_value 
    and show methods. '''
    def __init__(self,vector,label=None,callback=None,initial=None,padding=3):
        ''' Initialise with a vector to put in the combobox.
        Optional arguments:
            label - the combobox label
            callback - a tuple with a callback to pass the current value to 
                       after it has been changed and something else that the
                       callback knows how to interpret, e.g. (callback, target)
                       will result in a functional call to callback(target,value).
            initial - is an initial value
            padding - the typical hbox padding.
            '''
        self.callback=callback
        # I think we can afford a copy
        options=[str(i) for i in vector]
        
        super(arrayCombo,self).__init__(options,initial=initial,label=label,
                                        callback=self.__aCcallback)
        # following magic sets the dropdown to use scrollbars (and be much faster)
        style = gtk.rc_parse_string('''
        style "my-style" { GtkComboBox::appears-as-list = 1 }
        widget "*.mycombo" style "my-style" ''')
        self._box.set_name('mycombo')
        self._box.set_style(style)
        
        # the natural size request seems to be (106,25), but
        # it could be much smaller given our smaller text
        self._box.set_size_request(60,20)
      
    def set_value(self,v):
        ''' Set active value of combobox '''
        # need to override the mixin class to ensure type conversion from float
        super(arrayCombo,self).set_value(str(v))
    def get_value(self):
        ''' Returns value in combobox '''
        # need to override the mixin class to ensure type conversion to float
        return float(super(arrayCombo,self).get_value())
    def __aCcallback(self,entry,value):
        ''' This is the internal component of the optional callback '''
        if self.callback is not None:
            self.callback[0](self.callback[1],value)  

################################################################################
# EVERYTHING ABOVE IS gtk aware, but not cf aware
# EVERYTHING BELOW is *both* gtk aware and cf aware
################################################################################    
    
def cfkeyvalue(f,p):
    ''' Utility method for making a pango string from a cf object <f> and 
    a specific property <p>. '''
    s='<b>%s</b>'%p
    if hasattr(f,p):
        v=getattr(f,p)
    else: return ''
    if hasattr(v,'__call__'): v=str(v())
    return '%s: %s'%(s,v)    
    
def cfdimprops(f):
    ''' Utility method for obtaining dimension properties from a CF field
    and converting them into a list of pango strings. '''
    r=[]
    
    for p in ['X','Y','Z','T']:
        s='<b>%s</b>:\n'%p
        coord=f.coord(p)
        if coord is None: continue
        for k in coord.properties:
            kv=cfkeyvalue(coord,k)
            if kv<>'':s+='     %s\n'%kv
        s+='     <b>Units: </b>%s'%str(f.coord(p).data.Units)
        r.append(s)
    return r
            
class fieldMetadata(scrolledFrame):
    ''' Provides a frame widget for field metadata, and packs it with content
    via the set_data method which takes one or more fields in a list. If 
    multiple fields are provided, show the metadata common to the fields. '''
    
    size='small'   # font size for the content
    
    def __init__(self,title='Field Metadata',xsize=None,ysize=None):
        ''' Initialise '''
        super(fieldMetadata,self).__init__(title=title,xsize=xsize,ysize=ysize)
        # Tell the set_data method when it's the first time through.
        self.shown=False
        
    def set_data(self,fields):
        ''' Show field metadata information for a specific field.
        If more than one field in fields, show common metadata. '''
        common=[]
        if len(fields)>1:
            string='<i>Common Field Metadata</i>\n'
            # find intersection, don't you love python?
            sets=[set([cfkeyvalue(f,p) for p in f.properties]) for f in fields]
            u=set.intersection(*sets)
        else:
            string=''
            # just show the field properties
            u=[cfkeyvalue(fields[0],p) for p in fields[0].properties]
        for i in u: 
            if i<>'':string+='%s\n'%i
        if self.shown:  
            self.label.destroy()
            self.hbox.destroy()  # we don't want it to be the old size
        # now build the label
        self.label=smallLabel(string)
        # shove it in a box and make sure it doesn't expand.
        self.hbox=gtk.HBox()
        self.hbox.pack_start(self.label,expand=False,padding=5)
        self.vbox.pack_start(self.hbox,expand=False,padding=5)
        self.show()
        self.shown=True
        

    
class gridMetadata(scrolledFrame):
    ''' Shows grid metadata for a field or set of fields '''
    def __init__(self,title='Grid Metadata',xsize=None,ysize=None):
        ''' Initialise as an empty vessel which gets populated
        via the set data method.'''
        super(gridMetadata,self).__init__(title=title,xsize=xsize,ysize=ysize)
        self.shown=False
    def set_data(self,fields):
        ''' Takes a set of cf fields and extracts their grid information.
        If their is common information is common, it says so. '''
        common=[]
        if len(fields)>1:
            string='<i>Common Grid Metadata</i>\n'
            # find intersection, don't you love python?
            sets=[set(cfdimprops(f))for f in fields]
            u=set.intersection(*sets)
        else:
            string=''
            # just show the field properties
            u=cfdimprops(fields[0])
        for i in u: 
            if i<>'':string+='%s\n'%i
        if self.shown:  
            self.label.destroy()
            self.hbox.destroy()  # we don't want it to be the old size
        # now build the label
        self.label=smallLabel(string)
        # shove it in a box and make sure it doesn't expand.
        self.hbox=gtk.HBox()
        self.hbox.pack_start(self.label,expand=False,padding=5)
        self.vbox.pack_start(self.hbox,expand=False,padding=5)
        self.show()
        self.shown=True
        
class fieldSelector(guiFrame):
    ''' Provides a widget for data discovery, depends on the CF api
    to load data through the set_data method. '''
    
    def __init__(self, selection_callback,xsize=None,ysize=None):
        ''' Initialise as an empty vessel which gets populated when
        via the set_data method. Needs a selection callback for when
        the selection is changed. '''
        
        super(fieldSelector,self).__init__(title='Field Selector',xsize=xsize,ysize=ysize)   
        
        self.selection_callback=selection_callback
      
        # use a scrolled window to hold a list store for examining variables
        self.sw=gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        
        # create a tree view list store
        self.view=gtk.TreeView(None)
        self.view.set_search_column(1)          # search on field names
        self.view.set_rules_hint(True)          # nice alternating lines
        self.view.set_headers_clickable(True)   # can reorder on column headers

        # now set a liststore for the treeview.
        # [Index, Field Name, Length of X Array, Length of Y Array, Length of Z Array and Length of T Array]
        self.fieldStore = gtk.ListStore(int, str, int, int, int, int)
        
        # bind the store to the tree view
        self.view.set_model(self.fieldStore)      
        
        #The cell renderer is used to display the text in list store.
        self.fieldRenderer = gtk.CellRendererText() 
        for k,v in (('xpad',10),('size-points',8)):
            self.fieldRenderer.set_property(k,v)
            
        self.columns_are_setup=False
        
        # Allow multiple selections
        treeselector=self.view.get_selection()
        treeselector.set_mode(gtk.SELECTION_MULTIPLE)
        
        #Add the tree view to the scrolled window and the sw to self (frame)
        self.sw.add(self.view)
        self.add(self.sw)
            
    def _setColumns(self):
        ''' Set's the columns. We do this as late as possible, so
        the widget knows how big it is and get can the sizing right.'''
        
        #column headings
        headings=['Index', 'Field Name', 'X', 'Y', 'Z', 'T'] 
        i=0

        # work out how big we are so we can get the right column sizes
        allocation=self.get_allocation()
        xsize=allocation[2]-allocation[0]
        
        for h in headings:
            
            col=gtk.TreeViewColumn(h,self.fieldRenderer,text=i)
            col.set_sort_column_id(i)    # is sortable
            col.set_alignment(0.5)  
            i+=1
                
            #Each column is fixed width, dependant on screen size
            col.set_property('sizing',gtk.TREE_VIEW_COLUMN_FIXED)
            
            if h=='Field Name': 
                col.set_fixed_width(int(xsize * 0.5))
            else:
                col.set_fixed_width(int(xsize * 0.1))
            
            #Add the column created to the tree view
            self.view.append_column(col)
        
        #When the selection is changed the function selectionChanged is called.
        self.fieldChoice = self.view.get_selection()
        self.fieldChoice.connect("changed", self.changed)
        self.columns_are_setup=True
    
    def cf_field_to_columns(self,index,field):
        ''' Given a CF field, convert to list store data structure '''
        if hasattr(field,'standard_name'):
            name=field.standard_name
        else: name=field.long_name
        # FIXME, what happens if X, Y,Z or T are not present?
        (nx,ny,nz,nt) = (len(field.item('X').array), 
                        len(field.item('Y').array), 
                        len(field.item('Z').array) , 
                        len(field.item('T').array))
        return (index,name,nx,ny,nz,nt)
        
    def set_data(self,data):
        ''' Loop over fields in data file and display'''
        
        if not self.columns_are_setup: self._setColumns()
        
        # clear existing content, if any
        if len(self.fieldStore)<>0:
            self.fieldStore.clear()
            
        # loop over fields
        i=0
        for field in data:
            self.fieldStore.append(self.cf_field_to_columns(i,field))
            i+=1
        
    def changed(self,treeSelection):
        ''' Called when the liststore changes '''
        (treestore, pathlist) = treeSelection.get_selected_rows()
        # at this point pathlist is a list of tuples that looks like
        # [((6,),(7,), ...]
        # These indices are the field indexes in the file!
        indices=[i[0] for i in pathlist]
        self.selection_callback(indices)
    
    def show(self):
        ''' Show widgets '''
        super(fieldSelector,self).show_all()
        
class cfGrid(object):
    ''' This is the grid part of a CF field, basically
    a convenience API into it. '''
    def __init__(self,field):
        ''' Initialise with a field. Provides two dictionaries
        which are keyed by the grid dimension names:
            .axes is the axes dictionary, and
            .drange is a set of min,max tuples for each axis.
        There must be a cleaner way to do this.
        # FIXME DAVID
        '''
        self.domain=field.domain
        self.axes={}
        self.drange={}
        self.names={}
        # FIXME, use CF grid information, not this ...
        #order=['X','Y','Z','T']
        #for k in order ...field.dim[k]
        self.shortNames={'dim0':'T','dim1':'Z','dim2':'Y','dim3':'X'}
        for k in self.domain.data_axes():
            cfdata=field.dim(k)
            self.axes[k]=cfdata
            self.drange[k]=min(cfdata.array),max(cfdata.array)
            self.names[k]=self.domain.axis_name(k)
        
class gridSelector(guiFrame):
    ''' Provides a selector for choosing a sub-space in a multi-dimensional field'''
    def __init__(self,xsize=None,ysize=None):
        ''' Constuctor just sets some stuff up '''
        super(gridSelector,self).__init__(title='Grid Selector',xsize=xsize,ysize=ysize)
        self.vbox=gtk.VBox()
        self.add(self.vbox)
        self.shown=False
        
    def set_data(self,field):
        ''' Set data with just one field '''
        self.grid=cfGrid(field)
        self._makeGui()
        self.show()
        
    def _makeGui(self):
        ''' Make the GUI for a specific domain '''
        if self.shown:
            for d in self.sliders:
                self.sliders[d].destroy()
        self.sliders={}
        self.combos={}
        for dim in self.grid.axes:
            box=self._makeSlider(dim)
            self.sliders[dim]=box
            self.vbox.pack_start(box,expand=False)
        self.shown=True
            
    def _makeSlider(self,dim):
        ''' Makes an entry for choosing array max and minima and
        for selecting a collapse operator. Note that the
        max grid selector slaves from the min grid selector,
        so users should always use that one first.'''
        maxcombo=arrayCombo(self.grid.axes[dim].array,'Max:')
        mincombo=arrayCombo(self.grid.axes[dim].array,'Min:',
                    callback=(self._linkCallback,maxcombo),
                    initial=self.grid.drange[dim][0])
        colcombo=collapseCombo(initial=' ')
        self.combos[dim]=(mincombo,maxcombo,colcombo)        
        # can't do this one at initial value coz it gets reset by the link
        maxcombo.set_value(self.grid.drange[dim][1])
        # all the box and border malarkey to make it look nice
        vbox=gtk.VBox()
        bbox=gtk.HBox()
        if len(self.grid.axes[dim].array)>1:
            bbox.pack_start(colcombo,padding=2)
            bbox.pack_start(mincombo,padding=2)
            bbox.pack_start(maxcombo,padding=2)
        else:
            bbox.pack_start(smallLabel('Value %s'%self.grid.axes[dim].array[0]))
        vbox.pack_start(bbox,padding=5)
        frame=gtk.Frame(self.grid.names[dim])
        frame.set_border_width(5)
        frame.add(vbox)
        return frame
    
    def _linkCallback(self,target,value):
        ''' Takes a callback from a mincombo, which has been changed to value
        and updates the maxcombo to this value as an initial condition. '''
        target.set_value(value)
        
    def get_selected(self):
        ''' Return the combobox selections as they currently stand '''
        selections={}
        if not self.shown: return None
        for dim in self.combos:
            selections[dim]=(self.combos[dim][0].get_value(),
                             self.combos[dim][1].get_value(),
                             self.combos[dim][2].get_value())
        return selections
    
    def show(self):
        ''' Show all widgets '''
        super(gridSelector,self).show_all()
            
class guiInspect(guiFrame): 
    ''' Provides a file inspection widget '''
    def __init__(self,selector):
        super(guiInspect,self).__init__()
    def reset(self):
        ''' Handle changing the data file '''
        pass

class guiGallery(guiFrame):
    ''' Provides a gallery of plots '''
    def __init__(self,selector):
        super(guiGallery,self).__init__()
    def reset(self):
        ''' Handle changing the data file'''
        pass
        
class QuarterFrame(guiFrame):
    ''' Provides a frame with four sub-frames in the four quarters
    topLeft, topRight, bottomLeft, bottomRight. Each of these
    is exposed for use, e.g. self.topLeft ...
    Optional arguments include the xsize and ysize of the overall frame,
    otherwise defaults are used. '''
    # these are the default window ratio splits
    xsplit=[0.6,0.4]
    ysplit=[0.7,0.3]
    def __init__(self,xsize=None,ysize=None):
        ''' Initialise with optional quarter frame size '''
        super(QuarterFrame,self).__init__(xsize=xsize,ysize=ysize)
        self.set_shadow_type(gtk.SHADOW_NONE)  # no border
        # two boxes inside a vbox for the frames to sit in
        vbox=gtk.VBox()
        hboxTop=gtk.HBox()
        hboxBottom=gtk.HBox()
        vbox.pack_start(hboxTop)
        vbox.pack_start(hboxBottom)
        self.add(vbox)
        # find out the frame sizes
        ls,rs=int(self.xsplit[0]*self.xsize),int(self.xsplit[1]*self.xsize)
        ts,bs=int(self.ysplit[0]*self.ysize),int(self.ysplit[1]*self.ysize)
        # and then create them
        self.topLeft=guiFrame(xsize=ls,ysize=ts)
        self.topRight=guiFrame(xsize=rs,ysize=ts)
        self.bottomLeft=guiFrame(xsize=ls,ysize=bs)
        self.bottomRight=guiFrame(xsize=rs,ysize=bs)
        # don't want borders around the subframes:
        for f in [self.topLeft,self.topRight,self.bottomLeft,self.bottomRight]:
            f.set_shadow_type(gtk.SHADOW_NONE)
        # and place them in the boxes
        hboxTop.pack_start(self.topLeft)
        hboxTop.pack_start(self.topRight)
        hboxBottom.pack_start(self.bottomLeft)
        hboxBottom.pack_start(self.bottomRight)
    def show(self):
        ''' Show internal widgets '''
        self.show_all()
        
def makeDummy(standardname,longname):
    ''' Returns a dummy cf field object for testing, with
    standardname <standardname> and variablename <longname> from
    http://cfpython.bitbucket.org/docs/0.9.8.3/field_creation.html '''
    #---------------------------------------------------------------------
    # 1. Create the field's domain items
    #---------------------------------------------------------------------
    # Create a grid_latitude dimension coordinate
    dim0 = cf.DimensionCoordinate(properties={'standard_name': 'grid_latitude'},
                          data=cf.Data(numpy.arange(10.), 'degrees'))

    # Create a grid_longitude dimension coordinate
    dim1 = cf.DimensionCoordinate(data=cf.Data(numpy.arange(9.), 'degrees'))
    dim1.standard_name = 'grid_longitude'
    
    # Create a time dimension coordinate (with bounds)
    bounds = cf.CoordinateBounds(
    data=cf.Data([0.5, 1.5], cf.Units('days since 2000-1-1', calendar='noleap')))
    dim2 = cf.DimensionCoordinate(properties=dict(standard_name='time'),
                                  data=cf.Data(1, cf.Units('days since 2000-1-1',
                                                           calendar='noleap')),
                                  bounds=bounds)
    
    # Create a longitude auxiliary coordinate
    aux0 = cf.AuxiliaryCoordinate(data=cf.Data(numpy.arange(90).reshape(10, 9),
                                               'degrees_north'))
    aux0.standard_name = 'latitude'
    
    # Create a latitude auxiliary coordinate
    aux1 = cf.AuxiliaryCoordinate(properties=dict(standard_name='longitude'),
                                  data=cf.Data(numpy.arange(1, 91).reshape(9, 10),
                                               'degrees_east'))
    
    # Create a rotated_latitude_longitude grid mapping transform
    trans0 = cf.Transform(grid_mapping_name='rotated_latitude_longitude',
                          grid_north_pole_latitude=38.0,
                          grid_north_pole_longitude=190.0)
    
    # --------------------------------------------------------------------
    # 2. Create the field's domain from the previously created items
    # --------------------------------------------------------------------
    domain = cf.Domain(dim=[dim0, dim1, dim2],
                       aux=[aux0, aux1],
                       trans=trans0,
                       assign_axes={'aux1': ['dim1', 'dim0']})
    
    #---------------------------------------------------------------------
    # 3. Create the field
    #---------------------------------------------------------------------
    # Create CF properties
    properties = {'standard_name': standardname,
                  'long_name'    : longname,
                  'cell_methods' : cf.CellMethods('latitude: point')}
    
    # Create the field's data array
    data = cf.Data(numpy.arange(90.).reshape(9, 10), 'm s-1')
    
    # Finally, create the field
    f = cf.Field(properties=properties,
                 domain=domain,
                 data=data,
                 axes=domain.axes(['grid_long', 'grid_lat'], ordered=True))
                 
    return f
    
class TestCFutilities(unittest.TestCase):
    ''' Test methods for the CF utilities '''
    def setUp(self):
        ''' make some dummy CF data'''
        self.sname,self.lname='eastward_wind','East Wind'
        self.f=makeDummy(self.sname,self.lname)
        
    def test_cfkeyval(self):
        ''' test the cfkeyval method '''
        expecting={'long_name':'<b>long_name</b>: %s'%self.lname,
                   'standard_name':'<b>standard_name</b>: %s'%self.sname,
                   'cell_methods':'?'}
        # currently cf python doesn't return cell_methods in properties
        # even though I think it should. This test will break when it does,
        # coz expected will need to be filled out correctly and I haven't
        # gotten around to that.
        for p in self.f.properties:
            self.assertEqual(cfkeyvalue(self.f,p),expecting[p])
            print p,cfkeyvalue(self.f,p)
    def test_cfdimprops(self):
        ''' test the cfdimprops method doesn't crash '''
        p=cfdimprops(self.f)
    def test_arrayCombo(self):
        ''' Actually creates and runs a widget, so we turn this off
        after testing it properly '''
        win=gtk.Window()
        vector=numpy.arange(100.)
        x=arrayCombo(vector)
        x.set_value(10.)
        self.assertEqual(x.get_value(),10.)
        #win.add(x.box)
        #win.show_all()
        #gtk.main()
        
    
if __name__=="__main__":
    unittest.main()
    
    
    
    
