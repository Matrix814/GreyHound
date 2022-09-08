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

path2final = "./Archive/InternalIPEnumerationRange"
final_postfix = ".json"
    
def main():
    es_node = sys.argv[1]
    index = sys.argv[2]
    days = 0
    columns = ENUMERATE.txt2list("./Columns/columns.txt")
    ip_whitelist = ENUMERATE.txt2list("./Whitelist/internet_facing_ips.txt")
    n = ENUMERATE.differenceINbegin(sys.argv[3])
    days = ENUMERATE.arkime_last_n_days(n)
    final_unsorted_dict = ENUMERATE.enumerate_multiple(es_node,
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
    ENUMERATE.dict2json(sorted_dict, './MostRecentCollection/MostRecentCollection.json')
    full_path = path2final + days[0] + days[-1] + final_postfix
    ENUMERATE.dict2json(sorted_dict, full_path)
    print(breakline)
    print("The JSON that contains the enumerated Internal IPs & Public IPs")
    print("The file is at:", full_path)
main()