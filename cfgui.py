#!/usr/bin/env python

import pygtk
import gtk
import cf
import guiWidgets as gw
import plotConfigWidgets as pcw
import sys
import cfplot as cfp

__version__='0.1.3'

cfgPadding=5

class cfgui:
    ''' Provides the main frame for the cfgui '''
    def __init__(self, filename):
        ''' Create main window as a notebook with three panes:
                Discover
                Inspect
                Plot
            Provide a status window underneath and a toolbar above.
        '''
        
        window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect('delete_event',self.delete)
        window.set_border_width(cfgPadding)
        
        # box for all main window elements
        vbox=gtk.VBox()
        window.add(vbox)
        
        # get menubar
        menubar=self.get_mainMenu(window)
        vbox.pack_start(menubar,expand=False)
        
        # script record of what is going on 
        self.script=script(debug=True)
        
        # notebook
        nb=gtk.Notebook()
        nb.show_tabs=True
        vbox.pack_start(nb,padding=cfgPadding)
        self.nb=nb
        for a,p,m in [ ('Select',xconvLike,self.script),
                    ('Inspect',gw.guiInspect,self.selector),
                    ('Gallery',gw.guiGallery,self.selector),
                   ]:
            label=gtk.Label(a)
            w=p(m)
            self.nb.append_page(w,label)
            setattr(self,a,w)
            w.show_all()
        
        # status window
        statusbar=gtk.Statusbar()
        statusbar.set_has_resize_grip(False)
        vbox.pack_start(statusbar,padding=cfgPadding,expand=False)
        
        self.w=window
        
        self.default_title=' CF GUI %s'%__version__
        self.set_title(self.default_title)
        
        window.show_all()
        
        if filename is not None:
            self.reset_with(filename)
        
    def selector(self):
        ''' Callback to mediate the various panes. May need to be
        a class with methods ... '''
        #FIXME
        pass
        
    def get_mainMenu(self,w):
        
        ''' Build a menuBar toolbar using the gtk uimanager '''
        
        ui = '''<ui>
            <menubar name="MenuBar">
                <menu action="File">
                    <menuitem action="Load"/>
                    <separator/>
                    <menuitem action="Quit"/>
                </menu>
                <menu action="Help">
                    <menuitem action="About"/>
                </menu>
            </menubar>
            </ui>
            '''
        uimanager = gtk.UIManager()
        
        accelgroup = uimanager.get_accel_group()
        w.add_accel_group(accelgroup)
        
        actiongroup=gtk.ActionGroup('cfgui')
        
        actiongroup.add_actions ([
                ('File',None,'_File'),
                ('Load',gtk.STOCK_OPEN,'Load File',None,
                 'Load File',self.file_load),
                 ('Quit',gtk.STOCK_QUIT,'Quit',None,
                 'Quit',self.delete),
                ('Help',None,'_Help'),
                ('About',gtk.STOCK_HELP,'About', None,
                'About cfgui',self.help_about),
                ])
                 
        uimanager.insert_action_group(actiongroup, 0)
        uimanager.add_ui_from_string(ui)
        
        widget=uimanager.get_widget('/MenuBar')
        
        # make sure the help menu is on the right
        helpmenu = uimanager.get_widget('/MenuBar/Help')
        helpmenu.set_right_justified(True)         
        
        return widget
        
    def file_load(self,b):
        ''' Open a file for cfgui. '''
        chooser=gtk.FileChooserDialog(title='Open data file',
                    action=gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons=(   gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN,gtk.RESPONSE_OK),
                    )
        response=chooser.run()
        if response==gtk.RESPONSE_OK:
            newfile=chooser.get_filename()
            self.reset_with(newfile)
        chooser.destroy()
        
    def reset_with(self,filename):
        ''' Open dataset filename '''
        data=cf.read(filename)
        self.Select.set_data(data)
        self.Inspect.reset()
        self.Gallery.reset()
        self.script.open(filename)
        
    def help_about(self,b):
        ''' Provide an about dialog '''
        m=gtk.AboutDialog()
        m.set_program_name('cfgui')
        m.set_copyright ( '(c) National Centre for Atmospheric Science')
        m.set_version(__version__)
        m.set_comments('''
This is a pre-release version of the NCAS cfgui

Credits to:
    David Hassell - for cf-python
    Andy Heaps - for cf-plot
    Mudit Gupta - for the prototype pygtk interface to cf-plot
    Bryan Lawrence - for the initial version of cfgui
            
            ''')
        m.run()
        m.destroy()
        
    def delete(self,w=None,b=None):
        ''' Delete menu '''
        gtk.main_quit()
        return False
        
    def set_title(self,title):
        ''' Set window title '''
        self.w.set_title(title)

class xconvLike(gw.QuarterFrame):
    ''' Set up an xconv like set of panels with 
            field selection on the top left
            field metadata on the bottom left
            grid metadata on the bottom right
            and a combination of grid selection and actions on the top right
        which of course isn't like xconv, but is more cf-like ...
        
        '''
    def __init__(self,script):
        ''' Initialise with the script recorder '''
        super(xconvLike,self).__init__()
        self.script=script
        self.fieldSelector=gw.fieldSelector(self.selection)
        self.fieldMetadata=gw.fieldMetadata()
        self.gridMetadata=gw.gridMetadata()
        self.gridSelector=gw.gridSelector(ysize=200)
        self.topLeft.add(self.fieldSelector)
        self.bottomLeft.add(self.fieldMetadata)
        self.bottomRight.add(self.gridMetadata)
        self._topRight()
        
    def _topRight(self):
        ''' Combination frame for the top right '''
        topRv=gtk.VBox()
        topRv.pack_start(self._actionBox(),padding=2)
        topRv.pack_start(self.gridSelector,expand=True,fill=True)
        self.topRight.add(topRv)
        
    def _actionBox(self):
        ''' Provides the buttons and callbacks to the actual actions which 
        the routine supports. '''
        actionBox=pcw.plotChoices(callback=self._plot,ysize=90)
        actionBox.show()
        return actionBox
        
    def _plot(self,w,plotOptions):
        ''' Executes a plot given the information returned from the various
        selectors and configuration widgets. In practice we have
            - the grid selector telling us about the data slicing,
            - the field selector telling us about what data to plot, and
            - the plot choices widget giving us the cf plot arguments.
        All we have to do here is configure the plot (possibly including
        dealing with multiple plots on one page). 
        '''
        print 'Plot received',plotOptions
        #self.script.add('plotOptions are'+str(plotOptions))

        


        grid=self.gridSelector.get_selected()
        # check we have some data
        if grid is None:
            dialog=gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR,gtk.BUTTONS_CLOSE,
                    'Please select some data before trying to plot!')
            dialog.run()
            dialog.destroy()
            return
       
        # for now let's operatate on the first field.
        # FIXME What to do if we have more than one field? 
        sfield=self.fields[0]
        self.script.add('sfield=fields[0]')
        # first let's do the subspace selection (if any):
        kwargs={}
        self.script.add('kwargs={}',hash=True)
        for d in grid:
            kwargs[d]=cf.wi(grid[d][0],grid[d][1])
            self.script.add("kwargs['%s']=cf.wi(%s,%s)"%(d,grid[d][0],grid[d][1]))
        sfield=sfield.subspace(**kwargs)
        self.script.add('sfield=sfield.subspace(**kwargs)')
        # now, do we have to apply any operators?
        opstring=''
        for d in grid:
            if grid[d][2]<>None:
                #sfield=cf.collapse(sfield,grid[d][2],axes=d)
                sfield=sfield.collapse(grid[d][2],axes=d)
                opstring+='%s:%s '%(grid[d][2],sfield.domain.axis_name(d))
                self.script.add(
                    "sfield=cf.collapse(sfield,'%s',axes='%s')"%(grid[d][2],d))
        
        # now we know the shape we can check that the plotting options
        # and data shape are consistent.
        message=pcw.checkConsistency(sfield,plotOptions)
        if message <>'':
            # We currently don't know how to plot it
            dialog=gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR,gtk.BUTTONS_CLOSE,message)
            dialog.run()
            dialog.destroy()
            return
        
        # ok we really can plot this thing!
        
        # Sort out the basic title
        if plotOptions=={}:
            title=sfield.file
        else:
            if 'title' in plotOptions['con']:
                title=plotOptions['con']['title']
            else:
                title=sfield.file
        title+='\n'

        
        # Add details of any operators, if any
        title+=opstring
        
        # get more titles, and slicing information for multiple plots
        tsList=pcw.getSlicesAndTitles(sfield,plotOptions)

        #reset cfplot before any plot to clear previous settings
        cfp.reset()

        if plotOptions=={}:
            title+=tsList[0][0]
            cfp.con(sfield,title=title)
            self.script.add("cfp.con(sfield,title='%s')"%title,hash=True)
        else:
            # need to remove the ptype from the contour options, cf-plot
            # can't cope with cf data, and ptype, unless we expressly give
            # it x and y ... and we're not.
            plotOptions['con']['ptype']=None
            #
            self.script.add('plotOptions=%s'%plotOptions,hash=True)
            if plotOptions['nup']<>1:
                cfp.gopen(**plotOptions['gopen'])
                self.script.add("cfp.gopen(**plotOptions['gopen'])")
            if plotOptions['mapset']['proj']<>'cyl':               
                #cfp.mapset(**plotOptions['mapset']['proj'])
                cfp.mapset(proj=plotOptions['mapset']['proj'])
                self.script.add("cfp.mapset(proj="+plotOptions['mapset']['proj']+")")
            if 'title' not in plotOptions['con']:
                plotOptions['con']['title']=sfield.file
                self.script.add("plotOptions['con']['title']=sfield.file")
            if plotOptions['nup']==1:
                title+=tsList[0][0]
                plotOptions['con']['title']=title
                self.script.add("plotOptions['con']['title']=%s"%title)
                self.script.add("cfp.con(sfield,**plotOptions['con'])")
                cfp.con(sfield,**plotOptions['con'])
            else:
                i=1
                for (title,slicer) in tsList:
                    self.script.add("cfp.gpos(%s)"%i)
                    self.script.add("plotOptions['con']['title']='%s'"%title)
                    self.script.add('slicer=%s'%slicer)
                    self.script.add("cfp.con(sfield.subspace(**slicer),**plotOptions['con'])")
                    cfp.gpos(i)
                    plotOptions['con']['title']=title
                    cfp.con(sfield.subspace(**slicer),**plotOptions['con'])
                    i+=1
                self.script.add("cfp.gclose()")
                cfp.gclose()
        self.script.close('bnl.py')

    def set_data(self,data):
        ''' Set with an open cf dataset object '''
        self.cf_dataset=data
        self.fieldSelector.set_data(data)
        
    def selection(self,data):
        ''' Provided to fieldSelector as a callback, so that when
        fields are selected, the metadata and grid selectors are
        updated. '''
        fields=[self.cf_dataset[i] for i in data]
        self.script.add('fields=[dataset[i] for i in %s]'%data)
        self.fieldMetadata.set_data(fields)
        self.gridMetadata.set_data(fields)
        self.gridSelector.set_data(fields[0]) 
        self.fields=fields
        
class script:
    ''' Provides a scriptable copy of what the gui is doing '''
    def __init__(self,debug=True):
        ''' Construct the file header. If debug, write actions 
        as we go along. '''
        self.content='''
import cf
import cfplot as cfp
#
# script generated by cfgui version %s
#
                    '''%__version__
        if debug: 
            self.debug=open('debug.py','w')
            self.debug.write(self.content)
        else: self.debug=False
    def open(self,filename):
        ''' Open a specific file '''
        content="#\ndataset=cf.read('%s')\n#\n"%filename
        self.content+=content
        if self.debug:self.debug.write(content)
    def add(self,command,hash=False):
        ''' Add a command to the script, preceded by a hash if hash true '''
        if hash: self.content+='\n#\n'
        # we have to parse the command for things that need escaping
        command=command.replace('\n','\\n')
        self.content+='%s\n'%command
        if self.debug:self.debug.write('%s\n'%command)
    def close(self,output_filename):
        ''' Save to output_filename '''
        f=file(output_filename,'w')
        f.write(self.content)
        print 'Script written to  %s'%output_filename
        f.close()
            
def main(filename):
    ''' main loop for the cfgui '''
    c=cfgui(filename)
    gtk.main()
    return 0
        
if __name__=="__main__":
    args=sys.argv
    if len(args)>2:
        print 'Usage: cfgui <filename>   (filename is optional)'
    elif len(args)==2:
        main(args[1])
    else: main(None)
