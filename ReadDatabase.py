import sqlite3

SettingsFile = "Settings.cfg"  # Location of settings file to be used
def GetSetting(Option, File=SettingsFile):
    try:
        with open(File) as Settings:
            for line in Settings:
                if Option in line:
                    SettingResult = line.split("=", 1)[1]
                    SettingResult = SettingResult.rstrip()
                    return SettingResult
    except:
        print("{0} was not found or an error occured using its settings! Fix the issue/location (or create a new one using the defaults commented out in this script) before continueing".format(SettingsFile))

database = sqlite3.connect(GetSetting("DatabaseLocation"))
cursor = database.cursor()
###################################################
CollectedData=[]
def GetData(TableName):
    cursor.execute("""SELECT {0}.* FROM SYSTEMS INNER JOIN {0} ON SYSTEMS.{1}_id = {0}.{0}_id""".format(TableName, TableName[:-1].lower()))
    return cursor.fetchall()

def GetValues(TableNames):
    for i in TableNames:
        TableName = i
        for pair in GetData(TableName):
            Value = str(pair).split("'", 1)[1].split("'",1)[0]
            print(Value)
            CollectedData.append(Value)


TableNames = ["USERNAMES","OSVERSIONS","HOSTNAMES","LOCALIPS","GATEWAYIPS","PUBLICIPS"]
GetValues(TableNames)

#print(UsableData)
#for i in UsableData:
#    int(len(UsableData)/6)

#UsableData[:int(len(UsableData)/6)]
#UsableData[6:12]
print("\n\n\n")
def SortData(CollectedData=CollectedData):
    Start=0
    UsableData=[]
    NumberOfSystems = int(len(CollectedData)/6)
    for i in range(NumberOfSystems):
        #SystemUsername=CollectedData[Start]
        #SystemOSVer=CollectedData[Start+NumberOfSystems]
        #SystemHostname=CollectedData[Start+NumberOfSystems*2]
        #SystemLocalIP=CollectedData[Start+NumberOfSystems*3]
        #SystemGatewayIP=CollectedData[Start+NumberOfSystems*4]
        #SystemPublicIP=CollectedData[Start+NumberOfSystems*5]

        UsableData.append(CollectedData[Start]) #AddUsernames
        UsableData.append(CollectedData[Start+NumberOfSystems]) #Add OS Versions
        UsableData.append(CollectedData[Start+NumberOfSystems*2]) #Add Hostnames
        UsableData.append(CollectedData[Start+NumberOfSystems*3]) #Add LocalIPs
        UsableData.append(CollectedData[Start+NumberOfSystems*4]) #Add Gateways
        UsableData.append(CollectedData[Start+NumberOfSystems*5]) #Add PublicIps

        Start+=1
    return UsableData
UsableData = SortData()
print(UsableData)
database.close()
