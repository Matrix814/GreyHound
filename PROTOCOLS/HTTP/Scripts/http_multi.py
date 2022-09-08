from elasticsearch import Elasticsearch
import pandas as pd
import json
import time
import logging
from datetime import date
import datetime
import re
import sys
import os
import os.path
import GREY_FUNCTIONS
    
#//GLOBAL VARIABLES//

#Maximum size of the Elastiseach page
max_size = 1000

#Path & postfix of file name format [path][date index][postfix].json
path2result = './JSON_Storage/'
postfix = '_lfa_pre_results.json'

path2final = "./Archive/INITIAL_http_logs"
final_postfix = ".json"
    
def main():
    es_node = sys.argv[1]
    index = sys.argv[2]
    days = 0
    columns = GREY_FUNCTIONS.txt2list("columns.txt")
    query_list = GREY_FUNCTIONS.txt2list("query.txt")
    ip_whitelist = GREY_FUNCTIONS.txt2list("./Whitelist/ip_whitelist.txt")
    n = GREY_FUNCTIONS.differenceINbegin(sys.argv[3])
    days = GREY_FUNCTIONS.arkime_last_n_days(n)
    LFA_percentage = .05
    GREY_FUNCTIONS.redux_search_multiple(es_node, index, days, query_list, ip_whitelist, columns)
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
    
main()