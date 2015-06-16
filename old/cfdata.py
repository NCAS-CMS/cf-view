import cf

class CFData:
    
    ''' Provides the interface to the data '''

    def __init__(self):
        ''' Initialise without the data interface without arguments '''
        
        #DataSet is a store of the whole file; uses a lot of memory however is quicker than accessing data by re-reading the file
        self.DataSet = []

        #fieldDataSet is the list of field names
        self.fieldDataSet = []

        #dataIndex is the index of the field selected.
        self.dataIndex = None

        #Maximums and Minimums store [value,index]
        self.MaximumX = [None, None]
        self.MinimumX = [None, None]
        
        self.MaximumY = [None, None]
        self.MinimumY = [None, None]
        
        self.MinimumZ = [None, None]
        self.MaximumZ = [None, None]
        
        # Only single Ts can be plotted 
        # so a maximum and minimum is not needed
        self.currentTValue = [0,0]

        # The common interval in the array.
        self.xInterval = None
        self.yInterval = None
        self.zInterval = None
    
        # The unit and name of each variable, e.g. 
        # (For X, the name may be Longitude and the unit is Degrees )
        self.variableNames = []
        self.unitNames = []

    def readDataSet(self, fileName):
        '''Opens, reads, and stores attributes of filename into DataSet '''
        self.DataSet = cf.read(fileName)

    def getFieldNames(self):
        ''' Parse the data from the fileand retrieves the long names and the 
        length of the arrays. The data retrieved is stored in order: 
        Index - Field Name - Number of X Values - Number of Y Values - 
        Number of Z Values - Number of T Values '''
            
        # The index is created so that data from the DataSet can easily be found.       
        index = 0

        for DataPiece in self.DataSet:          
            
            # Dim3 is the X Data, Dim2 is the Y Data, Dim1 is the Z Data and 
            # Dim0 is the T Data

            self.fieldDataSet.append([index, DataPiece.long_name, 
                                len(DataPiece.item('dim3').array), 
                                len(DataPiece.item('dim2').array), 
                                len(DataPiece.item('dim1').array) , 
                                len(DataPiece.item('dim0').array)])
            index += 1
            
    def getXYZT(self):
        
        ''' Called when the selected field changes and the XYZT values need to 
        be retrieved/changed. '''

        def findInterval (array):
            ''' Internal funciton to find the common interval in the argument
            array. If there isn't a common interval, return None '''
            # FIXME_BNL: Need to consider whether there is more cf'ish way to do this.
            interval = None
            previousInterval = None
            valid = True
            for index in range(len(array)-1):
                interval = array[index+1] - array[index]
                if interval != previousInterval and previousInterval != None:
                    valid = False
                previousInterval = interval
                
            if valid == True:
                return interval
        
        #The variable names are retrieved from the data. 
        self.variableNames = [  self.DataSet[self.dataIndex].item('dim3').ncvar, 
                                self.DataSet[self.dataIndex].item('dim2').ncvar, 
                                self.DataSet[self.dataIndex].item('dim1').ncvar, 
                                self.DataSet[self.dataIndex].item('dim0').ncvar  ]  
        
        #The unit names are also retrieved.
        self.unitNames = [  self.DataSet[self.dataIndex].item('dim3').units,
                            self.DataSet[self.dataIndex].item('dim2').units, 
                            self.DataSet[self.dataIndex].item('dim1').units, 
                            self.DataSet[self.dataIndex].item('dim0').units  ]
        
        #The arrays of each variable are stored.
        self.xArray = self.DataSet[self.dataIndex].item('dim3').array
        self.yArray = self.DataSet[self.dataIndex].item('dim2').array
        self.zArray = self.DataSet[self.dataIndex].item('dim1').array
        self.tArray = self.DataSet[self.dataIndex].item('dim0').array
        
        #These are put into a list so that they can be more easily used.
        self.xyztArrays = [self.xArray, self.yArray, self.zArray, self.tArray]
        
        ###The default values are set:

        #The default for X includes all the values in its array
        self.MaximumX = [self.xArray[len(self.xArray) - 1], len(self.xArray) -1]
        self.MinimumX = [self.xArray[0], 0]
        self.xInterval = findInterval(self.xArray)
        
        #The default for Y includes all the values in its array
        self.MinimumY = [self.yArray[0], 0]
        self.MaximumY = [self.yArray[len(self.yArray) - 1], len(self.yArray) -1]
        self.yInterval = findInterval(self.yArray)
        
        #The default for Z contains the first value in its array
        self.MinimumZ = [self.xArray[0], 0]
        self.MaximumZ = self.MinimumZ
        self.zInterval = findInterval(self.zArray)
        
        #The default for T contains the first value in its array
        self.currentTValue = [self.tArray[0], 0]
