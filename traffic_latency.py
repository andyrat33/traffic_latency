#Version 3
import matplotlib.pyplot as plt
import csv
import sys
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
group2 = parser.add_mutually_exclusive_group()
group.add_argument("-l", "--load", dest="loadFile", help="load a saved set of flows", metavar="JSON_FILE")
group.add_argument("-f", "--file", dest="filename", help="wireshark csv file", metavar="FILE")
group2.add_argument("-p", "--print", dest="dataprint", action="store_true", help="print unidirectional flow tuples")
group2.add_argument("-g", "--graph", nargs = '*', type=int, dest="flowToGraph", help="select the flow to graph, use -p to print flows", metavar="FLOW")
args = parser.parse_args()


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
    # dict: f used to add offset to slice with as a word that identifies the field better
    data = dict()
    top=True
    
    counter = 0   
    try:
        pcap = open(filename, mode='rb')
    except IOError as e:
        print "Error: {}".format(e)
        sys.exit()
    else:
        with pcap:
            wline = csv.reader(pcap, delimiter=',')
            for row in wline:
                if top:
                    top=False
                    if sTraffic != row:
                        print "Wireshark CSV Export should have this structure"
                        print ', '.join(sTraffic)
                        sys.exit()
        
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
    try:
        saveFlowData = open(filename, mode='wb')
    except IOError as e:
        print "Error: {}".format(e)
        sys.exit()
    else:
        with saveFlowData:
            dump(flowData, saveFlowData)
    

def loadFile(jsonFile=args.loadFile):
    try:
        loadFlow = open(jsonFile)
    except IOError as e:
        print "Error: {}".format(e)
        sys.exit()
    else:
        with loadFlow:
            return load(loadFlow)
    

def printFlows(pfData, display=True):
    lookup = {}
    for index, key in enumerate(pfData.keys()):
        if display: print index, key
        lookup[int(index)] = key
    return lookup

def graphFlows(listOfFlows,gData):
    keysToGraph = printFlows(gData, display=False)
    nData = {}
    for f in listOfFlows:
        try:
            nData[keysToGraph[f]] = gData[keysToGraph[f]]
        except KeyError as e:
            print "FLOW {} not found".format(e)
        
    return nData



if args.loadFile:
    fData = loadFile()
    
else:    
    numOfFlows, fData = rTraffic(args.filename)
    saveFlow(args.filename,fData)
    print "The total number of uni-directional conversations plotted is ", len(fData)
    print "The total number of x values plotted is ", numOfFlows    

if args.dataprint:
    printFlows(fData)
    sys.exit()

if args.flowToGraph:
    fData = graphFlows(args.flowToGraph, fData)

if len(fData) > 0:
    for xe, ye in fData.iteritems():
        plt.scatter(range(len(ye)), ye)
    
    plt.ylabel('Latency')
    plt.xlabel('Samples')
    plt.axis(ymax=1)
    plt.show()
else:
    print "No data to graph"
