from elasticsearch import Elasticsearch
import pandas as pd
import json
import time
import logging
import datetime
import re
import sys
import os
import os.path
import GREY_FUNCTIONS



def main():
    #Input JSON  //Read in later//
    json_filename = sys.argv[1]
    whitelist_path = sys.argv[2]
    columns = GREY_FUNCTIONS.txt2list("columns.txt")
    logs = GREY_FUNCTIONS.json2dict(json_filename)    
    for column in columns:
        whitelist = []
        output_logs = {}  
        junk = {}
        whitelist_filename = whitelist_path
        whitelist_filename += column + "_whitelist.txt"
        whitelist = GREY_FUNCTIONS.txt2list(whitelist_filename)
        for key in logs[column].keys():
            value = key
            test = GREY_FUNCTIONS.matchRegexList(value, whitelist)
            if test:
                junk[value] = logs[column][value]
            else:
                output_logs[value] = logs[column][value]
        GREY_FUNCTIONS.dict2txt("./Results/", output_logs, column)
        GREY_FUNCTIONS.dict2txt("./Results/JUNK/", junk, column)
main()