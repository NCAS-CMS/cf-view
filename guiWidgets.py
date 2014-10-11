
import pygtk
import gtk

class guiFrame(gtk.Frame):
    ''' Mixin to simplify framesetup with size and label '''
    xsize,ysize=800,600
    def __init__(self,title=None,xsize=None,ysize=None):
        super(guiFrame,self).__init__()
        
        if title is not None: self.set_label(title)
        
        if xsize is not None: self.xsize=xsize
        if ysize is not None: self.ysize=ysize
        self.set_size_request(self.xsize,self.ysize)
        
class fileMetadata(guiFrame):
    def __init__(self,title='File Metadata',xsize=None,ysize=None):
        ''' Initialise '''
        super(fileMetadata,self).__init__(title=title,xsize=xsize,ysize=ysize)
    def set_data(self,data):
        ''' Set file metadata information, aka common properties '''
        pass
    
        
class fieldSelector(guiFrame):
    ''' Provides a widget for data discovery, depends on the CF api
    to load data through the set_data method. '''
    
    def __init__(self, selection_callback,xsize=None,ysize=None):
        ''' Initialise as an empty vessel which gets populated when
        via the set_data method. Needs a selection callback for when
        the selection is changed. '''
        
        super(fieldSelector,self).__init__(xsize=xsize,ysize=ysize)   
        
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
        for k,v in (('xpad',25),('size-points',8)):
            self.fieldRenderer.set_property(k,v)
            
        self.columns_are_setup=False
        
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
        print xsize
        
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
        # FIXME, use CF grid information, not this ...
        (nx,ny,nz,nt) = (len(field.item('dim3').array), 
                        len(field.item('dim2').array), 
                        len(field.item('dim1').array) , 
                        len(field.item('dim0').array))
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
        
    def changed(self,data):
        ''' Called when the liststore changes '''
        print data
        self.selection_callback()
    
    def show(self):
        ''' Show widgets '''
        super(fieldSelector,self).show_all()
        
class guiInspect(guiFrame): 
    ''' Provides a file inspection widget '''
    def __init__(self,selector):
        super(guiInspect,self).__init__()
    def reset(self):
        ''' Handle changing the data file '''
        pass

class guiPlot(guiFrame):
    ''' Provides a file plot widget '''
    def __init__(self,selector):
        super(guiPlot,self).__init__()
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
    xsplit=[0.65,0.35]
    ysplit=[0.7,0.3]
    def __init__(self,xsize=None,ysize=None):
        ''' Initialise with optional quarter frame size '''
        super(QuarterFrame,self).__init__(xsize=xsize,ysize=ysize)
        vbox=gtk.VBox()
        hboxTop=gtk.HBox()
        hboxBottom=gtk.HBox()
        vbox.pack_start(hboxTop)
        vbox.pack_start(hboxBottom)
        self.add(vbox)
        ls,rs=int(self.xsplit[0]*self.xsize),int(self.xsplit[1]*self.xsize)
        ts,bs=int(self.ysplit[0]*self.ysize),int(self.ysplit[1]*self.ysize)
        self.topLeft=guiFrame(xsize=ls,ysize=ts)
        self.topRight=guiFrame(xsize=rs,ysize=ts)
        self.bottomLeft=guiFrame(xsize=ls,ysize=bs)
        self.bottomRight=guiFrame(xsize=rs,ysize=bs)
        hboxTop.pack_start(self.topLeft)
        hboxTop.pack_start(self.topRight)
        hboxBottom.pack_start(self.bottomLeft)
        hboxBottom.pack_start(self.bottomRight)
    def show(self):
        ''' Show internal widgets '''
        self.show_all()
