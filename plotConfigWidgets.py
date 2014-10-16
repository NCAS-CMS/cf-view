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
        sp=gw.smallButton('Simple Plot')
        np=gw.smallButton('Plot (Configured)')
        hb=gw.smallButton('Help')
        s1=gtk.VSeparator()
        s2=gtk.VSeparator()
        for b in [sp,s1,np,s2,hb]:
            self.row1.pack_start(b,padding=2)
        self.vbox.pack_start(self.row1,expand=False,padding=2)
        self.vbox.pack_start(gtk.HSeparator(),expand=False,padding=2)
        sp.connect('clicked',callback,{})
        np.connect('clicked',self._getConfig,None)
        hb.connect('clicked',self._help,None)
    
    def _row2(self):
        ''' Lays out the buttons for standard plots '''
        self.projComboShown=1
        ptypes=['X-Y','X-Z','Y-Z','X-T','Y-T']
        nup=['1','2','4','6','9']
        self.proj=['cyl','moll','npolar','spolar']
        self.typCombo=gw.myCombo(ptypes,label='type',initial='X-Y',callback=self._showProj)
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
        self.cbar=['Off','On','On-X','On-Y']
        self.cbarChoiceShown=1
        self.conCombo=gw.myCombo(contours,label='contours',initial='filled',
                callback=self._showCbar)
        self.linCombo=gw.myCombo(labels,label='labels',initial='On')
        self.cbarCombo=gw.myCombo(self.cbar,label='bar',initial='Off')
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
        if value=='X-Y' and not self.projComboShown:
            self.projCombo=gw.myCombo(self.proj,initial='cyl')
            self.row2.pack_start(self.projCombo,expand=False,padding=2)
            self.projCombo.show()
        if value!='X-Y' and self.projComboShown:
            self.projCombo.destroy()
            self.projComboShown=0
            
    def _help(self,w,data):
        ''' Show configuration help '''
        dialog=gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_INFO,gtk.BUTTONS_OK,
                    'Sorry help not yet implemented')
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
            'nup':self.nupCombo.get_value(),
            'mapset':{
                'proj':{'cyl':'cyl','moll':'moll','npolar':'npsphere',
                            'spolar':'spsphere'}[self.projCombo.get_value()]
                    },
            'con':{
                'ptype':
                    {'X-Y':1,'X-Z':3,'Y-Z':2,'X-T':5,'Y-T':4}[self.typCombo.get_value()],
                'line_labels':
                    {'On':True,'On--':True,'Off':False}[self.linCombo.get_value()],
                'negative_linestyle':
                    {'On':None,'Off':None,'On--':1}[self.linCombo.get_value()],
                'colorbar':
                    {'Off':None,'On':1,'On-X':1,'On-Y':1}[self.cbarCombo.get_value()],
                'colorbar_orientation':
                    {'Off':None,'On':None,'On-X':'horizontal','On-Y':'vertical'}
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
    generate error messages if appropriate '''
    if plotOptions=={}:
        # simple plot option, we expect a 2d field
        dimensionality=0
        for i in field.shape:
            if i>1: dimensionality+=1
        if dimensionality<>2:
            message= 'Currently we only know how to plot 2d fields.\n'+\
                    'Please use the grid selector to choose a 2d field.'
            return message
    else:
        print 'Consistency not yet implemented'
        return None
    
     #print grid.keys()
        #axis_sizes={}
        #print sfield.axes_sizes()
        #for a in ['X','Y','Z','T']:
        #    axis_sizes[a]=sfield.axes_sizes()[sfield.axis.name(a)]
        #print axis_sizes
        # At this point we need a two dimensional field, if it's not 
        # two dimensional, raise an error
