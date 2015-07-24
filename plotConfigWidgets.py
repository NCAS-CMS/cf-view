import pygtk
import gtk
import guiWidgets as gw

class plotChoices(gw.guiFrame):
    ''' Provides a small set of cf-plot aware plot choices '''
    def __init__(self,callback,xsize=None,ysize=None):
        ''' Constructor places buttons etc in frame, users interact,
        and then press one of the two key buttons: simple plot, or normal plot.
        They can also do advanced configuration via the advanced config button.
        Caller needs to provide a callback for when one of the two plot
        buttons is called (and deal with either {} for a simple plot, or 
        a dictionary of dictionaries with cf plots etup information for the
        normal plot. 
        Optional arguements are size hints. '''
        super(plotChoices,self).__init__(
            'Configure and Generate Plots',xsize=xsize,ysize=ysize)
        self.callback=callback
        self.vbox=gtk.VBox()
        self.row1=gtk.HBox()
        self.row2=gtk.HBox()
        self.row3=gtk.HBox()
        self.row4=gtk.HBox()
        self.add(self.vbox)
        self._row1(callback)
        self._row2()
        self._row3()
        self._row4(callback)
    
    def _row1(self,callback):
        ''' Sets up the basic action buttons '''
        #sp=gw.smallButton('Simple Plot')
        #np=gw.smallButton('Plot (Configured)')
        np=gw.smallButton('Plot')
        hb=gw.smallButton('Help')
        s1=gtk.VSeparator()
        s2=gtk.VSeparator()
        #for b in [sp,s1,np,s2,hb]:
        for b in [np,s2,hb]:
            self.row1.pack_start(b,padding=2)
        self.vbox.pack_start(self.row1,expand=False,padding=2)
        self.vbox.pack_start(gtk.HSeparator(),expand=False,padding=2)
        #sp.connect('clicked',callback,{})
        np.connect('clicked',self._getConfig,None)
        hb.connect('clicked',self._help,None)
    
    def _row2(self):
        ''' Lays out the buttons for standard plots '''
        self.projComboShown=1
        #ptypes=['X-Y','X-Z','Y-Z','X-T','Y-T']
        ptypes=['contour', 'vector', 'contour+vector']
        nup=['1','2x1', '1x2', '2x2' , '3x2', '2x3','3x3']
        self.proj=['cyl','moll','npolar','spolar']
        #self.typCombo=gw.myCombo(ptypes,label='type',initial='X-Y',callback=self._showProj)
        self.typCombo=gw.myCombo(ptypes,label='type',initial='contour',callback=self._showProj)
        self.nupCombo=gw.myCombo(nup,label='n-up',initial='1')
        self.projCombo=gw.myCombo(self.proj,label='projection',initial='cyl')
        self.row2.pack_start(self.nupCombo,expand=True,padding=2)
        self.row2.pack_start(self.typCombo,expand=True,padding=2)
        self.row2.pack_start(self.projCombo,expand=True,padding=2)
        self.vbox.pack_start(self.row2,expand=False,padding=2)
    def _row3(self):
        ''' Lays out the buttons for configuring contours '''
        contours=['lines','filled','block']
        labels=['Off','On','On--']
        self.cbar=['On','Off','On-X','On-Y']
        self.cbarChoiceShown=1
        self.conCombo=gw.myCombo(contours,label='contours',initial='filled',
                callback=self._showCbar)
        self.linCombo=gw.myCombo(labels,label='labels',initial='On')
        self.cbarCombo=gw.myCombo(self.cbar,label='bar',initial='On')
        #self.cbarCombo=gw.myCombo(self.cbar,label='bar',initial='Off')
        for w in [self.conCombo,self.linCombo,self.cbarCombo]:
            self.row3.pack_start(w,padding=2)
        self.vbox.pack_start(self.row3,expand=False,padding=2)
        
        extend=['min','max','neither','both']
        #minc,maxc,nlevs,extend
        
    def _row4(self,callback):
        ''' Lays out axes information'''
        logv=['Normal','log-x','log-y','log-xy']
        self.axeCombo=gw.myCombo(logv,label='axes',initial='Normal')
        ac=gw.smallButton('Advanced Config')
        ac.connect('clicked',self._advancedConfig,None)
        self.row4.pack_start(self.axeCombo,padding=2,expand=False)
        self.row4.pack_start(ac,padding=2,expand=True)
        self.vbox.pack_start(self.row4,expand=False,padding=2)
        
    def _showCbar(self,w,value):
        ''' Callback used to turn off the colour bar choice as appropriate '''
        if value=='lines' and self.cbarChoiceShown:
            self.cbarCombo.destroy()
            self.cbarChoiceShown=0
        elif not self.cbarChoiceShown:
            self.cbarCombo=myCombo(self.cbar,initial='Off')
            self.row3.pack_start(self.cbarCombo,padding=2)
            self.cbarChoiceShown=1
            self.cbarCombo.show()
        
    def _showProj(self,w,value):
        ''' Callback used for the typcombo to allow projections for X-Y '''
        if value=='contour' and not self.projComboShown:
            self.projCombo=gw.myCombo(self.proj,initial='cyl')
            self.row2.pack_start(self.projCombo,expand=False,padding=2)
            self.projCombo.show()
        if value!='contour' and self.projComboShown:
            self.projCombo.destroy()
            self.projComboShown=0
            
    def _help(self,w,data):
        ''' Show configuration help '''
        dialog=gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_INFO,gtk.BUTTONS_OK,
                    'Making vector plots - select u field and then click plot  \
                                         - select v field and then click plot\
                     Making contour and vector plots - select contour field and click plot\
                                         - select u field and then click plot\
                                         - select v field and then click plot\
')



        dialog.run()
        dialog.destroy()
   
    def _advancedConfig(self,w,data):
        ''' Generate advanced plot configuration information via a dialog popup '''
        dialog=gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_INFO,gtk.BUTTONS_OK,
                    'Sorry advanced config not yet implemented')
        dialog.run()
        dialog.destroy()
        
    def _getConfig(self,w,d):
        ''' Return all the configuration information in dictionaries
        suitable for use as arguments for cf plot via the callback.
        This is the intersection between cf-gui and cf-plot 
        (i.e. it implements most of the cf-plot API (more of it
        is implemented via the advanced config.) '''
        config={
            #'nup':int(self.nupCombo.get_value()),
            'nup':self.nupCombo.get_value(),
            'gopen':{
                'rows':
                    {'1':None, '2x1':1, '1x2':2, '2x2':2, '3x2':2, '2x3':3, '3x3':3}[self.nupCombo.get_value()],
                'columns':
                    {'1':None, '2x1':2, '1x2':1, '2x2':2, '3x2':3, '2x3':2, '3x3':3}[self.nupCombo.get_value()],
                    },
            'mapset':{
                'proj':{'cyl':'cyl','moll':'moll','npolar':'npstere',
                            'spolar':'spstere'}[self.projCombo.get_value()]
                    },
            'con':{
                'ptype':
                    #{'X-Y':1,'X-Z':3,'Y-Z':2,'X-T':5,'Y-T':4}[self.typCombo.get_value()],
                    {'contour':1,'vector':2, 'contour+vector':3}[self.typCombo.get_value()],
                'line_labels':
                    {'On':True,'On--':True,'Off':False}[self.linCombo.get_value()],
                'negative_linestyle':
                    {'On':None,'Off':None,'On--':1}[self.linCombo.get_value()],
                'colorbar':
                    {'On':1,'Off':None,'On-X':1,'On-Y':1}[self.cbarCombo.get_value()],
                'colorbar_orientation':
                    #{'Off':None,'On':None,'On-X':'horizontal','On-Y':'vertical'}
                    {'On':'horizontal','Off':None,'On-X':'horizontal','On-Y':'vertical'}
                        [self.cbarCombo.get_value()],
                'blockfill':
                    {'lines':None,'filled':None,'block':1}[self.conCombo.get_value()],
                'lines':
                    {'lines':True,'filled':True,'block':None}[self.conCombo.get_value()],
                'fill':
                    {'lines':None,'filled':True,'block':None}[self.conCombo.get_value()],
                'xlog':
                    {'Normal':None,'log-x':True,'log-y':None,'log-xy':True}
                        [self.axeCombo.get_value()],
                'ylog':
                    {'Normal':None,'log-x':None,'log-y':True,'log-xy':True}
                        [self.axeCombo.get_value()],
                    }
                }
        self.callback('Configured',config)
   
    def show(self):
        super(plotChoices,self).show_all()
        
def checkConsistency(field,plotOptions):
    ''' Check consistency between the data chosen and the plot options and
    generate error messages if appropriate. Return '' if ok! '''
    fixit='\nPlease use the grid selector to choose a 1d or 2d field'
    message=''
    #if plotOptions=={}:
    #    # simple plot option, we expect a 2d field
    #    if (len(xyshape(field)) < 1 or len(xyshape(field)) > 2):
    #        message= 'cfview can only plot 1D or 2D fields'+fixit
    #        return message
    #    else: message=''
    #else:
        # The key thing we need to check is for consistency between
        # plot options and the shape, so we can work out what to do with
        # for example, and XY plot which is 6-up.
    #    multi=plotOptions['nup']<>'1'
    #    message=plotPossibleWithField(field,plotOptions['con']['ptype'],multi)
    #    if message<>'': 
    #        if not multi: message+=fixit
    return message
        
def axes_sizes(f):
    ''' Return the sizes of the X,Y,Z,T arrays in field,f , if that's possible. 
    Much of this is temporary code, needed because 0.9.8.1 of cf-python
    can't do this trivially, 0.9.8.3 can ...'''
    sizes,results={},{}
    axes=f.domain.axes()
    # After this next line, we have an array keyed by 'dim'
    for axis in axes: sizes[axis]=f.domain.axes_sizes(key=True)[axis]

    # We need to know those for the short names. 
    for axis in ['X','Y','Z','T']:
        try:
            results[axis]=sizes[f.domain.axis(axis)]
        except ValueError:
            results[axis]=None
    return results
    
def xyshape(f):
    ''' Return the shape of a field as a string, e.g. XY, or XYT '''
    sizes=axes_sizes(f)
    shapeString=''
    for s in sizes:
        if sizes[s]>1: shapeString+=s
    return shapeString
    
#def ptype2string(ptype):
#    ''' Take a plot type understood by cf-plot, and convert to an XYZT string '''
#    return {1:'XY',3:'XZ',2:'YZ',5:'XT',4:'YT'}[ptype]
    
#def plotPossibleWithField(f,ptype,multi=False):
#    ''' For a given field, is a plot of ptype possible?
#            ptype is the integer understood by cf-plot.
#        One extra dimension can be allowed to be non-singular,
#        but only if multi is true.
#        Returns '' for success, otherwise a string with an error message!
#    '''
#    ss=ptype2string(ptype)
#    fs_shape=xyshape(f)
#    nd=len(fs_shape)
#    message=''
#    if nd>3:
#        message='Dimensionality (%s) too great'%nd
#    elif nd==3 and not multi:
#        message='Dimensionality (3) not allowed unless multiple plots'
#    elif nd<2:
#        message='Dimensionality (%s) too small'%nd
#    elif nd==2 and multi:
#        message='Dimensionality (2) too small for multiple plots'
#    elif nd==3 and multi:
#        for s in ss:
#            if s not in fs_shape:
#                message='Missing axis %s'%s
#    else:
#        raise ValueError('This should not occur')
#    #print multi,nd,ss,ptype,fs_shape,f.shape,message
#    #return message
#    return ''

def getSlicesAndTitles(field,plotOptions):
    ''' Get appropriate title information for each plot, and for multiple
    plots, extract the slicing information necessary to extract each
    plot from the field. '''
    grid=gw.cfGrid(field)
    # start with common title
    title=''
    simple=False
    if plotOptions=={}:
        simple=True
    else:
        if plotOptions['nup']==1 or len(xyshape(field))==2: simple=True
    simple=True
    if simple:
        # it's easy, just find the singleton dimension values
        for dim in grid.axes:
            if len(grid.axes[dim].array)==1:
                title+=' %s:%s '%(grid.names[dim],grid.axes[dim].array[0])
        # just return the title, no subspace argument selector necessary.
        r=[(title,None),]
    #else:
    #    # find the dimension we're stepping through.
    #    myplot={1:'XY',3:'XZ',2:'YZ',5:'XT',4:'YT'}[plotOptions['con']['ptype']]
    #    shape=xyshape(field)                                 # eg XYT
    #    stepper=shape.strip(myplot)                          # eg T
    #    dim=field.domain.axis(stepper)                       # eg 'dim2'
    #    r=[]
    #    # how many, minimum of length of field or nup
    #    howmany=min(plotOptions['nup'],len(grid.axes[dim].array))
    #    #howmany=len(grid.axes[dim].array)
    #    for i in range(howmany):
    #        thisTitle=title
    #        key,value=grid.names[dim],grid.axes[dim].array[i]
    #        thisTitle+=' %s:%s '%(key,value)
    #        # need to use dim in the next command to avoid possible name ambiguity
    #        # in non-cf compliant files.
    #        r.append((thisTitle,{dim:value}))
    #    print shape,stepper,dim,key,value
    return r
            
            
        
    
    
