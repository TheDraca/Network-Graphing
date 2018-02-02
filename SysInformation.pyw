###SystemInfomation Garthering Script###
##Import neeed modules for info and windows##
from tkinter import *
import getpass
import socket
import requests
import os
import platform
import sqlite3


OS = platform.platform() #OS Version is needed regardless as it determinds how the NetworkDiagramGen is ran

##Variable setup##
LabelNum = 0  # Starting Number of labels, used for the CreateLabel Function
ButtonNum = 0  # Starting number of buttons, used for CreateButton function
InfoList = ["Hostname", "OS Version", "Username", "Local IP","Gateway IP", "Public IP"]  # List of info to collect
InfoCount = len(InfoList)
tablelist = []

###Settings File####
SettingsFile = "Settings.cfg"  # Location of settings file to be used

######

def GetSetting(Option, File=SettingsFile):
    try:
        with open(File) as Settings:
            for line in Settings:
                if Option in line:
                    SettingResult = line.split("=", 1)[1]
                    SettingResult = SettingResult.rstrip()
                    return SettingResult
    except:
        NoSettingsFile = window()
        CreateLabel(NoSettingsFile, "{0} was not found or an error occured using settings! Fix the location in the script or read error".format(SettingsFile), 1, 0, NW)
database = sqlite3.connect(GetSetting("DatabaseLocation"))
cursor = database.cursor()


##Open database and tables + create if it doesn't exist###

def CreateTable(cursor, TableName, ColumnName, Rowproperties, add=True):
    IDproperties = "{0}_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE".format(TableName)
    cursor.execute("""CREATE TABLE IF NOT EXISTS {0} ({1}, {2} {3})""".format(TableName, IDproperties, ColumnName, Rowproperties))
    if add:
        tablelist.append((TableName, ColumnName))


def SetupDatabase(cursor):
    CreateTable(cursor, "HOSTNAMES", "hostname", "varchar(63)")
    CreateTable(cursor, "OSVERSIONS", "osversion", "varchar(255)")
    CreateTable(cursor, "USERNAMES", "username", "varchar(255)")
    CreateTable(cursor, "LOCALIPS", "localip", "varchar(15)")
    CreateTable(cursor, "GATEWAYIPS", "gatewayip", "varchar(15)")
    CreateTable(cursor, "PUBLICIPS", "publicip", "varchar(15)")
    CreateTable(cursor, "SYSTEMS", "username_id","INTEGER, osversion_id INTEGER, hostname_id INTEGER, localip_id INTEGER, gatewayip_id INTEGER, publicip_id INTEGER", False)


def AddToDatabase(cursor, ReportedInfo):
    ExistCount = 0
    #ExistingInfo = []
    data = {}
    for index, value in enumerate(ReportedInfo):
        Exists = False
        print("\nLoop start Exists = {0}".format(Exists))
        cursor.execute("""SELECT {0} FROM {1} """.format(tablelist[index][1], tablelist[index][0]))
        result = cursor.fetchall()
        print("Result: " + str(result))
        for row in result:
            print("\nRow: " + str(row[0]))
            if value == row[0]:
                Exists = True
                print(Exists)
                break
            else:
                Exists = False
                print("Does not exists!")

        if Exists == False:
            print("New data, adding to database!")
            cursor.execute("""INSERT INTO {0} ('{1}') VALUES ('{2}')""".format(tablelist[index][0], tablelist[index][1], value))

            #Add to SYSTEMS table#
            dataid = cursor.execute("""SELECT last_insert_rowid()""").fetchall()
            idcolumn = "{0}_id".format(tablelist[index][1])
            print(idcolumn)

            data[idcolumn] = str(dataid[0][0])
            print(Exists)
        else:
            print("Didn't add data into tables as it is in database")
            ExistCount += 1
            idcolumn = "{0}S_id".format(tablelist[index][1].upper())
            print("IDCOLUMN {0}".format(idcolumn))
            value = cursor.execute("""SELECT * FROM {0}S """.format(tablelist[index][1].upper())).fetchall()
            print(value)
            for row2 in value:
                rowId, dataValue = row2
                print("Row2 id is: " + str(rowId))
                print(dataValue)
                if dataValue == row[0]:
                    idinput=rowId
            data["{0}_id".format(tablelist[index][1])] = str(idinput)
            print(Exists)
    print(data)

    if ExistCount < InfoCount:
        print("Some new data was found, adding new system to system table")
        cursor.execute("""INSERT INTO SYSTEMS ('{0}') VALUES ('{1}')""".format("','".join(data.keys()), "','".join(data.values())))
        ##Success Window##
        DataAddedWindow=dialogwindow()
        CreateLabel(DataAddedWindow, "System has been added", 1, 0, NW)
    else:
        print("All data already Existed!")
        DataExistedWindow=dialogwindow()
        CreateLabel(DataExistedWindow,"This system already exists in database!!", 1, 0, NW)

##Button Functions##


def AddRecord():  # Add Information to database
    ReportedInfo = GetInfo()
    print("Record stuff:")
    print(ReportedInfo)
    database = sqlite3.connect(GetSetting("DatabaseLocation"))
    cursor = database.cursor()
    SetupDatabase(cursor)
    AddToDatabase(cursor, ReportedInfo)
    database.commit()
    database.close()


def SearchIPConfig(IPConfigSearchTerm):
    IPConfigResults = os.popen("ipconfig | findstr /i {0}".format(IPConfigSearchTerm)).read()
    ResultsString = IPConfigResults.split(": ")[1]
    ResultsString = ResultsString.split("\n")[0]
    print(ResultsString)
    return ResultsString


def GetInfo():
    hostname = socket.gethostname()
    OS = platform.platform()
    username = getpass.getuser()

    ##Gateway IP collection is OS specfic!
    if "Windows" in OS:
        IPaddr = str(SearchIPConfig("IP"))
        GatewayIP = str(SearchIPConfig("Gateway"))
    else:
        IPaddr = str(os.popen("ip route show | grep 'src' | awk '{print $9}'").read().split("\n")[0])
        GatewayIP = str(os.popen("ip route show | grep 'default' | awk '{print $3}'").read().split("\n")[0])

    PIPaddr = requests.get('http://api.ipify.org').text
    print("Info Collected")
    ReportedInfo = [hostname, OS, username, IPaddr, GatewayIP, PIPaddr]
    return ReportedInfo



###### VIEW EXISTING DATA FUNCTION ########
def ViewData():
    ViewDataWindow=window()
    #DataScrollbar = Scrollbar(ViewDataWindow)
    #DataScrollbar.grid(row=3, column=1, sticky=NS)
    from ReadDatabase import UsableData
    #CreateLabel(ViewDataWindow,"Hostname            Local IP    Gateway     Public IP   OS Version  Added by",2,0,W)
    StartRow = 3
    UsernameIndex=0
    OSVersionIndex=1
    HostnameIndex=2
    LocalIPIndex=3
    GatewayIPIndex=4
    PublicIPIndex=5
    for i in range(int(len(UsableData)/6)):
        SystemUsername = UsableData[UsernameIndex]
        SystemOSVersion = UsableData[OSVersionIndex]
        SystemHostname = UsableData[HostnameIndex]
        SystemLocalIP = UsableData[LocalIPIndex]
        SystemGatewayIP = UsableData[GatewayIPIndex]
        SystemPublicIP = UsableData[PublicIPIndex]
        UsernameIndex+=6
        OSVersionIndex+=6
        HostnameIndex+=6
        LocalIPIndex+=6
        GatewayIPIndex+=6
        PublicIPIndex+=6
        
        System="Hostname: {0}   Local IP: {1}   Gateway: {2}    Public IP: {3}  OS Version: {4}     Added By User: {5}".format(SystemHostname,SystemLocalIP,SystemGatewayIP,SystemPublicIP,SystemOSVersion,SystemUsername)
        print(System)
        CreateLabel(ViewDataWindow,System,StartRow,0,W)
        StartRow+=1

    CreateButton(ViewDataWindow, "Refresh", lambda:reload(ViewDataWindow),StartRow +1,0,W)

def reload(ViewDataWindow):
    ViewDataWindow.destroy()
    ViewData()


###Creating base window class##
class window(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("System Info Script")
        if "Windows" not in OS:
            self.attributes('-type', 'dialog') #Makes the applications windows free floating for certian unix window managers that like to force full screen windows
        self.label()
        self.button()

    def label(self):
        L0 = Label(self, text="System Info Collector V1")
        L0.grid(row=0, column=0, sticky=N)

    def button(self):
        B0 = Button(self, text="Close", command=self.destroy)
        B0.grid(row=0, column=0, sticky=NE)

class dialogwindow(window):
    def __init__(self):
        super(dialogwindow, self).__init__()
        self.title("System Info Alert")
        self.button()

    def button(self):
        B0 = Button(self, text="Close", command=self.destroy)
        B0.grid(row=2, column=0, sticky=N)



##Functions to speed up creation of objects##

def CreateLabel(WindowName, Text, Row, Column, Sticky, LabelNo=LabelNum):
    LabelNo += 1
    exec("L{0} = Label(WindowName, text=Text)".format(LabelNum))
    exec("L{0}.grid(row=Row, column=Column, sticky=Sticky)".format(LabelNum))


def CreateButton(WindowName, Text, Command, Row, Column, Sticky, ButtonNo=ButtonNum):
    ButtonNo += 1
    exec("B{0} = Button(WindowName, text=Text, command=Command)".format(ButtonNum))
    exec("B{0}.grid(row=Row, column=Column, sticky=Sticky)".format(ButtonNum))


##Main Window##

def GraphGen():
    from time import sleep
    print("Loading NetworkDiagramGen")
    CurrentLocation='"{0}"'.format(os.getcwd())
    #print(CurrentLocation)
    os.popen("python {0}/NetworkDiagramGen.py".format(CurrentLocation))
    #sleep(1)
    print(os.path.isfile(GetSetting("GraphLocation")))
    while True:
        if os.path.isfile(GetSetting("GraphLocation")) == True:
            break
        else:
            sleep(1)
            loopcount += 1
            if loopcount == 6:
                print("He's dead jim")
                break
            else:
                pass
    try:
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        plt.title(GetSetting("GraphLocation"))
        graph = plt.imshow(mpimg.imread(GetSetting("GraphLocation")))
        cur_axes = plt.gca()
        cur_axes.axes.get_xaxis().set_visible(False)
        cur_axes.axes.get_yaxis().set_visible(False)
        plt.show(graph)
    except:
        print("DOUH")
        ErrorWindow=dialogwindow()
        CreateLabel(ErrorWindow, "ERROR, most likely missing dependecies (matplotlib/graphviz), install dependecies or run generator on configured system", 1, 0, N)


MainWindow = window()

CreateLabel(MainWindow, "The Following Info will be stored in the database ({0}):".format(GetSetting("DatabaseLocation")), 1, 0, NW)

ReportedInfo = GetInfo()
i = 0  # Starting item from InfoList list
Item = ""  # Start of info list
StartRow = 3
for I in ReportedInfo:
    Name = InfoList[i]
    Item = u"\u2022 {0}: {1}".format(Name, I)  # Add record to the list
    CreateLabel(MainWindow, Item, StartRow, 0, NW)
    i += 1
    StartRow += 1



CreateButton(MainWindow, "Add System to record",AddRecord, StartRow + 2, 0, N+S+E+W)
CreateButton(MainWindow, "View existing systems",lambda: ViewData(), StartRow + 1, 0, NW)
CreateButton(MainWindow, "Run Graph Generation", lambda: GraphGen(),StartRow +1, 0, NE,)

###DEBUG COMMENT OUT WHEN DONE###
##
# def debug_DeleteDatabase():
# os.remove(GetSetting("DatabaseLocation"))
##    print("debug_DeleteDatabase finshed")
##
##CreateButton(MainWindow, "RM DB", debug_DeleteDatabase, StartRow + 1, 0, N)
##
##########

MainWindow.mainloop()
