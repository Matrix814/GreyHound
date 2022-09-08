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
    filename = sys.argv[1]
    destination_filename = sys.argv[2]
    frequency = float(sys.argv[3])
    columns = GREY_FUNCTIONS.txt2list("columns.txt")
    Pre_LFA = GREY_FUNCTIONS.json2dict(filename)
    LFA_dict = {}
    LFA_dict = GREY_FUNCTIONS.split_LFA(Pre_LFA, frequency, columns)
    GREY_FUNCTIONS.dict2json(LFA_dict, destination_filename)
    
    
main()