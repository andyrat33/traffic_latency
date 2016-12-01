#Version 3
import matplotlib.pyplot as plt
import csv
import argparse
from json import dump, load


# cmd options 
# print uni flow
# select uni_flow to graph defaul graph all
# auto save dict
# reload dict

parser = argparse.ArgumentParser()

parser = argparse.ArgumentParser(description="plot a graph showing the latency in tcp streams")
group = parser.add_mutually_exclusive_group()

group.add_argument("-l", "--load", dest="loadFile", help="load a saved set of flows", metavar="FILE")
group.add_argument("-f", "--file", dest="filename", help="wireshark csv file", metavar="FILE")
parser.add_argument("-p", "--print", dest="dataprint", action="store_true", help="print unidirectional flow tuples")
parser.add_argument("-g", "--graph", nargs = '*', dest="flowToGraph", help="select the flow to graph, use -p to print flows", metavar="FLOW")
args = parser.parse_args()


counter2 = 0

def rTraffic(filename):
    """open csv export from wireshark and parse to a uni_flow list with collected latency. Return counter & dict tuple"""
    #  order of fields
    sTraffic = [
    "No.",
    "Time",
    "Source",
    "SPort",
    "Destination",
    "DPort",
    "Protocol",
    "Length",
    "Time since previous frame in this TCP stream",
    "Info"
    ]    
    f = {field:i for i,field in enumerate(sTraffic)}
    data = dict()
    top=True
    
    counter = 0    
    with open(filename, mode='rb') as pcap:
        wline = csv.reader(pcap, delimiter=',')
        for row in wline:
            if top:
                top=False
                if sTraffic != row:
                    print "Wireshark CSV Export should have this structure"
                    print ', '.join(sTraffic)
                    exit()
    
                continue
            if not str((row[f["Source"]],row[f["SPort"]],row[f["Destination"]],row[f["DPort"]])) in data and float(row[f["Time since previous frame in this TCP stream"]]) != 0.0:
                data[str((row[f["Source"]],row[f["SPort"]],row[f["Destination"]],row[f["DPort"]]))] = [float(row[f["Time since previous frame in this TCP stream"]])]
                counter += 1
            elif float(row[f["Time since previous frame in this TCP stream"]]) != 0.0:
                data[str((row[f["Source"]],row[f["SPort"]],row[f["Destination"]],row[f["DPort"]]))].append(float(row[f["Time since previous frame in this TCP stream"]]))
                counter += 1
    return (counter, data)

def saveFlow(filename,flowData):
    filename = filename.split('.')[0]+'.json'
    with open(filename, mode='wb') as saveFlowData:
        dump(flowData, saveFlowData)

def loadFile(jsonFile=args.loadFile):
    with open(jsonFile) as loadFlow:
        return load(loadFlow)

def printFlows():
    for xe, ye in fData.iteritems():
        print xe,ye    

def graphFlows(listOfFlows=args.flowToGraph):
    pass


if args.loadFile:
    fData = loadFile()
    if args.dataprint:
        printFlows()
        exit()
else:    
    numOfFlows, fData = rTraffic(args.filename)
    saveFlow(args.filename,fData)
    if args.dataprint:
        printFlows()
        exit()    

for xe, ye in fData.iteritems():
    plt.scatter(range(len(ye)), ye)
    
    

#print "The total number of uni-directional conversations plotted is ", len(data)
#print "The total number of x values plotted is ", numOfFlows

plt.ylabel('Latency')
plt.xlabel('Samples')
plt.axis(ymax=1)
plt.show()
