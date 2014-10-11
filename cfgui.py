#!/usr/bin/env python

import pygtk
import gtk
import cf
import guiWidgets as gw

__version__='0.0.1'

cfgPadding=5

class cfgui:
    ''' Provides the main frame for the cfgui '''
    def __init__(self):
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
        for a,p,m in [ ('discover',xconvLike,self.selector),
                    ('inspect',gw.guiInspect,self.selector),
                    ('plot',gw.guiPlot,self.selector),
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
        self.discover.set_data(data)
        self.inspect.reset()
        self.plot.reset()
        
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
    ''' Set up an xconv like set of panels with discovery in the top left,
    file metadata at the bottom, field metadata on the top right, and
    grid metadata on the bottom right ... which of course is not exactly
    like xconv. '''
    def __init__(self,selector=None):
        ''' Initialise with no arguments '''
        super(xconvLike,self).__init__()
        self.fieldSelector=gw.fieldSelector(self.selection)
        self.fileMetadata=gw.fileMetadata()
        self.topLeft.add(self.fieldSelector)
        self.bottomLeft.add(self.fileMetadata)
        
    def set_data(self,data):
        ''' Set with an open cf dataset object '''
        self.fieldSelector.set_data(data)
        self.fileMetadata.set_data(data)
    
    def selection(self,data):
        ''' A call to set properties '''
        print 'selection called',data

            
def main():
    ''' main loop for the cfgui '''
    c=cfgui()
    gtk.main()
    return 0
        
if __name__=="__main__":
    main()
