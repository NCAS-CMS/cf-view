#!/usr/bin/env python

import pygtk
import gtk
import cf
import guiWidgets as gw
import sys

__version__='0.0.1'

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
        
        # notebook
        nb=gtk.Notebook()
        nb.show_tabs=True
        vbox.pack_start(nb,padding=cfgPadding)
        self.nb=nb
        for a,p,m in [ ('Select',xconvLike,self.selector),
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
        
    def help_about(self,b):
        ''' Provide an about dialog '''
        m=gtk.AboutDialog()
        m.set_program_name('cfgui')
        m.set_copyright ( '(c) National Centre for Atmosheric Science')
        m.set_version(__version__)
        m.set_comments('''
This is a pre-release version of the NCAS cfgui
            ''')
        m.run()
        m.destroy()
        
    def delete(self,b=None):
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
        
        The action box is passed in ... 
        '''
    def __init__(self,actionbox):
        ''' Initialise with an action box to put in the top corner '''
        super(xconvLike,self).__init__()
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
        actionbox=gw.guiFrame('Actions',ysize=80)
        vbox=gtk.VBox()
        self.buttonPanel=gtk.HBox()
        actionbox.add(vbox)
        vbox.pack_start(self.buttonPanel,expand=False)
        chooser=gtk.Button('Choose Plot')
        chooser.connect('clicked',self._choosePlot)
        self.buttonPanel.pack_start(chooser,padding=5,expand=False)
        return actionbox
        
    def _choosePlot(self,widget):
        ''' Given the dimensionality of the plot, offer a set of plot types '''
        # At this point we need a two dimensional field, if it's not 
        # two dimensional, raise an error
        grid=self.gridSelector.get_selected()
        # for now let's operatate on the first field. 
        # FIXME (handle multiple fields)
        # FIXME (is there a more elegant way of doing this than looping?)
        sfield=self.fields[0]
        print grid
        print sfield.shape
        for d in grid:
            # doesn't work ...
            sfield=sfield.subspace(d=cf.wi(grid[d][0],grid[d][1]))
        print sfield.shape
        
    def set_data(self,data):
        ''' Set with an open cf dataset object '''
        self.cf_dataset=data
        self.fieldSelector.set_data(data)
        
    def selection(self,data):
        ''' Provided to fieldSelector as a callback, so that when
        fields are selected, the metadata and grid selectors are
        updated. '''
        fields=[self.cf_dataset[i] for i in data]
        self.fieldMetadata.set_data(fields)
        self.gridMetadata.set_data(fields)
        self.gridSelector.set_data(fields[0]) 
        self.fields=fields
            
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
