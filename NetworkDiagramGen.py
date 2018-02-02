###Diagram Generation Script from databse###
#Dependecy's that must be installed with pip: networkx matplot jgraph pydot pydot-ng

###GRAPHING Setup###
import networkx as nx
import matplotlib.pyplot as plt
from jgraph import *

#####Fix graphviz bug on windows where graphviz is often not in the PATH#######
import platform
OS = platform.platform()
if "Windows" in OS:
    import os
    os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
    print("PATH fix has been done")
else:
    print("PATH fix was not ran")

####SETTINGS####
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
        print("{0} was not found or an error occured using settings! Fix the location in the script or read error".format(
            SettingsFile))

G = nx.DiGraph()


####Read data using script ######
from ReadDatabase import UsableData

#print(UsableData)
HostnameIndex=2
LocalIPIndex=3
GatewayIPIndex=4
PublicIPIndex=5
for i in range(int(len(UsableData)/6)):
    SystemHostname = UsableData[HostnameIndex]
    SystemLocalIP = UsableData[LocalIPIndex]
    SystemGatewayIP = UsableData[GatewayIPIndex]
    SystemPublicIP = UsableData[PublicIPIndex]

    HostnameIndex+=6
    LocalIPIndex+=6
    GatewayIPIndex+=6
    PublicIPIndex+=6
    print("Public IP: {0} to Gateway: {1}  to hostname: {2} (Local IP: {3})".format(SystemPublicIP,SystemGatewayIP,SystemHostname,SystemLocalIP))
    G.add_edges_from([("Public IP\n{0}".format(SystemPublicIP),"Gateway\n{0}".format(SystemGatewayIP)),("Gateway\n{0}".format(SystemGatewayIP),"{0}\n{1}".format(SystemHostname, SystemLocalIP))])

###PLT always seems to make the horizontal axis too small, this adds the extra length needs to make eveything fix on the graph:
GraphSize = plt.rcParams["figure.figsize"]
print("Default Graph Size was {0} vertical and {1} horizontal".format(GraphSize[1], GraphSize[0]))
GraphSize[0]=GraphSize[0]+5
print("New Graph Size is {0} vertical and {1} horizontal".format(GraphSize[1], GraphSize[0]))
print(GraphSize)
print("Graph generated")
plt.rcParams["figure.figsize"] = GraphSize

print("\n")
print(nx.info(G))
#plt.title('Network Graph')
pos=nx.nx_pydot.graphviz_layout(G, prog='dot') #k=0.015, iterations=1
nx.draw(G, pos, with_labels=True, arrows=False,node_shape='s',node_size=3500,node_color='white',linewidths='0')
#plt.tight_layout()
plt.savefig(GetSetting("GraphLocation"), format="png", figsize=(200,200))
#plt.show()
