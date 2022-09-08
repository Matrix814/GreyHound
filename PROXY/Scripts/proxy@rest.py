from elasticsearch import Elasticsearch
import pandas as pd
import json
import time
import logging
import datetime
import re
import os
import sys
from datetime import date
import GREY_FUNCTIONS


#Path & postfix of file name format [path][date index][postfix].json
path2result = './JSON_Storage/'
postfix = '_lfa_pre_results.json'

path2final = "./Archive/UPDATED@REST_proxy_logs"
final_postfix = ".json"


#Fields of interest from this style of log

def main():
    es_node = sys.argv[1]
    index = sys.argv[2]
    columns = GREY_FUNCTIONS.txt2list("columns.txt")
    days = 0
    n = GREY_FUNCTIONS.differenceINbegin(sys.argv[3])
    days = GREY_FUNCTIONS.proxy_last_n_days(n)
    final_unsorted_dict = {}
    for day in days:
        filename = path2result + index + day + postfix
        day_unsorted_dict = GREY_FUNCTIONS.json2dict(filename)
        final_unsorted_dict = GREY_FUNCTIONS.redux_dict_update(day_unsorted_dict, final_unsorted_dict, columns)
    #Final Sort
    
    sorted_dict = {}
    for column in columns:
        sorted_dict[column] = GREY_FUNCTIONS.dict_sort(final_unsorted_dict[column])
    GREY_FUNCTIONS.dict2json(sorted_dict, './MostRecentCollection/MostRecentCollection.json')
    GREY_FUNCTIONS.dict2json(sorted_dict, path2final + days[0] + days[-1] + final_postfix)
    #thing
    
    
    
main()