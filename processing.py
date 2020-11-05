import os
import json
import re
import sys

## Get the matched config file
def getJson(hdaFile):
    jsonFile = hdaFile.replace('.hda', '.json')
    return jsonFile

## Parse the HDA file to get the parms and then save it into disk as json
def parse(fileName):

    # regex pattern
    regexKey = r'\s+?(\w+)\s+?'
    regexValue = r'\w+?\s+(.*)\s'
    
    patternKey = re.compile(regexKey)
    patternValue = re.compile(regexValue)

    # open the hda as binary and then use regex to parse it
    file = open(fileName, "rb")

    # Try a new algrithm to parse the hda file
    line = file.readline().decode(errors='replace')
    parmJson = []
    parmDict = {}
    flag = False
    while line is not None:
        
        # When meet the } it indicate it is the end of parm segment
        # So we should pop the parmDict and append it to our json stream
        if "    }" in line:
            flag = False

            if parmDict:
                parmJson.append(parmDict)
            parmDict = {}

        # When the flag is true, we will filter the line and using regex to detect it
        # A proper parm line should have a key and a value
        if flag:
            lineFilter = line.replace('\n',' ').replace('{',' ').replace('}',' ').replace('"',' ')
            parmKey = re.search(patternKey, lineFilter)
            parmValue = re.search(patternValue, lineFilter)
            if parmKey and parmValue:
                # In HDA some parms have the same name, which will not acceptable in Dict
                # So we add some counts to make every parm name unique
                counts = 0
                if parmKey.group(1) in parmDict:
                    counts += 1 
                    parmDict[parmKey.group(1) + (str(counts))] = parmValue.group(1).strip()
                else:
                    parmDict[parmKey.group(1)] = parmValue.group(1).strip()
            else:
                # When the line is not proper, we should clear the dict and stop reading this segment
                flag = False
                counts = 0
                parmDict = {}

        ## When we meet the 'parm {' it indicate the beginning of a parm segment
        if "    parm {" in line:
            flag = True

        line = file.readline().decode(errors='replace')

        ## We can break earlier when meet some special words
        if "Automatically generated script" in line:
            break


    file.close()
    outputFile = getJson(fileName)
    with open(outputFile, 'w+') as output:
        json.dump(parmJson, output, indent = 4)


if __name__ == "__main__":
    parse(sys.argv[1])