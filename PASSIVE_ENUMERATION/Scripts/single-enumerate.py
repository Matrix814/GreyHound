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
import ENUMERATE
    
#//GLOBAL VARIABLES//
breakline = "-" * 73
#Maximum size of the Elastiseach page
max_size = 1000

#Path & postfix of file name format [path][date index][postfix].json
path2result = './JSON_Storage/'
postfix = '_enumerate_pre_results.json'

path2final = "./Archive/"
final_postfix = ".json"
    
def main():
    start_time = time.time()
    es_node = sys.argv[1]
    index = sys.argv[2]
    days = 0
    columns = ENUMERATE.txt2list("./Columns/columns.txt")
    ip_whitelist = [sys.argv[4]]
    n = ENUMERATE.differenceINbegin(sys.argv[3])
    days = ENUMERATE.arkime_last_n_days(n)
    final_unsorted_dict = ENUMERATE.enumerate_single(
                                                          es_node,
                                                          index,
                                                          days,
                                                          ip_whitelist,
                                                          columns,
                                                          path2result,
                                                          postfix)
    standard_ports = (ENUMERATE.enumerate_display(final_unsorted_dict))
    sorted_dict = {}
    for address in standard_ports.keys():
        sorted_dict[address] = {}
        for column in standard_ports[address].keys():
            sorted_dict[address][column] = ENUMERATE.dict_sort(standard_ports[address][column])
    print("Time to Complete Total Enumeration of", ip_whitelist[0], "is:", time.time()-start_time, "SECS")
    print(breakline)
    ENUMERATE.easy_read_enumeration(sorted_dict)
    full_path = path2final + ip_whitelist[0] + days[0] + days[-1] + "_" + sys.argv[4] + final_postfix
    ENUMERATE.dict2json(sorted_dict, full_path)
    print(breakline)
    print("FOR THE OUTPUT LOOK UNDER:", full_path)
    
main()