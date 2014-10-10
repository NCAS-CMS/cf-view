#!usr/bin/env python

#Interface using PyGtk, CFPython and CFPlot

import pygtk
import gtk
import cf, cfplot as cfp
import os

from cfdata import CFData
    
class Interface:
        
    #If this function returns false, the destroy function is called. 
    #ToDo: Edit function to create a pop-up window to ask if the user is sure they want to exit.
    def delete_event(self, widget, event, data=None):
        return False

    #This function quits the interface.
    def destroy(self, widget, data=None):
        gtk.main_quit()


    #This function is called when setting up the interface; it sets the properties of the main window.
    def setWindowProperties(self, data=None):
        
        #Set Window Design Properties       
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.resize(int(self.window.get_screen().get_width() * 0.9), int(self.window.get_screen().get_height()*0.8))
        self.window.move(int(self.window.get_screen().get_width()*0.05), int(self.window.get_screen().get_height()*0.1))
        self.window.set_border_width(10)
        self.window.set_title('CF View')

        #Connect signals and functions
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)


            

    #This function is used to initialise the variables that will be used by the rest of the program.
    def initialiseVariables(self):
        
        #openFile is the window that pops-out when choosing the data file. 
        #This needs to be initialised so that there aren't multiple windows to choose a file.
        self.openFile = None    


        #Sets the titles of the Field Selection tree view and also the alignment of the titles
        self.fieldSelectionTitlesAlignment = 0.5
        self.fieldSelectionTitles = ['Index', 'Field Name', 'X', 'Y', 'Z', 'T'] 

        #xyztListStores are the ListStores containing the data from each variable in the form of [value, index]
        self.xyztListStores = [gtk.ListStore(float, int), gtk.ListStore(float, int), gtk.ListStore(float, int), gtk.ListStore(float, int)]

        #Set the label names so they can be changed when the user selects each variable
        self.xyzLabelNames = ["Variable Name: ", "Minimum Value: ", "Common Interval: ", "Variable Units: ",  "Maximum Value: ", "No. of Values Selected: "]
        self.tLabelNames = ["Variable Name: ", "Variable Units: ", "Selected Value: ", "", "", ""]
        
        #Set size and font of the labels.
        self.labelSize = "<span font ='12'>"
        self.labelEnd = "</span>"
        
        #Set the title of the variables when displayed in the Tree View.
        self.variablesTitle = ['X', 'Y', 'Z', 'T']  

        #Set the current selected variable to 0 (X)
        self.currentXYZT = 0
        
        #mapMode determines whether the plot is from the northern hemisphere, southern hemisphere or the whole world. 
        #The default (0) is the whole world
        self.mapMode = 0
        
        #Plot type refers to whether the plot is a Hovmuller plot
        #The default (1) is not a Hovmuller plot
        self.plotType = 1
        
        #maps is the list of plots that the user has added to the viewing area.
        self.maps = []
        
        #new Maps is a list of plots to be added to the viewing area
        self.newMaps = []
        
        #The buttons start inactive.
        self.buttonsActive = False
        
        #Storing the height and width of the window
        self.windowHeight = self.window.get_screen().get_height()
        self.windowWidth = self.window.get_screen().get_width()
        
        #Sets the size of the map thumbnails (Proportion of the screen)
        self.mapThumbnailScalingX = 0.15
        self.mapThumbnailScalingY = 0.15

    #########################################################################################################################################
    #                                  Function                                 #
    #                                 fileChanged                               #   
    #                                                                   #
    #########################################################################################################################################
    
    #This function is called when a new file is selected.
    def fileChanged(self, fileName):
        #The functions from the CFData class to extract the data and update the field names are called
        self.ClimateData.readDataSet(fileName)
        self.ClimateData.getFieldNames()
        
        #The List Store for field selection is cleared and the new data is put into it
        self.fieldSelectionData.clear()
        for fieldData in self.ClimateData.fieldDataSet:
            self.fieldSelectionData.append(fieldData)
    

    #########################################################################################################################################
    #                                                                   #
    #                               Menu Region                             #   
    #                                                                   #
    #########################################################################################################################################

    #This function is called when the open button is clicked from the menu bar.
    #It creates a window to select which file to extract data from.
    def addOpenFile(self, widget, Data=None):
        #If the cancel button is clicked the widget is destroyed
        def cancelOpenFile(widget, self, Data=None):
            self.openFile.destroy()
            self.openFile = None
        
        #If the ok button is clicked the filename is checked to see if it is a .nc file. 
        #If it is it calls the function "fileChanged" and destroys the widget
        #If not an error message is outputted.
        def loadFile(widget, self, Data=None):
            if self.openFile.get_filename()[-3:] == '.nc':
                self.fileChanged(self.openFile.get_filename())
                cancelOpenFile(None, self)
            else:
                self.addErrorMessage("Error - File type must be netCDF")
        
        #If there is already an open file window, it is destroyed. 
        if self.openFile != None:
            self.openFile.destroy()
            
        #A new file selection window is created and the relevant signals connected to the corresponding functions.
        self.openFile = gtk.FileSelection('Open File')
        self.openFile.show()        
        self.openFile.cancel_button.connect("clicked", cancelOpenFile, self)
        self.openFile.ok_button.connect("clicked", loadFile, self)
    
    
    #This function is called when setting up the interface. It creates the menu bar at the top.
    #To add this menu bar into the interface self.menuBar must be added to a container in the main code.
    def addMenu(self, Data=None):


        #Create Sub-menus       
        self.fileMenu = gtk.Menu()
        self.optionsMenu = gtk.Menu()
        
        
        
        #Create Items in File Sub-menu
        self.openOption = gtk.MenuItem("Open")
        self.fileMenu.append(self.openOption)
        self.openOption.connect("activate", self.addOpenFile)
        self.openOption.show()
        
        
        self.quitOption = gtk.MenuItem("Quit")
        self.fileMenu.append(self.quitOption)
        self.quitOption.connect_object("activate", self.destroy, "file.quit")
        self.quitOption.show()
        
        
        
        
        #Create Items in Options Sub-menu
        self.XConvOption = gtk.MenuItem("XConv Defaults")
        self.optionsMenu.append(self.XConvOption)
        self.XConvOption.show()
        
        
        self.STASHOption = gtk.MenuItem("STASH Master File")
        self.optionsMenu.append(self.STASHOption)
        self.STASHOption.show()
        
        
        self.netCDFOption = gtk.MenuItem("netCDF Attributes")
        self.optionsMenu.append(self.netCDFOption)
        self.netCDFOption.show()
        
        
        self.globalnetCDFOption = gtk.MenuItem("Global netCDF Attributes")
        self.optionsMenu.append(self.globalnetCDFOption)
        self.globalnetCDFOption.show()
        


                
        #Create Items to Display and Connect Sub-Menus
        self.fileItem = gtk.MenuItem("File")
        self.fileItem.show()
        self.fileItem.set_submenu(self.fileMenu)
        
        
        self.optionsItem = gtk.MenuItem("Options")
        self.optionsItem.show()
        self.optionsItem.set_submenu(self.optionsMenu)
        


        #Create Menu Bar and Add Sub-Menus to Menu Bar
        self.menuBar = gtk.MenuBar()
        self.menuBar.append(self.fileItem)
        self.menuBar.append(self.optionsItem)
        self.menuBar.show()

        
        
    
    #########################################################################################################################################
    #                                  Function                                 #
    #                                addErrorMessage                            #   
    #                                                                   #
    #########################################################################################################################################   

    #This function takes in a message and adds it to the last line of the output area.
    #ToDo - Automatically scroll to the bottom of the area when a new message is added.
    def addErrorMessage(self, message):
        lastLine = self.outputBuffer.get_end_iter()
        self.outputBuffer.insert(lastLine, message + "\n")  



    """-------------------------------------------------------------------------------------------------------------------------------------|
    |                                                                   |                               |
    |                               Create Maps Page                            |
    |                                                                   |
    |           #########################################################################################           |
    |           #                       #       #           #           |
    |           #                       #       #           #           |
    |           #                       #       #           #           |
    |           #                       #       #           #           |
    |           #                       #       #       3       #           |
    |           #                       #       #           #           |
    |           #                       #       #           #           |   
    |           #           1           #   2   #           #           |   
    |           #                       #       #           #           |
    |           #                       #       #           #           |   
    |           #                       #       #           #           |           
    |           #                       #       #########################           |
    |           #                       #       #           #           |       
    |           #                       #       #           #           |       
    |           #                       #       #       4       #           |       
    |           #                       #       #           #           |
    |           #                       #       #           #           |               
    |           #########################################################################################           |       
    |           #               #           #               #           |       
    |           #               #           #               #           |           
    |           #               #           #               #           |   
    |           #               #           #               #           |               
    |           #       5       #       6       #       7       #           |               
    |           #               #           #               #           |               
    |           #               #           #               #           |   
    |           #               #           #               #           |   
    |           #               #           #               #           |       
    |           #########################################################################################           |   
    |                                                                   |
    |                                                                   |
    --------------------------------------------------------------------------------------------------------------------------------------"""

    #########################################################################################################################################
    #                                    Function                               #
    #                                selectionChanged                           #   
    #                                                                   #
    #########################################################################################################################################
    

    #This function is called when a new field is selected. It updates all the relevant data.
    def selectionChanged(self, widget, Data=None):
        
        #The function  adds every value in the array into the ListStore which are both passed into it. It also indexes each item
        def createListStores (listStore, dataArray):
            index = 0
            for value in dataArray:
                listStore.append([value, index])
                index += 1              
            
        #Sets the index of the field currently selected
        theModel, thePath = widget.get_selected()
        self.ClimateData.dataIndex = theModel.get_value(thePath,0)
        
        #Updates the variable data
        self.ClimateData.getXYZT()
        
        #Clear ListStores and add the contents of the respective arrays to each one
        for i in range(4):
            self.xyztListStores[i].clear()
            createListStores(self.xyztListStores[i], self.ClimateData.xyztArrays[i])
        
        #Buttons start inactive to avoid errors, so must be set to active
        if self.buttonsActive == False:
            for btn in self.xyztButtons:
                btn.set_sensitive(True)
            self.buttonsActive = True
            self.xyztButtons[self.currentXYZT].set_active(True)
            
        #Set the tree view to the currently active list store 
        self.xyztTreeview.set_model(self.xyztListStores[self.currentXYZT])
                
        #Update the labels
        self.updateLabels(self.currentXYZT)



    #########################################################################################################################################
    #                                  Function                             #
    #                                selectMaximum                              #   
    #                                                                   #
    #########################################################################################################################################
    
    
    #This function is called when the select maximum button is clicked. 
    #It changes the Maximum of the selected variable to the last value in the selection
    def selectMaximum(self, widget, Data=None):
    
        #This function keeps updating TempValue, so the final time it is called TempValue will be the last value in the selection
        def getLast (model, path, iter):
            self.TempValue = [model.get_value(iter, 0),model.get_value(iter, 1)]
             
            
        #Set temporary value as [] so if there is no selection the maximum will not be changed
        self.TempValue = []
        
        #For each row selected the getLast function is run
        self.xyztTreeview.get_selection().selected_foreach(getLast)
    
        #Checks to see if there was a selection     
        if self.TempValue != []:

            #Checks which variable is selected and changes the respective maximum
        
            if self.currentXYZT == 0:

                #The selected maximum can not be lower than the minimum value, to avoid errors in plotting.
                if self.TempValue[1] >= self.ClimateData.MinimumX[1]:
                    self.ClimateData.MaximumX = self.TempValue
                else:
                    self.addErrorMessage("Error - Maximum value can not be lower than minimum value")
                    
            elif self.currentXYZT == 1:     
                if self.TempValue[1] >= self.ClimateData.MinimumY[1]:               
                    self.ClimateData.MaximumY = self.TempValue
                else:
                    self.addErrorMessage("Error - Maximum value can not be lower than minimum value")

            elif self.currentXYZT == 2:
                if self.TempValue[1] >= self.ClimateData.MinimumZ[1]:
                    self.ClimateData.MaximumZ = self.TempValue
                else:
                    self.addErrorMessage("Error - Maximum value can not be lower than minimum value")

        else:
                self.addErrorMessage("Error - There are no values selected")

        
        
        #Update the labels
        self.updateLabels(self.currentXYZT) 

    #########################################################################################################################################
    #                                   Function                                #
    #                                 selectMinimum                             #   
    #                                                                   #
    #########################################################################################################################################   
    
    #This function is called when the Select Minimum button is clicked. 
    #It changes the Minimum of the selected variable to the first value in the selection
    def selectMinimum(self, widget, Data=None):
    
        #TempValue will only be empty on the first call of the function, so will only store the first value
        def getFirst (model, path, iter):
            if self.TempValue == []:
                self.TempValue = [model.get_value(iter, 0), model.get_value(iter, 1)]
                
                
        #Set temporary value as [] so if there is no selection the minimum will not be changed
        self.TempValue = []
        self.xyztTreeview.get_selection().selected_foreach(getFirst)
        
        #Checks to see if there was a selection
        if self.TempValue != []:
            
            #Checks which variable is selected and changes the respective minimum
            if self.currentXYZT == 0:
            
                #The Minimum value can not be greater than the maximum value.
                if self.TempValue[1] <= self.ClimateData.MaximumX[1]:
                    self.ClimateData.MinimumX = self.TempValue
                else:
                    self.addErrorMessage("Error - Minimum value can not be greater than maximum value")

            elif self.currentXYZT == 1:     
                if self.TempValue[1] <= self.ClimateData.MaximumY[1]:               
                    self.ClimateData.MinimumY = self.TempValue
                else:
                    self.addErrorMessage("Error - Minimum value can not be greater than maximum value")

            elif self.currentXYZT == 2:
                if self.TempValue[1] <= self.ClimateData.MaximumZ[1]:
                    self.ClimateData.MinimumZ = self.TempValue
                else:
                    self.addErrorMessage("Error - Minimum value can not be greater than maximum value")
        else:
            self.addErrorMessage("Error - There are no values selected")
                    
    
        #Update the labels
        self.updateLabels(self.currentXYZT)

    #########################################################################################################################################
    #                                  Function                                 #
    #                                 selectValue                               #   
    #                                                                   #
    #########################################################################################################################################

    #This function is called when the Select button is clicked
    #If T is selected, the function changes the chosen T value to the selected T value
    #If another variable is selected the function changes both the maximum and minimum to the last and first value in the selection respectively.   
    def selectValue(self, widget, Data=None):
        
        #Checks if T is selected.
        if self.currentXYZT == 3:
            #Get the location to the currently selected value
            theModel, thePath = self.xyztTreeview.get_selection().get_selected()
            
            #If there isn't a selected value thePath will be None, only update current values if there is a row selected
            if thePath != None:
                self.ClimateData.currentTValue = [theModel.get_value(thePath,0),theModel.get_value(thePath,1)]
            else:
                self.addErrorMessage("Error - There are no values selected")

        #Else if X, Y or Z are selected
        else:
            def getFirstandLast(model, path, iter, Data):
                #Functions runs multiple times, but the changes to MaxAndMin is passed through
                
                #MaxAndMin[0] is only empty in the first pass so will get the first value
                if MaxAndMin[0] == []:
                    MaxAndMin[0] = [model.get_value(iter, 0), model.get_value(iter, 1)]
                    
                #MaxAndMin[1] will keep updating with every pass of the function so will get the last value
                MaxAndMin[1] = [model.get_value(iter, 0), model.get_value(iter, 1)]
            
            #Set MaxAndMin to empty so if there is no selection, the maximum and minimum will not change
            MaxAndMin = [[],[]]

            #For each selected row run the getFirstandLast function
            self.xyztTreeview.get_selection().selected_foreach(getFirstandLast, Data)
            
            #If there are no rows selected MaxAndMin will be empty. Only update the minimums and maximums if it is not empty.
            if MaxAndMin != [[],[]]:
                #Check which variable is selected and change the maximum and minimum of that variable.
                if self.currentXYZT == 0:
                    self.ClimateData.MinimumX = MaxAndMin[0]
                    self.ClimateData.MaximumX = MaxAndMin[1]
                elif self.currentXYZT == 1:
                    self.ClimateData.MinimumY = MaxAndMin[0]
                    self.ClimateData.MaximumY = MaxAndMin[1]
                else:
                    self.ClimateData.MinimumZ = MaxAndMin[0]
                    self.ClimateData.MaximumZ = MaxAndMin[1]
            else:
                self.addErrorMessage("Error - There are no values selected")    

        #Update the labels.
        self.updateLabels(self.currentXYZT)

    #########################################################################################################################################
    #                                  Function                             #
    #                                    reset                              #   
    #                                                                   #
    #########################################################################################################################################

    #This function is called when the Reset button is clicked
    #It resets the chosen values of the variable selected to default
    def reset(self, widget):        
        #For X or Y (0 or 1) change minimum to lowest and maximum to highest value in the array.
        #For Z or T (2 or 3) change the selected value to the first in the array
        
        if self.currentXYZT == 0:
            self.ClimateData.MaximumX = [self.ClimateData.xArray[len(self.ClimateData.xArray) - 1], len(self.ClimateData.xArray) -1]    
            self.ClimateData.MinimumX = [self.ClimateData.xArray[0], 0] 
        elif self.currentXYZT == 1:
            self.ClimateData.MaximumY = [self.ClimateData.yArray[len(self.ClimateData.yArray) - 1], len(self.ClimateData.yArray) -1]
            self.ClimateData.MinimumY = [self.ClimateData.yArray[0], 0]
        elif self.currentXYZT == 2:
            self.ClimateData.currentZValue = [self.ClimateData.zArray[0], 0]
            self.ClimateData.MaximumZ = [self.ClimateData.zArray[0], 0]
            self.ClimateData.MinimumZ = [self.ClimateData.zArray[0], 0]
        else:
            self.ClimateData.currentTValue = [self.ClimateData.tArray[0], 0]
        
        #Update the lables
        self.updateLabels(self.currentXYZT)
        
    #########################################################################################################################################
    #                                  Function                                 #
    #                                 xyztClicked                               #   
    #                                                                   #
    #########################################################################################################################################       
    
    #This function is called a variable button is clicked; whether to change the variable, when a .set_active() function is called or even if a toggled button is clicked again.
    #It updates the labels, and the tree view to display the information about the newly selected variable
    def xyztClicked(self, widget, variable):

        #If widget is now active, it was either inactive before so the variable has changed, or the .set_active(True) function has been run on an already active button
        if widget.get_active():
            
            #Update current and previous variable choices
            previousXYZT = self.currentXYZT
            self.currentXYZT = variable 
            
            #Checks to see if the variable has changed, the current variable will be different to the previous variable.        
            if variable != previousXYZT:
                #If it has changed the previous variables button is set to not be active (Toggled Off)
                self.xyztButtons[previousXYZT].set_active(False)    
                
            #The tree view model and title are updated
            self.xyztTreeview.set_model(self.xyztListStores[variable])
            self.treeViewColumn.set_title(self.variablesTitle[variable])
            
            #Change the label names according to the variable chosen            
            if variable != 3:
                for informationLabel, labelName in zip(self.xyztInformationLabels, self.xyzLabelNames):
                    informationLabel.set_markup(self.labelSize + labelName + self.labelEnd)
                
                #Allow multiple rows to be selected
                self.xyztTreeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
                
                #Activate the select maximum and minimum buttons
                self.xyztButtons[4].set_sensitive(True)
                self.xyztButtons[5].set_sensitive(True)
            else:
                for informationLabel, labelName in zip(self.xyztInformationLabels, self.tLabelNames):
                    informationLabel.set_markup(self.labelSize + labelName + self.labelEnd)
                    
                #Allow only a single row to be selected
                self.xyztTreeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
                
                #Deactivate the maximum and minimum buttons
                self.xyztButtons[4].set_sensitive(False)
                self.xyztButtons[5].set_sensitive(False)
                
            #Update the labels  
            self.updateLabels(self.currentXYZT)
        
        #The widget will be inactive when the user clicks a toggled down button or the .set_active(False) function is run
        else:
            #Checks to see if the user clicked a toggled down button, and if so sets that button to active.
            #There must be a button toggled down.
            if variable == self.currentXYZT:
                widget.set_active(True)


    #########################################################################################################################################
    #                                  Function                             #
    #                                updateLabels                               #   
    #                                                                   #
    #########################################################################################################################################

    #This function is called whenever the data that the labels are showing changes.
    #It simple updates the labels to show the new data.
    def updateLabels(self, variable):

        #shortcut is to avoid rewriting self.Climate data multiple times. Can be changed
        shortcut = self.ClimateData
        
        #The label information about the selected variable is loaded into a list, the data is converted to string if it is numerical
        if variable == 0:
            self.OutputData = [shortcut.variableNames[0], str(shortcut.MinimumX[0]), str(shortcut.xInterval), 
                       shortcut.unitNames[0], str(shortcut.MaximumX[0]), str(shortcut.MaximumX[1]-shortcut.MinimumX[1] + 1)]            
        elif variable == 1:
            self.OutputData = [shortcut.variableNames[1], str(shortcut.MinimumY[0]), str(shortcut.yInterval), 
                       shortcut.unitNames[1], str(shortcut.MaximumY[0]), str(shortcut.MaximumY[1]-shortcut.MinimumY[1] + 1)]            
        elif variable == 2:
            self.OutputData = [shortcut.variableNames[2], str(shortcut.MinimumZ[0]), str(shortcut.zInterval), 
                                       shortcut.unitNames[2], str(shortcut.MaximumZ[0]), str(shortcut.MaximumZ[1]-shortcut.MinimumZ[1] + 1)]    
        else:
            self.OutputData = [shortcut.variableNames[3], shortcut.unitNames[3], str(shortcut.currentTValue[0]), '', '', '']
    
        #For each item in the list create there is a corresponding label. 
        #These are cycled through and the labels text is updated.
        for outputLabel, outputData in zip(self.xyztOutputLabels, self.OutputData):
            outputLabel.set_markup(self.labelSize + outputData + self.labelEnd )
            outputLabel.set_alignment(0, 0.5)

    #########################################################################################################################################
    #                                  Function                                 #
    #                                   plotMap                             #   
    #                                                                   #
    #########################################################################################################################################
    
    #This method is called when the Add To Maps button or the Plot Map button are clicked
    #It either plots the map to display or plots the map to add to the viewing area.
    def plotMap(self, widget, mode):
        
        #Checks to see if a field has actually been selected.
        if self.ClimateData.dataIndex != None:
            
            #Creating references to the data to make it easier to read.
            i = self.ClimateData.dataIndex
            Data = self.ClimateData.DataSet
            tIndex = self.ClimateData.currentTValue[1]

        
            #Mode is the variable passed in as a parameter, if it is 0 the Plot Map button has been clicked
            #If it is 1 the Add to Maps button has been clicked.
            if mode == 0:
                #If the Plot Map button is clicked, the map should not be saved.
                #The reset function is called to set file name to None inside CFPlot
                #This will display the map in a pop out window when 'con' is called.
                cfp.reset()


            #If the add maps button has been clicked:
            else:
            
                #This loop checks to see if the name of the map entered into the entry has already been used
                #x is the pixbuf of the map, name is the map name. 
                #If the map name has already been used an error message is displayed and the plotMap function is exited
                for x, name in self.maps:
                    if self.mapNameEntry.get_text() == name:
                        self.addErrorMessage("Error - Map name already exists") 
                        return None 

                #Checks to see if there is actually text in the map name entry, otherwise the plotMap function is exited.   
                if self.mapNameEntry.get_text() == "":
                    self.addErrorMessage("Error - Map name not specified")
                    return None                                 
                else:   
                    #If all other validation has been passed a temporary file name is created to store the map in. 
                    #This file will be deleted automatically in another function.
                    fileName = "temporarymap123456789.png"
                    cfp.setvars(file=fileName)
                    
            #Updates where the plot shows (e.g. Northern Hemisphere) depending on mapMode
            if self.mapMode == 0:
                cfp.mapset()
            
            elif self.mapMode == 1:
                cfp.mapset(proj='npstere')
                
            else:
                cfp.mapset(proj='spstere')


            #Checks to see if the data is two dimensional. 
            #If it is the number of length 1 dimensions in the shape of the four dimensional array will be 2
            if (Data[i].subspace[:, self.ClimateData.MinimumZ[1]:self.ClimateData.MaximumZ[1]+1, 
                         self.ClimateData.MinimumY[1]:self.ClimateData.MaximumY[1]+1, 
                                             self.ClimateData.MinimumX[1]:self.ClimateData.MaximumX[1]+1]
                            ).shape.count(1) == 2:
                
                #Plot the Data
                #plotType decides if the plot is a Hovmuller plot or not 
                cfp.con((Data[i].subspace[:, self.ClimateData.MinimumZ[1]:self.ClimateData.MaximumZ[1]+1, 
                                                          self.ClimateData.MinimumY[1]:self.ClimateData.MaximumY[1]+1, 
                                                          self.ClimateData.MinimumX[1]:self.ClimateData.MaximumX[1]+1]
                                         ), lines=self.plotType)
            #If the data is not 2 dimensional
            else:
                self.addErrorMessage('Error - Incorrect number of dimensions')      
            
            #If the button add to maps was pressed
            if mode == 1:
                #Adds the new maps file name and map title to the newMaps list
                self.newMaps.append([fileName, self.mapNameEntry.get_text()])
    
                #Calls two other functions which add the map to the viewing area.
                self.addNewMaps()
                self.addMapsToDisplay()     
    
            
    #This function is called when any of the map property radio buttons are called. 
    #mapMode is changed depending on which button was pressed.
    def mapModeSelection(self, widget, mode):
        if widget.get_active():
            self.mapMode = mode
    
    #This function is called when the Hovmuller check button is clicked
    #If changed to active the plotType is set to 0 (which  means Hovmuller plot is true) else 1
    def plotTypeSelection(self, widget):
        if widget.get_active():
            self.plotType = 0
        else:
            self.plotType = 1


    #########################################################################################################################################
    #                                  Region #1                                #
    #                           Field Selection Region                              #   
    #                          (self.fieldSelectionInputWindow)                         #
    #########################################################################################################################################   
    

    #This function is called when the Create Maps page is being created. 
    #It creates the Tree View for the user to select which field from the file they want to use 
    def addFieldSelection(self):
            
                
        #The Tree View is put into a scrolled window which has a vertical scrolling bar but not a horizontal scrolled bar. 
        self.fieldSelectionInputWindow = gtk.ScrolledWindow()
        self.fieldSelectionInputWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)

        #The tree view is created and properties are set
        self.fieldSelectionView = gtk.TreeView(None)
        self.fieldSelectionView.set_search_column(1)        # Sets the search column to 1 (The field name)
        self.fieldSelectionView.set_rules_hint(True)        # Alternating lines in the tree view will have different background colours
        self.fieldSelectionView.set_headers_clickable(True) #The headers can be clicked to re order the model

        #The tree view ListStore is created 
        #This stores [Index, Field Name, Length of X Array, Length of Y Array, Length of Z Array and Length of T Array]
        self.fieldSelectionData = gtk.ListStore(int, str, int, int, int, int)
        
        #The tree view's model is set to this list store. If the list store is edited the tree view will automatically change   
        self.fieldSelectionView.set_model(self.fieldSelectionData)      
        
        
        
        #The cell renderer is used to display the text in list store.
        self.fieldSelectionRenderer = gtk.CellRendererText() 
        self.fieldSelectionRenderer.set_property('xpad', 25)        
            
        #This loop creates a tree view column for each of the items in the list store 
        for i in range(len(self.fieldSelectionTitles)):
            #gtk.TreeViewColumn is initialised with (Title, Renderer, Column in ListStore being displayed)
            fieldSelectionColumn = gtk.TreeViewColumn(self.fieldSelectionTitles[i], self.fieldSelectionRenderer, text=i)

            #The column can be sortable
            fieldSelectionColumn.set_sort_column_id(i)          
            
            #Sets the alignment of the title, (set in InitialiseVariables function)
            fieldSelectionColumn.set_alignment(self.fieldSelectionTitlesAlignment)

            #Each column is a fixed width, dependant on the size of the screen.
            fieldSelectionColumn.set_property('sizing', gtk.TREE_VIEW_COLUMN_FIXED)
            
            #i is 1 when the Field Names column is being added.
            if i == 1:
                fieldSelectionColumn.set_fixed_width(int(self.windowWidth * 0.25))
            else:
                fieldSelectionColumn.set_fixed_width(int(self.windowWidth * 0.04))
            
            #Adds the column created to the tree view
            self.fieldSelectionView.append_column(fieldSelectionColumn)
        
        #Add the tree view to the scrolled window
        self.fieldSelectionInputWindow.add(self.fieldSelectionView)
        
        
        #When the selection is changed the function selectionChanged is called.
        self.fieldSelectionChoice = self.fieldSelectionView.get_selection()
        self.fieldSelectionChoice.connect("changed", self.selectionChanged)




    #########################################################################################################################################
    #                                  Region #2                                #
    #                               XYZT Selection                              #   
    #                              (self.xyztTreeviewWindow)                            #
    #########################################################################################################################################
    
    #This function is called when the Create Maps page is being created
    #It creates the tree view to see the data in the arrays of each variable
    def addXYZTSelection(self):
        #Creates a cell renderer to display the text        
        self.valueRenderer = gtk.CellRendererText()
        self.valueRenderer.set_property('xalign', 1)            
                    
        #A scrolled window to contain the tree view is created with a vertical scroll bar only
        self.xyztTreeviewWindow = gtk.ScrolledWindow()
        self.xyztTreeviewWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        self.xyztTreeviewWindow.show()
        
        #The tree view is created
        self.xyztTreeview = gtk.TreeView(None)
        self.xyztTreeview.show()
        
        self.xyztTreeview.set_rules_hint(True)          # Alternating lines will have different background colours

        #Adds the tree view to the scrolled window.
        self.xyztTreeviewWindow.add(self.xyztTreeview)          
        
        #Only a single column is needed. Initialised with (Title, Renderer, Column in List Store to Display)
        self.treeViewColumn = gtk.TreeViewColumn(self.variablesTitle[self.currentXYZT], self.valueRenderer, text=0)
        self.treeViewColumn.set_alignment(0.5)
        self.treeViewColumn.set_property('sizing', gtk.TREE_VIEW_COLUMN_FIXED)
        self.treeViewColumn.set_fixed_width(150)
        self.xyztTreeview.append_column(self.treeViewColumn)
        
        #Set the model of the tree view to be a list store with two columns, float and int. 
        #The second column is not displayed.
        self.xyztTreeview.set_model(gtk.ListStore(float, int))
        

    #########################################################################################################################################
    #                                   Region #3                               #
    #                           Select Data Page (Variable Display)                     #   
    #                               (self.xyztVBox)                             #
    #########################################################################################################################################
    

    #This function is called when the Create Maps page is being created
    #It creates the labels and buttons for the Select Data tab in the notebook on the top right of the page.
    def addSelectDataPage(self):
        #A container to hold all of the labels and buttons is created
        self.xyztVBox = gtk.VBox()

        #All labels will be in a table with 4 rows and 5 columns
        self.xyztTable = gtk.Table(4, 5, False)
        self.xyztTable.set_row_spacings(30)

        #The table is put at the start of the container so will be at the top of this page
        self.xyztVBox.pack_start(self.xyztTable, False, False, 2)
        
        #The labels are created and placed into the table.
        #Labels start with no text
        self.xyztLabel0 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel0, 0, 1, 0, 1)
        
        self.xyztLabel1 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel1, 0, 1, 1, 2)
        
        self.xyztLabel2 = gtk.Label('')     
        self.xyztTable.attach(self.xyztLabel2, 0, 1, 2, 3)
        
        self.xyztLabel3 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel3, 3, 4, 0, 1)
        
        self.xyztLabel4 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel4, 3, 4, 1, 2)
        
        self.xyztLabel5 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel5, 3, 4, 2, 3)
        
        self.xyztLabel6 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel6, 1, 2, 0, 1)
        
        self.xyztLabel7 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel7, 1, 2, 1, 2)
            
        self.xyztLabel8 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel8, 1, 2, 2, 3)
        
        self.xyztLabel9 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel9, 4, 5, 0, 1)
        
        self.xyztLabel10 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel10, 4, 5, 1, 2)
        
        self.xyztLabel11 = gtk.Label('')
        self.xyztTable.attach(self.xyztLabel11, 4, 5, 2, 3)
        
        
        #The labels are put into lists so that setting their texts will be easier
        self.xyztInformationLabels = [self.xyztLabel0, self.xyztLabel1, self.xyztLabel2, self.xyztLabel3, self.xyztLabel4,self.xyztLabel5]

            
        self.xyztOutputLabels = [self.xyztLabel6, self.xyztLabel7, self.xyztLabel8, self.xyztLabel9, self.xyztLabel10, self.xyztLabel11]
        
        #Initially set the title labels e.g.(Name :) for X since it is the default starting variable.
        for informationLabel, labelName in zip(self.xyztInformationLabels, self.xyzLabelNames):
            informationLabel.set_markup(self.labelSize + labelName + self.labelEnd)
            informationLabel.set_alignment(0, 0.5)
        
        
        
        #A table to pack the all buttons is created with 3 rows and 4 columns. 
        self.xyztButtonTable = gtk.Table(3, 4, False)
        self.xyztVBox.pack_start(self.xyztButtonTable, False, False, 2) 
        
    
        #The X, Y, Z, T ToggleButtons are created and placed into the table. 
        #All buttons connect to the same function, xyztClicked(), however pass a different parameter into it.       
        self.xBtn = gtk.ToggleButton('X')
        self.xBtn.connect('clicked', self.xyztClicked, 0)
        
        self.yBtn = gtk.ToggleButton('Y')
        self.yBtn.connect('clicked', self.xyztClicked, 1)
        
        self.zBtn = gtk.ToggleButton('Z')
        self.zBtn.connect('clicked', self.xyztClicked, 2)
        
        self.tBtn = gtk.ToggleButton('T')   
        self.tBtn.connect('clicked', self.xyztClicked, 3)   
        
        
        self.xyztButtonTable.attach(self.xBtn, 0, 1, 2, 3, gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL, 25,25 )
        self.xyztButtonTable.attach(self.yBtn, 1, 2, 2, 3, gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL, 25,25 )
        self.xyztButtonTable.attach(self.zBtn, 2, 3, 2, 3, gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL, 25,25 )
        self.xyztButtonTable.attach(self.tBtn, 3, 4, 2, 3, gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL, 25,25 )
        
            
        #The selection buttons and reset buttons are created and put into the table.
        #The buttons are connected to their respective functions

        self.selectMinimumBtn = gtk.Button('Select Minimum')
        self.selectMinimumBtn.connect('clicked', self.selectMinimum)
        
        self.selectMaximumBtn = gtk.Button('Select Maximum')
        self.selectMaximumBtn.connect('clicked', self.selectMaximum)
        
        self.selectBtn = gtk.Button('Select')
        self.selectBtn.connect("clicked", self.selectValue)
        
        
        self.resetBtn = gtk.Button('Reset')
        self.resetBtn.connect("clicked", self.reset)
        
        self.xyztButtonTable.attach(self.selectMinimumBtn, 0, 2, 1, 2, gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL, 25,10 )
        self.xyztButtonTable.attach(self.selectMaximumBtn, 2, 4, 1, 2, gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL, 25,10 )
        self.xyztButtonTable.attach(self.selectBtn, 0, 2, 0, 1, gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL, 25,10 )
        self.xyztButtonTable.attach(self.resetBtn, 2, 4, 0, 1, gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL, 25,10 )
        
        
        
        #Put all buttons into a list to make them easier to access.
        self.xyztButtons = [self.xBtn, self.yBtn, self.zBtn, self.tBtn, self.selectMinimumBtn, self.selectMaximumBtn,self.selectBtn, self.resetBtn]
        
        
        #Start with buttons inactive

        for btn in self.xyztButtons:
            btn.set_sensitive(False)

    #########################################################################################################################################
    #                                     Region #3                             #
    #                               Map Properties Page                         #   
    #                                (self.mapPropertiesTable)                          #
    #########################################################################################################################################
    
    #This function is called when the Create Maps page is being created
    #It adds the second page to the notebook in the top right of the page, Map Properties
    def addMapPropertiesPage(self):

        #A table to contain all the options is created. It currently has 4 rows and a single column
        self.mapPropertiesTable = gtk.Table(4, 1, False)

        #The radio buttons are initialised with (Group, Text)
        #They are added to the table and are connected to the same function, mapModeSelection, with a different parameter being passed through
        #The first radio button created has no group
        self.normalViewRadioButton = gtk.RadioButton(None, "View Whole Map")
        self.mapPropertiesTable.attach(self.normalViewRadioButton, 0, 1, 0, 1)
        self.normalViewRadioButton.connect("toggled", self.mapModeSelection, 0)
        
        #The second two radio button's group uses the first radio button widget to add them to the group
        self.northernPoleRadioButton = gtk.RadioButton(self.normalViewRadioButton, "View from Northern Pole")
        self.mapPropertiesTable.attach(self.northernPoleRadioButton, 0, 1, 1, 2)
        self.northernPoleRadioButton.connect("toggled", self.mapModeSelection, 1)
        
        self.southernPoleRadioButton = gtk.RadioButton(self.normalViewRadioButton, "View from Southern Pole")
        self.mapPropertiesTable.attach(self.southernPoleRadioButton, 0, 1, 2, 3)
        self.southernPoleRadioButton.connect("toggled", self.mapModeSelection, 2)

        
        #A check button to decide if the user wants a Hovmuller plot is created
        #It is added to the table and connected to a function.      
        self.HovmullerPlotCheckButton = gtk.CheckButton("Hovmuller Plot")
        self.mapPropertiesTable.attach(self.HovmullerPlotCheckButton, 0, 1, 3, 4)
        self.HovmullerPlotCheckButton.connect("toggled", self.plotTypeSelection)


    #########################################################################################################################################
    #                                   Region #4                           #
    #                               Plotting Buttons Area                           #   
    #                                     (self.PlotOptions)                            #
    #########################################################################################################################################
    
    #This function is called when the Create Maps page is created
    #It adds the buttons to plot the map, view the data and add the maps to the viewing area
    def addPlottingButtonsArea(self):
        
        #A table to add all the buttons and labels to is created        
        self.PlotOptions = gtk.Table(2, 3, False)
        self.PlotOptions.show()
        
        #A label to tell the user to enter a map name is added to the top left
        self.PlotOptions.attach(gtk.Label('Enter map name: '), 0, 1, 0, 1)
        
        #The map name can be entered into this Entry widget which takes up the top right and top middle cells
        self.mapNameEntry = gtk.Entry()
        self.PlotOptions.attach(self.mapNameEntry, 1, 3, 0, 1)

        #The View Data button is created and added to the table. 
        #It is connected to a function which can be found later in the code     
        self.viewDataBtn = gtk.Button('View Data')
        self.PlotOptions.attach(self.viewDataBtn, 0, 1, 1, 2)
        self.viewDataBtn.connect("clicked", self.viewData)
        
        #The add to maps button is created and added to the table
        #It is connected to the plotMap function
        self.addBtn = gtk.Button('Add to Maps')
        self.PlotOptions.attach(self.addBtn, 1, 2, 1, 2)
        self.addBtn.connect("clicked", self.plotMap, 1)
        
        #The plot map button is created and added to the table
        #It also is connected to the plotMap function but passes a different parameter into it.
        self.plotMapBtn = gtk.Button('Plot Map')
        self.PlotOptions.attach(self.plotMapBtn, 2, 3, 1, 2)
        self.plotMapBtn.connect("clicked", self.plotMap, 0)

    #########################################################################################################################################
    #                                     Region #5                         #
    #                                   Output Messages Area                        #   
    #                                         (self.outputFrame)                        #
    #########################################################################################################################################
    
    #This function is called when the Create Maps page is created
    #It adds the output message box, where any errors or other messages are displayed on
    def addOutputMessagesArea(self):
        
        #The output box is put into a scrolled window which only has a vertical scroll bar
        self.outputWindow = gtk.ScrolledWindow()
        self.outputWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        
        #A text view widget is created and added to the scrolled window
        self.outputTextView = gtk.TextView(None)
        self.outputWindow.add(self.outputTextView)
        
        #The text views properties are set. 
        self.outputTextView.set_editable(False)
        self.outputTextView.set_cursor_visible(False)
        self.outputTextView.set_wrap_mode(gtk.WRAP_WORD)
                 
        #Since the text view was created without a buffer, a buffer is automatically created for it.
        #This buffer is stored in outputBuffer, any messages will be added to this. 
        self.outputBuffer = self.outputTextView.get_buffer()
        

        #The output window is stored into a frame for clarity
        self.outputFrame = gtk.Frame(label="Output Messages")   
        self.outputFrame.add(self.outputWindow)

    #########################################################################################################################################
    #                                     Region #6                         #
    #                                      Map Listings Area                        #   
    #                                      (self.mapListingsWindow)                     #
    #########################################################################################################################################
    
    #This function is called when the selected map from the user created list of maps is changed
    #It changes the map thumbnail being displayed at the bottom right of the page
    def mapChanged(self, widget, Data=None):
        #The currently selected map is extracted from the tree view
        theModel, thePath = widget.get_selected()
        
        #Checks to see if there is actually a selection
        if thePath != None:
            #Gets the map name from the model
            mapName = theModel.get_value(thePath,0)
            
            #Cycles through the list of maps to find the map pixbuf
            for pixbuf, name in self.maps:
                if mapName == name:
                    #The map pixbuf is rescaled and the image is set from the pixbuf
                    scaledMap = pixbuf.scale_simple(int(self.windowWidth * 0.2), int(self.windowHeight * 0.2), gtk.gdk.INTERP_BILINEAR)
                    self.mapThumbnail.set_from_pixbuf(scaledMap)

                    
    #This function is called when the Create Maps page is created
    #It adds a tree view to show the maps the user has created
    def addMapListings(self):
        
        #The scrolled window is created to contain the tree view, with only a vertical scroll bar.
        self.mapListingsWindow = gtk.ScrolledWindow()
        self.mapListingsWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
    
        #A model for the tree view is created with only one column, the map name
        #Items are added to this model whenever the user adds or deletes maps, this will be shown later in the code
        self.mapListingsModel = gtk.ListStore(str)
        
        #The tree view is created and properties set
        self.mapListings = gtk.TreeView(None)
        self.mapListings.set_rules_hint(True)
        
        #A cell renderer is created to display the text
        self.mapListingRenderer = gtk.CellRendererText()
        self.mapListingRenderer.set_property('xalign', 1)
        
        #Only 1 column is needed, it is created and the properties are set.
        self.mapListingColumn = gtk.TreeViewColumn('Maps', self.mapListingRenderer, text = 0)
        self.mapListingColumn.set_alignment(0.5)
        self.mapListingColumn.set_property('sizing', gtk.TREE_VIEW_COLUMN_FIXED)
        self.mapListingColumn.set_fixed_width(int(self.windowWidth * 0.15))

        #The column is added to the tree view and the model is set      
        self.mapListings.append_column(self.mapListingColumn)
        self.mapListings.set_model(self.mapListingsModel) 
        
        #The tree view is connected to the function mapChanged whenever the selection changes
        self.mapListingChoice = self.mapListings.get_selection()
        self.mapListingChoice.connect("changed", self.mapChanged)
        
        #The tree view is added to the scrolled window.
        self.mapListingsWindow.add(self.mapListings)
        
        
    
        
    #########################################################################################################################################
    #                                     Region #7                         #
    #                                   Map Thumbnail View Area                     #   
    #                                      (self.mapThumbnailFrame)                     #
    #########################################################################################################################################
    
    #This function is called when the Create Maps page is created
    #It prepares an area for map thumbnails to be displayed.
    def addThumbnailArea(self):
                    
        #The map thumbnail is an image, which initially is empty
        self.mapThumbnail = gtk.Image()

        #A frame to surround the image is created with no label. 
        self.mapThumbnailFrame = gtk.Frame(None)

        #Since the image starts empty, the frame must be have a minimum size for the interface to have consistent spacing
        self.mapThumbnailFrame.set_size_request(int(self.windowWidth * 0.2), 0)
        
        #The image is added to the frame.
        self.mapThumbnailFrame.add(self.mapThumbnail)
        
        
    
    
    
    
    

    #########################################################################################################################################
    #                                                                   #
    #                                   Create Maps Page                            #   
    #                                   (self.fieldSelectionVBox)                       #
    #                                                                   #
    #########################################################################################################################################
        

    #This method is called in the main code
    #It adds the Create Maps page
    def addCreateMapsPage(self):

        #Each region is created
        #A seperate container for each of these regions is made so that the layout can easily be changed.

        #Region 1
        self.addFieldSelection()
        
        #Region 2 
        self.addXYZTSelection()
        
        #Region 3
        self.addSelectDataPage()
        self.addMapPropertiesPage()

        self.editDataNotebook = gtk.Notebook()
        self.editDataNotebook.set_tab_pos(gtk.POS_TOP)
        self.editDataNotebook.append_page(self.xyztVBox, gtk.Label('Select Data'))  
        self.editDataNotebook.append_page(self.mapPropertiesTable, gtk.Label('Map Properties'))     
        
        #Region 4
        self.addPlottingButtonsArea()
        
        #Region 5
        self.addOutputMessagesArea()
        
        #Region 6
        self.addMapListings()
        
        #Region 7
        self.addThumbnailArea()
        

    
        #Regions are joined together

        #Join Regions 1-4
        self.viewFieldsHBox = gtk.HBox(False, 0)
        self.viewFieldsHBox.pack_start(self.fieldSelectionInputWindow, False, False, 2)
        self.viewFieldsHBox.pack_start(self.xyztTreeviewWindow, False, False, 2)
        
        self.selectionsVBox = gtk.VBox()
        self.selectionsVBox.pack_start(self.editDataNotebook, False, False, 2)
        self.selectionsVBox.pack_end(self.PlotOptions, False, False, 2)

        self.viewFieldsHBox.pack_start(self.selectionsVBox, True, True, 2)

        #Join Regions 5-7
        self.outputsHBox = gtk.HBox(False, 0)
        self.outputsHBox.pack_start(self.outputFrame, True, True, 2)
        self.outputsHBox.pack_start(self.mapListingsWindow, False, False, 2)
        self.outputsHBox.pack_start(self.mapThumbnailFrame, False, False, 2)

        
        #Join All Regions
        self.CreateMapsVBox = gtk.VBox()
        self.CreateMapsVBox.pack_start(self.viewFieldsHBox, True, True, 2)
        self.CreateMapsVBox.pack_start(self.outputsHBox, True, True, 2)



        
    """-------------------------------------------------------------------------------------------------------------------------------------|
    |                                                                   |                               |
    |                                 View Maps Page                            |
    |                                                                   |
    |           #########################################################################################           |
    |           #                                           #           |
    |           #                                           #           |
    |           #                                           #           |
    |           #                                           #           |
    |           #                                               #           |
    |           #                                           #           |
    |           #                                           #           |   
    |           #                                           #           |   
    |           #                                           #           |
    |           #                                           #           |   
    |           #                                           #           |           
    |           #                                           #           |
    |           #                                           #           |       
    |           #                                           #           |       
    |           #                                               #           |       
    |           #                                           #           |
    |           #                                           #           |               
    |           #                                           #           |       
    |           #########################################################################################           |       
    |           #                                           #           |           
    |           #                                           #           |   
    |           #########################################################################################           |               
    |           #                                               #           |               
    |           #                                           #           |               
    |           #                                           #           |   
    |           #                                           #           |   
    |           #                                           #           |       
    |           #########################################################################################           |   
    |                                                                   |
    |                                                                   |
    --------------------------------------------------------------------------------------------------------------------------------------"""       
        
    #########################################################################################################################################
    #                                                                   #
    #                                    Map Layout Class                           #   
    #                                                                   #
    #########################################################################################################################################
    
    
    #Class for each map viewing area.
    class LayoutContent(gtk.EventBox):
    
        def __init__(self, xScale, yScale, layout):
            
            #The class is an event box type so the event box must be initialised
            gtk.EventBox.__init__(self)
            
            #The variables are initialised:
            
            #index is the index of the map in the list of maps.
            self.index = None
            
            #X and Y are used to get the current position of the map in the layout
            self.X = 0
            self.Y = 0

            #clickedX and clickedY store the position the mouse was when the mouse was clicked
            self.clickedX = 0
            self.clickedY = 0
            
            #clicked tells whether the mouse is currently clicked or not
            self.clicked = False
            
            #mapLayout stores the layout that was passed in as a parameter
            #It is the layout the class is inside
            self.mapLayout = layout
            
            #xScale and yScale store the proportion of the screen the map should initially take
            self.xScale = xScale
            self.yScale = yScale    
        
            #xScaling and yScaling store the magnitude of zoom for the map
            self.xScaling = xScale
            self.yScaling = yScale
        
            #mapImage stores the map as a gtk.Image. This itself is put inside the eventbox
            self.mapImage = None
            
            #Sets the event box settings
            self.set_visible_window(False)
            
            #Create events for mouse clicks and movement and connect them to the associated functions
            self.add_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)  
            self.connect("button-press-event", self.mouseClicked)
            self.connect("button-release-event", self.mouseReleased)
            self.connect("motion-notify-event", self.mouseMoved)

            #Puts the event box at the top left of the layout       
            self.mapLayout.put(self, 0, 0)

        #This function is called when a map thumbnail is drag and dropped onto the area.
        #It retrieves the map from the list of maps, stores and displays it.
        def addImage(self, widget, context, x, y, selection, targetType, time, pixbufs):
            
            #If there isn't a map alreading being stored, create an empty image and add it to the event box
            if self.mapImage == None:
                self.mapImage = gtk.Image()             
                self.add(self.mapImage)
            
            #Reset all the variables
            self.resetVariables()
            
            #The index of the map is passed through from the drag and drop event
            self.index = selection.format
        
            #Retrieve the default size map from the list of maps
            mapPixbuf = pixbufs[selection.format][0]
            
            #Finds the width and height of the screen
            topLevelWindow = widget.get_toplevel()
            self.ScreenWidth = topLevelWindow.get_screen().get_width()
            self.ScreenHeight = topLevelWindow.get_screen().get_height()

            #Scale the image
            scaledImage = mapPixbuf.scale_simple(int(self.ScreenWidth * self.xScale), int(self.ScreenHeight* self.yScale), gtk.gdk.INTERP_BILINEAR)

            #Store the map in the image and show it
            self.mapImage.set_from_pixbuf(scaledImage)
            self.mapImage.show()
        
            #Place the event box to the top left
            self.mapLayout.move(self, 0, 0)
            
            #Store the original pixbuf to mantain quality when zooming
            self.mapPixbuf = mapPixbuf

        #This function is called when the mouse is clicked on the event box
        #It stores the position of the mouse and finds the position of the event box
        def mouseClicked(self, widget, event):
            self.clicked = True
            self.clickedX = event.x
            self.clickedY = event.y
            self.X, self.Y = self.mapLayout.child_get(self, 'x', 'y')
        
        #This function is called when the mouse is realsed
        #It simple sets clicked to False
        def mouseReleased(self, widget, event):
            self.clicked = False
        
        #This function is called when the mouse is moved
        #If the mouse is clicked the map is moved depending on the mouses movement
        def mouseMoved(self, widget, event):
            #Check to see if the mouse in currently clicked
            if self.clicked:
                #If it is move the eventbox from its position when the mouse was clicked + the mouses displacement from the position where the mouse was clicked.
                self.mapLayout.move(self, self.X + int(event.x - self.clickedX), self.Y + int(event.y - self.clickedY))
        
        #This function is called when the image must be rescaled
        #It rescales the image based on xScaling and yScaling
        #xAdjustment and yAdjustment are to allow the maps position to be changed so zooming in stays on focus with the centre
        #However this has not yet been added
        def updateImage(self, xAdjustment, yAdjustment):
            #Checks to see if there is currently a map in the box
            if self.mapImage != None:   
                #If there is the original pixbuf is scaled and the map image is set from the scaled pixbuf.
                scaledPixbuf = self.mapPixbuf.scale_simple(int(self.ScreenWidth * self.xScaling), int(self.ScreenHeight * self.yScaling), gtk.gdk.INTERP_BILINEAR)
                self.mapImage.set_from_pixbuf(scaledPixbuf)         
                self.mapLayout.move(self, self.X + xAdjustment, self.Y + yAdjustment)
        
        #This function is called when zoom in or zoom out buttons are clicked on the toolbar
        #It updates the scaling and updates the map
        def zoom(self, scale):
            #Checks to see if there is currently a map in the box
            if self.mapImage != None:
                #If there is, find the maps current position
                self.X, self.Y = self.mapLayout.child_get(self, 'x', 'y')
                
                #Change the scaling based on the parameter passed in
                # scale will be > 1 for zooming in and <1 for zooming out
                self.xScaling = self.xScaling * scale
                self.yScaling = self.yScaling * scale
                
                #Update the image
                #To Do: Zoom functions should keep the centre in focus. Change parameters of updateImage to allow for this
                self.updateImage(0, 0)
        
        #This function is called when a new image is placed into the area or the image currently in the area is reset
        #It resets all the variables so the scale returns to default and its positioned again at the top left   
        def resetVariables(self):
            
            #Set variables back to default
            self.X = 0
            self.Y = 0
            self.xScaling = self.xScale
            self.yScaling = self.yScale
            self.ClickedX = 0
            self.ClickedY = 0
            self.Clicked = False
        
        #This function is called when the reset button on the toolbar is clicked
        #It resets the image to its default scale and position
        def reset (self):
            #Check if there is a map in the box
            if self.mapImage != None:
                #If there is call on these two functions to fully reset the image
                self.resetVariables()
                self.updateImage(0, 0)
        

        #This function is called when the remove button on the toolbar is clicked
        #It removes the map from the eventbox
        def removeImage(self):
            #Check if there is a map in the event box
            if self.mapImage != None:
                #If there is remove the image
                self.remove(self.mapImage)
                #Clear the image
                self.mapImage = None
                #Clear the index
                self.index = None
                
        #This function is called when the save button is clicked on the toolbar
        #ToDo: Make the function to save the map to the desired location    
        def saveMap(self):
            pass
        
        #This function returns the index of the map stored
        #It is called when a map needs to be deleted
        def mapID(self):
            if self.mapImage != None:
                return self.index
        
        #This function is called when the delete button is clicked on the toolbar       
        def deleteMap(self, mapIndex):
            #Checks to see if the map currently being deleted is being shown in this layout
            if self.index == mapIndex:
                #If it is it is removed
                self.removeImage()
            #Otherwise if the index is greater than the index of the map being deleled subtract 1
            #This is because the map will be destroyed from the list so all values above will drop by one value.
            elif self.index > mapIndex:
                self.index -= 1
        
        #This function is called when the compare button is clicked on the toolbar
        #It copies the scaling and position of one content to another
        def compareMaps(self, contents):

            #Get the current position of the map in the layout
            self.X, self.Y = self.mapLayout.child_get(self, 'x', 'y')

            #Copies the scalings and position to the other eventbox 
            contents.xScaling = self.xScaling
            contents.yScaling = self.yScaling
            contents.X = self.X
            contents.Y = self.Y
            
            #Update the image in the other event box
            contents.updateImage(0, 0)  

    #########################################################################################################################################
    #                                                                   #
    #                                    Toolbar Class                          #   
    #                                                                   #
    #########################################################################################################################################
    
    #Class to for toolbars (Initially there were multiple toolbars) 
    #This class can be removed since there is no longer a need for it
    class MapToolbar(gtk.Toolbar):  
    
        def __init__(self, content):
            #Class a a toolbar type so the toolbar must be initialised
            gtk.Toolbar.__init__(self)  
            
            #Set the orientation to horizontal
            self.set_orientation(gtk.ORIENTATION_HORIZONTAL)

            #Add all the options and connect them to the corresponding functions            
            self.append_item("Zoom In", "Zoom into image", "Zoom function", gtk.image_new_from_stock (gtk.STOCK_ZOOM_IN, gtk.ICON_SIZE_SMALL_TOOLBAR), self.zoom, 1.1)
            self.append_space()
            self.append_item("Zoom Out", "Zoom out of image", "Zoom out function", 
                     gtk.image_new_from_stock (gtk.STOCK_ZOOM_OUT, gtk.ICON_SIZE_SMALL_TOOLBAR), self.zoom, 0.9)
            self.append_space()
            self.append_item("Compare", "Copies scale and location from selected", "Compare", 
                          gtk.image_new_from_stock (gtk.STOCK_CONVERT, gtk.ICON_SIZE_SMALL_TOOLBAR), self.compareMaps)
            self.append_space()
            self.append_item("Reset", "Reset Image", "Reset", gtk.image_new_from_stock (gtk.STOCK_REFRESH, gtk.ICON_SIZE_SMALL_TOOLBAR), self.reset)
            self.append_space()
            self.append_item("Remove", "Remove Image from Viewing Area", "Remove",
                         gtk.image_new_from_stock (gtk.STOCK_CANCEL, gtk.ICON_SIZE_SMALL_TOOLBAR), self.removeImage)
            self.append_space()
            self.append_item("Save Map", "Save map to file", "Save Map", gtk.image_new_from_stock (gtk.STOCK_FLOPPY, gtk.ICON_SIZE_SMALL_TOOLBAR), self.saveMap)
            self.append_space()
            self.append_item("Delete Map", "Deletes map from store", "Delete Map", 
                     gtk.image_new_from_stock (gtk.STOCK_DELETE, gtk.ICON_SIZE_SMALL_TOOLBAR), self.deleteMap)
            self.append_space()

            self.leftToggle = self.append_element(gtk.TOOLBAR_CHILD_TOGGLEBUTTON, None, "Left Map", "Selects Left Map", "Left", 
                                  gtk.image_new_from_stock (gtk.STOCK_GO_BACK, gtk.ICON_SIZE_SMALL_TOOLBAR), self.leftMap, None)
            self.append_space()
            self.rightToggle = self.append_element(gtk.TOOLBAR_CHILD_TOGGLEBUTTON, None, "Right Map", "Selects Right Map", "Right",
                                                               gtk.image_new_from_stock (gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_SMALL_TOOLBAR), self.rightMap, None)

            #Store the eventboxes the toolbar references
            self.mapContents = content
            
            #Default eventbox is the one on the left (0)
            self.mapContent = content[0]
            self.leftToggle.set_active(True)
            
            #Selected is true if editing the left map, or false for the right map
            self.selected = True    
            
        #This function calls the compareMap function of the Layout Content class it is referencing
        #It passes the other Layout Content class as its parameter
        def compareMaps(self, widget):
            if self.selected == True:
                self.mapContent.compareMaps(self.mapContents[1])
            else:
                self.mapContent.compareMaps(self.mapContents[0])
        

        
        def leftMap(self, widget):
            #If the button has been toggled on when the right button is also toggled on, 
            #it changes the map contents and sets the toggle on the right off
            if widget.get_active() == True and self.rightToggle.get_active() == True:
                self.mapContent = self.mapContents[0]
                self.selected = True
                self.rightToggle.set_active(False)

            #If the button has toggled off but the right is also toggled off it retoggles the button
            elif widget.get_active() == False and self.rightToggle.get_active() == False:               
                widget.set_active(True)
                
        #This function is similar to the leftMap function except goes the opposite way.
        def rightMap(self, widget):
            if widget.get_active() == True and self.leftToggle.get_active() == True:
                self.leftToggle.set_active(False)
                self.mapContent = self.mapContents[1]
                self.selected = False
            elif widget.get_active() == False and self.leftToggle.get_active() == False:                
                widget.set_active(True)

        #This function delete the map in the currently active event box.
        def deleteMap(self, widget):    
            #Retrieves the map index of the map inside the event box
            mapIndex = self.mapContent.mapID()
            #checks if there is a map
            if mapIndex != None:
                #If there is, delete the index from the list of maps
                del CF.maps[mapIndex]
                #Remove the map if it is there from the map viewing areas
                CF.doubleViewContent0.deleteMap(mapIndex)
                CF.doubleViewContent1.deleteMap(mapIndex)

                #Update the thumbnails
                CF.addMapsToDisplay()
        

        #These functions just call functions from the event box class
        
        def zoom(self, widget, scale):
            self.mapContent.zoom(scale)
    
        def reset(self, widget):    
            self.mapContent.reset()
        
        def removeImage(self, widget):
            self.mapContent.removeImage()
            
        def saveMap(self, widget):
            self.mapContent.saveMap()
            
        


    #########################################################################################################################################
    #                                  Function                                 #
    #                                   addNewMaps                              #   
    #                                                                   #
    #########################################################################################################################################

    #This function is called when a new map is added by the user
    #It adds the map to the list of maps
    def addNewMaps(self):
        #Cycle through the new maps
        for plottedMap in self.newMaps:
            #Retrieve a pixbuf from the file
            mapPixBuf = gtk.gdk.pixbuf_new_from_file(plottedMap[0])
            #Add the pixbuf and map name to the list of maps
            self.maps.append([mapPixBuf, plottedMap[1]])
            #Remove the file
            os.remove(plottedMap[0])
        #Clear the new maps so they do not get added multiple times
        self.newMaps = []

    #########################################################################################################################################
    #                                  Function                                 #
    #                                  addMapsToDisplay                             #   
    #                                                                   #
    #########################################################################################################################################

    #This function is called whenever a map is added or deleted from the list of maps
    #It redraws the thumbnails and sets the model of the treeview of maps
    def addMapsToDisplay(self):

        #Remove the hBox from the viewport and re-create it
        self.mapDisplayViewport.remove(self.hBox)
        self.hBox = gtk.HBox()  
        
        #There must be a minimum size so that the display stays consistent if there are no maps
        self.hBox.set_size_request(0, int(self.windowHeight * self.mapThumbnailScalingY))
        
        #Add the hbox back to the viewport and show it 
        self.mapDisplayViewport.add(self.hBox)
        self.hBox.show()
            
        #Clear the map model on the Create Maps page
        self.mapListingsModel.clear()

        #Cycles each map in the list
        for mapPixbuf in self.maps:
            #Create a box to store the map and its title, then show it          
            mapVBox = gtk.VBox()
            mapVBox.show()
            
            #Create a button, and image. 
            mapButton = gtk.Button()
            mapImage = gtk.Image()

            #Scale the map's pixbuf to the thumbnails size and set the image to that pixbuf 
            newWidth = int(self.windowWidth * self.mapThumbnailScalingX)
            newHeight = int(self.windowHeight * self.mapThumbnailScalingY)
            scaledMap = mapPixbuf[0].scale_simple(newWidth, newHeight, gtk.gdk.INTERP_BILINEAR)
            mapImage.set_from_pixbuf(scaledMap)
            
            #Place the image on the button and show both
            mapButton.add(mapImage)
            mapButton.show()
            mapImage.show()

            #Create a label, show it and add both the button and label to the box
            mapLabel = gtk.Label(mapPixbuf[1])
            mapLabel.show()
            mapVBox.pack_start(mapLabel, False, False, 2)
            mapVBox.pack_end(mapButton, True, True, 2)
            
            #Add the box to the viewports box   
            self.hBox.pack_start(mapVBox, False, False, 2)
            
            #Set the button to be draggable, sending the maps index when dropped into the map viewing area.
            mapButton.drag_source_set(gtk.gdk.BUTTON1_MASK, [( "", 0, self.maps.index(mapPixbuf) )],gtk.gdk.ACTION_COPY)

            #When the button is dragged connect the function send data to select which data the button gives to the map viewing area
            mapButton.connect("drag_data_get", self.SendData)
            
            #Add the map name to the map listing model
            self.mapListingsModel.append([mapPixbuf[1]])
            
        

        
    #This function is called when a map thumbnail is dragged.
    #It sets the data which is sent to the reciever 
    def SendData (self, widget, context, selection, targetType, eventTime):     
        selection.set(selection.target, targetType, "map")  
    
    #This function is called when a map thumbnail is dropped onto a viewing area
    #It sends all the data from the map thumnail and also the list of maps
    def replaceImage(self, widget, context, x, y, selection, targetType, time, contents):
        contents.addImage(widget, context, x, y, selection, targetType, time, self.maps)



    #########################################################################################################################################
    #                                                                   #
    #                                Create Double Map View Page                        #   
    #                                   (self.doubleViewHBox)                           #
    #                                                                   #
    #########################################################################################################################################
    
    #This function is called when the View Maps page is created
    #It adds the two map view areas to the top of the page as well as the toolbar
    def addDoubleMapViewPage(self):
        
        
        
        #The first map area is created. 
        #A layout which contains the event box class is made
        self.doubleViewLayout0 = gtk.Layout()       
        
        

        #The event box is made
        self.doubleViewContent0 = self.LayoutContent(0.45, 0.4, self.doubleViewLayout0)

        #The layout and event box are shown
        self.doubleViewContent0.show()
        self.doubleViewLayout0.show()
    
        #The layout is set so that items can be dropped into it
        self.doubleViewLayout0.drag_dest_set(gtk.DEST_DEFAULT_ALL, [("", 0, 0)],gtk.gdk.ACTION_COPY)

        #When the layout recieves a map thumbnail it calls the function replaceImage
        self.doubleViewLayout0.connect("drag_data_received", self.replaceImage, self.doubleViewContent0)
        
        #The layout is put into a frame to seperate the two layouts
        self.viewFrame0 = gtk.Frame(None)
        self.viewFrame0.add(self.doubleViewLayout0)
    
        #Same as the code above except with a different layout
        self.doubleViewLayout1 = gtk.Layout()       
        self.doubleViewLayout1.drag_dest_set(gtk.DEST_DEFAULT_ALL, [("", 0, 0)],gtk.gdk.ACTION_COPY)
        self.doubleViewContent1 = self.LayoutContent(0.45, 0.4, self.doubleViewLayout1)
        self.doubleViewContent1.show()
        self.doubleViewLayout1.show()
        self.doubleViewLayout1.connect("drag_data_received", self.replaceImage, self.doubleViewContent1)    
        self.viewFrame1 = gtk.Frame(None)
        self.viewFrame1.add(self.doubleViewLayout1)


        #The layout frames are packed side by side in a horizontal box
        self.doubleViewHBox = gtk.HBox()
        self.doubleViewHBox.pack_start(self.viewFrame0, True, True, 5)
        self.doubleViewHBox.pack_start(self.viewFrame1, True, True, 5)
        
        #A new toolbar is created
        self.doubleViewToolbar = self.MapToolbar([self.doubleViewContent0, self.doubleViewContent1])
        
        #The toolbar and frames are packed in a vertical box, with the frames on top
        self.doubleViewVBox = gtk.VBox()
        self.doubleViewVBox.pack_start(self.doubleViewHBox, True, True, 5)
        self.doubleViewVBox.pack_end(self.doubleViewToolbar, False, False, 5)


    
    #This function is called when the View Maps page is created
    #It makes the thumbnail area    
    def addMapThumbnails(self):
        
        #The thumbnails are in a scrolled window with a horizontal scroll bar only.
        self.mapDisplayBar = gtk.ScrolledWindow()
        self.mapDisplayBar.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_NEVER)

        #A viewport is added to the scrolled window
        self.mapDisplayViewport = gtk.Viewport()
        self.mapDisplayBar.add(self.mapDisplayViewport)
        
        #A horizontal box is created and added to the viewport. 
        #The horizontal box must have a minimum height in order to stay consistent when there aren't any maps in the region
        self.hBox = gtk.HBox()
        self.hBox.set_size_request(0, int(self.windowHeight * self.mapThumbnailScalingY))
        self.mapDisplayViewport.add(self.hBox)
    
    #########################################################################################################################################
    #                                                                   #
    #                                Create View Maps Page                          #   
    #                                                                   #
    #########################################################################################################################################           
    
    #This function is called in the main code
    #It creates the View Maps Page
    def addMapDisplay(self):
        
        #Create the two regions
        self.addDoubleMapViewPage()
        self.addMapThumbnails()

        #Pack them inside a vertical box
        self.mapDisplayVBox = gtk.VBox()
        self.mapDisplayVBox.pack_start(self.doubleViewVBox, True, True, 2)
        self.mapDisplayVBox.pack_end(self.mapDisplayBar, False, False, 2)
        


    """-------------------------------------------------------------------------------------------------------------------------------------|
    |                                                                   |                               |
    |                                 View Data Page                            |
    |                                                                   |
    |           #########################################################################################           |
    |           #                                           #           |
    |           #                                           #           |
    |           #                                           #           |
    |           #                                           #           |
    |           #                                               #           |
    |           #                                           #           |
    |           #                                           #           |   
    |           #                                           #           |   
    |           #                                           #           |
    |           #                       1                   #           |   
    |           #                                           #           |           
    |           #                                           #           |
    |           #                                           #           |       
    |           #                                           #           |       
    |           #                                               #           |       
    |           #                                           #           |
    |           #                                           #           |               
    |           #                                           #           |       
    |           #                                           #           |       
    |           #                                           #           |           
    |           #                                           #           |   
    |           #                                           #           |               
    |           #                                               #           |               
    |           #                                           #           |               
    |           #                                           #           |   
    |           #                                           #           |   
    |           #                                           #           |       
    |           #########################################################################################           |   
    |                                                                   |
    |                                                                   |
    --------------------------------------------------------------------------------------------------------------------------------------"""


    #########################################################################################################################################
    #                                  Function                                 #
    #                                      viewData                             #   
    #                                                                   #
    #########################################################################################################################################   

    #This function is called when the View Data button is clicked from the Create Maps page
    #It loads all the data currently selected into a table style view
    def viewData(self, widget, Data=None):  
        
        #Check to see if there is a field currently selected 
        if self.ClimateData.dataIndex != None:
            
            #Copy data for clarity
            Data = self.ClimateData.DataSet
            i = self.ClimateData.dataIndex
            tIndex = self.ClimateData.currentTValue[1]
            viewingData = Data[i].subspace[:, self.ClimateData.MinimumZ[1]:self.ClimateData.MaximumZ[1]+1,
                               self.ClimateData.MinimumY[1]:self.ClimateData.MaximumY[1]+1, 
                                                       self.ClimateData.MinimumX[1]:self.ClimateData.MaximumX[1]+1]

            #If the data is not two dimensional, creates an error message and return from the function
            if viewingData.shape.count(1) != 2:
                self.addErrorMessage("Error - Data is not 2 dimensional")
                return None
            
            #Initialise axes variables              
            xAxis = None
            yAxis = None
            
            
            #This loop finds the first dimension with a length greater than 1 and stores in the xAxis, and the second to the yAxis
            #The viewingData.shape is reversed because by default the order is [t, z, y, x] which is the reverse of what is needed
            #This code allows the user to view Y vs Z data or X vs Z data as well as X vs Y data
    
            index = 0
            for x in reversed(viewingData.shape):
                if x > 1:
                    if xAxis == None:
                        xAxis =  index
                    else:
                        yAxis = index
                index += 1               

            #Create a list of maximum and minimums so that they can easily be indexed.      
            maxmins = [[self.ClimateData.MinimumX, self.ClimateData.MaximumX],
                                   [self.ClimateData.MinimumY, self.ClimateData.MaximumY], 
                                   [self.ClimateData.MinimumZ, self.ClimateData.MaximumZ]]
                
            #Set the length of the x axis(the number of columns in the table) to be the maximum index - the minimum index + 1
            # +1 is needed because the indexes are inclusive
            xAxisLength = maxmins[xAxis][1][1] - maxmins[xAxis][0][1] + 1

            #Remove the previous table and re-create it with the proper size
            self.viewDataXViewport.remove(self.viewDataXTable)  
            self.viewDataXTable = gtk.Table( 1 , xAxisLength)
        
            #Set the column spacings for clarity
            self.viewDataXTable.set_col_spacings(20)

            #Loops for each column in the table
            for i in range(xAxisLength):
                #Adds a label with the data piece in the position i + Minimum. 
                # + Minimum is needed because i starts from 0 and goes to the length of the array
                # instead of from the minimum index to the maximum index
                newLabel = gtk.Label(str(self.ClimateData.xyztArrays[xAxis][i + maxmins[xAxis][0][1]]))
                
                #Set the width of the label
                newLabel.set_width_chars(15)
            
                #Attach the label to the table
                self.viewDataXTable.attach(newLabel, i, i+1, 0, 1)

                #Show the label
                newLabel.show()

            #Add the table back to the viewport and show both items
            self.viewDataXViewport.add(self.viewDataXTable)
            self.viewDataXTable.show()
            self.viewDataXViewport.show()
        
        
            #Similar to the code above, but with the y axis instead
            yAxisLength = maxmins[yAxis][1][1] - maxmins[yAxis][0][1] + 1
            self.viewDataYViewport.remove(self.viewDataYTable)  
            self.viewDataYTable = gtk.Table(yAxisLength, 1)
            self.viewDataYTable.set_row_spacings(20)
            for i in range(yAxisLength):
                newLabel = gtk.Label(str(self.ClimateData.xyztArrays[yAxis][i + maxmins[yAxis][0][1]]))
                newLabel.set_width_chars(15)
                self.viewDataYTable.attach(newLabel, 0, 1, i, i+1)
                newLabel.show()
            
            self.viewDataYViewport.add(self.viewDataYTable)
            self.viewDataYTable.show()
            self.viewDataYViewport.show()


            #List to get position of data in array
            position = [0, 0, 0, 0]
        
            #Remove the table from the viewport and recreate it
            self.viewDataViewport.remove(self.viewDataTable)    
            self.viewDataTable = gtk.Table(yAxisLength, xAxisLength)
            
            #Set the spacings for clarity
            self.viewDataTable.set_row_spacings(20)
            self.viewDataTable.set_col_spacings(20)
        
            #Loops every column and row in the table
            for i in range(xAxisLength):
                for j in range(yAxisLength):
                    #3-xAxis is the position of the dimension that the xAxis contains
                    #Same for y axis
                    position[3-xAxis] = i
                    position[3-yAxis] = j
    
                    #Create a label with the data. 
                    #The minimums to not need to be added since viewingData already removed the data which is not needed 
                    newLabel = gtk.Label(str(viewingData.array[position[0], position[1], position[2], position[3]]))

                    #Set label width
                    newLabel.set_width_chars(15)

                    #If the mouse enters the labels area run the function viewXY. (DOES NOT WORK)
                    #To Do: FIX
                    newLabel.connect("motion-notify-event", self.viewXY, i, j)
                
                    #Attach label to table and show it
                    self.viewDataTable.attach(newLabel, i, i+1, j, j+1)
                    newLabel.show()

            #Add the table back to the viewport and show both items
            self.viewDataViewport.add(self.viewDataTable)
            self.viewDataTable.show()
            self.viewDataViewport.show()


    #########################################################################################################################################
    #                                                                   #
    #                                      Functions                                #   
    #                                                                   #
    #########################################################################################################################################
    
    #This function is called when the mouse enters a new label in the table of labels
    #ToDo : Display the data, the x axis value and the y axis value of the label being hovered over
    def viewXY (self, widget, s, i, j):
        pass
    
    #This function is called when the user scrolls the data viewport
    #It copies the scrolling adjustment to the respective x or y axis so that scrolling the data will scroll the axes as well.
    def scrolled(self, widget, widgetToChange):
        widgetToChange.set_value(widget.get_value())    


    #########################################################################################################################################
    #                                                                   #
    #                                Create View Data Page                          #   
    #                                                                   #
    #########################################################################################################################################



    #This function is called in the main code 
    #It adds the View Data page to the notebook.
    def addViewDataPage(self):  
        
            
        #Create a table to store the labels
        self.viewDataXTable = gtk.Table(1, 1, False)
        
        #Create a viewport to store the table
        self.viewDataXViewport = gtk.Viewport()
        
        #Store the adjustment of the viewport   
        self.viewDataXAdjustment = self.viewDataXViewport.get_hadjustment()

        #Set the viewports minimum size, so it stays consistent when data is added to the page.
        self.viewDataXViewport.set_size_request(100,50)
        
        #Add table to the viewport
        self.viewDataXViewport.add(self.viewDataXTable)
        
        
        #Similar to code above, but with the Y Axis
        self.viewDataYTable = gtk.Table(1, 1, False)
        self.viewDataYViewport = gtk.Viewport()
        self.viewDataYViewport.set_size_request(100,50) 
        self.viewDataYAdjustment = self.viewDataYViewport.get_vadjustment()
        self.viewDataYViewport.add(self.viewDataYTable)
        
        
        #A scrolled window is needed for the user to be able to look through the data
        #The viewport is added to this scrolled window      
        self.viewDataWindow = gtk.ScrolledWindow()
        self.viewDataTable = gtk.Table(1, 1, False)     
        self.viewDataViewport = gtk.Viewport()      
        self.viewDataHAdjustment = self.viewDataWindow.get_hadjustment()
        self.viewDataVAdjustment = self.viewDataWindow.get_vadjustment()
        self.viewDataWindow.add(self.viewDataViewport)
        self.viewDataViewport.add(self.viewDataTable)


        #If the scrolled window is scrolled, copy the scrolling to the other viewports
        #This makes the row and column titles an overlay
        self.viewDataHAdjustment.connect("value-changed", self.scrolled, self.viewDataXAdjustment)  
        self.viewDataVAdjustment.connect("value-changed", self.scrolled, self.viewDataYAdjustment)
        
        
        
        #Create a table to store all the viewports and scrolled window
        self.viewDataMainTable = gtk.Table(2, 2, False)
        self.viewDataMainTable.attach(self.viewDataXViewport, 1, 2, 0, 1, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL)
        self.viewDataMainTable.attach(self.viewDataYViewport, 0, 1, 1, 2, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL)
        self.viewDataMainTable.attach(self.viewDataWindow, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL)


        
        
        
        

    """-------------------------------------------------------------------------------------------------------------------------------------|
    |                                                                   |
    |                                                                   |
    |                                                                   |                               |
    |                                 Create Interface                          |           
    |                                                                   |                               
    |                                                                   |
    |                                                                   |
    --------------------------------------------------------------------------------------------------------------------------------------"""
        
    def __init__(self):
        
        #Initalise variables, CFData and the window properties
        self.setWindowProperties()
        self.initialiseVariables()
        self.ClimateData = CFData()     
        

        #Add a vertical box to store the menu bar and notebook and add to window
        self.VerticalBox = gtk.VBox(False,0)
        self.window.add(self.VerticalBox)   
    
        #Create all regions of the interface
        self.addMenu()  
        self.addCreateMapsPage()
        self.addMapDisplay()
        self.addViewDataPage()
        
        #Create the notebook and add all the pages
        self.selectionNotebook = gtk.Notebook()
        self.selectionNotebook.set_tab_pos(gtk.POS_BOTTOM)

        self.selectionNotebook.append_page(self.CreateMapsVBox, gtk.Label('Create Maps'))       
        self.selectionNotebook.append_page(self.mapDisplayVBox, gtk.Label('View Maps'))         
        self.selectionNotebook.append_page(self.viewDataMainTable, gtk.Label('View Data'))

        #Add the menu bar and the notebook to the main box
        self.VerticalBox.pack_start(self.menuBar, False, False, 2)      
        self.VerticalBox.pack_start(self.selectionNotebook, True, True, 2)
                    
        #Show all objects
        self.window.show_all()
        
    def main(self):
        gtk.main()

if __name__ == "__main__":
    CF = Interface()
    CF.main()
