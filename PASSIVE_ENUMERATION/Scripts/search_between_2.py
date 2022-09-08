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

#Maximum size of the Elastiseach page
max_size = 1000

#Path & postfix of file name format [path][date index][postfix].json
path2result = './JSON_Storage/'
postfix = '_ips_connected.json'

path2final = "./Archive/ips_connected_"
final_postfix = ".json"
    
def main():
    start_time = time.time()
    es_node = sys.argv[1]
    index = sys.argv[2]
    days = 0
    columns = ["destination.ip","source.ip"]
    ip_to_scan = sys.argv[3]
    dest_query = "destination.ip : " + ip_to_scan
    src_query = "source.ip : " + ip_to_scan
    query_list = [dest_query, src_query]
    ip_whitelist = ENUMERATE.txt2list("./Whitelist/ip_whitelist.txt")
    begin = sys.argv[4]
    end = sys.argv[5]
    if end == "TODAY":
        n = ENUMERATE.differenceINbegin(begin)
        days = ENUMERATE.arkime_last_n_days(n)
    else:
        n = ENUMERATE.difference2dates(begin, end)
        days = ENUMERATE.arkime_between_n_days(end, n)
    ips_dict = (ENUMERATE.pull_ips(es_node,index,days,query_list,columns,
                                        path2result,postfix))
    ips = []
    for address in ips_dict.keys():
        if address == ip_to_scan:
            for dst_address in ips_dict[address]['destination.ip'].keys():
                if not(dst_address in ips):
                    ips.append(dst_address)
        elif not(address in ips):
            ips.append(address)
            
            
            
    columns = ENUMERATE.txt2list("./Columns/columns.txt")     
    dir_path = "./Results/" + "Connections_" + ip_to_scan
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    for ip_addr in ips:
        
        ip_connected_summary = ENUMERATE.enumerate_single(es_node, index, days,[ip_addr],
                                                               columns,path2result,postfix)
        standard_ports = (ENUMERATE.enumerate_display(ip_connected_summary))
        ENUMERATE.dict2json(standard_ports,dir_path+"/"+ip_addr+"<-->"+
                                 ip_to_scan+final_postfix)
    print("Time to Complete Enumeration of", ip_to_scan, "is:", time.time()-start_time, "SECS")
    
main()