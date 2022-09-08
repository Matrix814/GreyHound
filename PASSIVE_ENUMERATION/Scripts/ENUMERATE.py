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

max_size = 3000

import warnings
warnings.filterwarnings('ignore', '.*Elasticsearch*', )


#Input: mystery_object<type irrelevant> Object you want to print
#       spacer<string> Its the string of tabs to indent the print as you start getting into nested items
#       flag<string> That denotes what the previous recurse id'd this field as to add helpful characters for reading output
#Output:STDOUT Easily Human readable layout of the data structure
#Description: Recurse print is the helper function to easy print that handles interpreting the input and breaks it into nested 
#             calls of this function till it finds an item that isnt iteratable
#             "-": Denotes that an item is an element in an array
#            "*:": Denotes that an item is a key in a dictionary
#             "+": Denotes that an item is the field referenced by a dictionary key
#            "\t": Denotes that an item is nested one layer deeper
def recursive_print(mystery_object, spacer, flag):
    if type(mystery_object) is dict:
        for key in mystery_object.keys():
            if flag == 'listdict':
                recursive_print(key, spacer + '-' , "key")
            elif flag == 'dict2':
                recursive_print(key, spacer + '+' , "key")
            else:
                recursive_print(key, spacer, "key")
            if type(mystery_object[key]) is dict:
                recursive_print(mystery_object[key], '\t' + spacer, "dict2")
            elif type(mystery_object[key]) is list:
                recursive_print(mystery_object[key], spacer, "list")
            else:
                recursive_print(mystery_object[key], '\t' + spacer, "field")
    elif type(mystery_object) is list:
        for item in mystery_object:
            if type(item) is dict:
                recursive_print(item, '\t' + spacer, "listdict")
            elif type(item) is list:
                recursive_print(item, '\t' + spacer, "list")
            else:
                recursive_print(item, '\t' + spacer, "element")
    else:
        if flag == "key":
            print(spacer + str(mystery_object) + ":")
        elif flag == "element":
            print(spacer + "-" + str(mystery_object))
        elif flag == "field":
            print(spacer + "+" + str(mystery_object))
        else:
            print(spacer + str(mystery_object))
            
            
#Input:        item<type irrelevant> Object you want to print
#Output:       STDOUT Easily Human readable layout of the data structure
#Description:
#              "-": Denotes that an item is an element in an array
#              "*:": Denotes that an item is a key in a dictionary
#              "+": Denotes that an item is the field referenced by a dictionary key       
def rec_print(item):
    recursive_print(item, "", "")
    

#Input: <String> Field that you are trying to compare to regex_list
#       <List> List of regex expressions
#Output: <Booolean> Returns true if it matches any of the regex expressions
def matchRegexList(field, regex_list):
    flag = False
    for regex_string in regex_list:
        match = re.search(regex_string, field)
        if bool(match):
            return bool(match)
    
    return flag

#Input: <dictionary>dict with integer field values
#Output: <int> the sum of all the fields
def dict_counter(mydict):
    total = 0
    for key in mydict.keys():
        total += mydict[key]
    return(total)

#Input: es_node<String> The Elastisearch Node for performing queries
#       index<String> The index within elastisearch that you are searching against
#       days[<string>] Array of day fields for matted for Arkime
#       query_list[<String>] list of queries to search for in an OR search
#       column[<Strings>] List of fields inside of Elastic that you would want searched for
#       path2result<String> Path to the folder you would want the results stored in
#       postfix<String> Nondynamoc portion of the the filename for results
#Output:
#       Final_Result{Dictionary} of elastisearch results
#
#Subordinate Functions: enumerate_day(), dict_add_enumerate()
def pull_ips(es_node, index, days,query_list,columns,path2result,postfix):
    es = Elasticsearch(es_node, timeout=30000)
    print("//STARTING CONNECTED IP SEARCH PLEASE WAIT//")
    days_start_time = time.time()
    logging.getLogger('elasticsearch').setLevel(logging.ERROR)
    should = []
    for clean in query_list:
        should.append({"query_string" : {"analyze_wildcard" : "true", "query" : clean}})
    query_body = {"bool": {"should": should}}
    final_result = {}
    for day in days:
        day_result = (enumerate_day(es, index, query_body, day, columns,path2result,postfix))
        final_result = dict_add_enumerate(day_result, final_result)
    return final_result


#Input: es_node<String> The Elastisearch Node for performing queries
#       index<String> The index within elastisearch that you are searching against
#       days[<string>] Array of day fields for matted for Arkime
#       public_ips[<String>] list of public facinf non-internal IPS to search for in an OR search
#       column[<Strings>] List of fields inside of Elastic that you would want searched for
#       path2result<String> Path to the folder you would want the results stored in
#       postfix<String> Nondynamoc portion of the the filename for results
#Output:
#       Final_Result{Dictionary} of elastisearch results
#
#Subordinate Functions: enumerate_day(), dict_add_enumerate()
def enumerate_multiple(es_node, index, days,public_ips,columns,path2result,postfix):
    es = Elasticsearch(es_node, timeout=30000)
    print("Searching for Internal IPs")
    print("//STARTING SEARCH FOR PLEASE WAIT//")
    days_start_time = time.time()
    logging.getLogger('elasticsearch').setLevel(logging.ERROR)
    should = []
    should.append({"query_string" : {"analyze_wildcard" : "true", "query" : "source.ip : 10.0.0.0\/8"}})
    should.append({"query_string" : {"analyze_wildcard" : "true", "query" : "source.ip : 172.31.0.0\/16"}})
    should.append({"query_string" : {"analyze_wildcard" : "true", "query" : "source.ip : 192.168.0.0\/24"}})
    for clean in public_ips:
        should.append({"query_string" : {"analyze_wildcard" : "true", "query" : "source.ip : " + clean}})
    query_body = {"bool": {"should": should}}
    final_result = {}
    for day in days:
        day_result = (enumerate_day(es, index, query_body, day, columns,path2result,postfix))
        final_result = dict_add_enumerate(day_result, final_result)
    difference = time.time() - days_start_time
    print("Time to Complete Total Search;", difference, "SECS")
    return final_result


#Input: es_node<String> The Elastisearch Node for performing queries
#       index<String> The index within elastisearch that you are searching against
#       days[<string>] Array of day fields for matted for Arkime
#       single_ip[<String>] list of a single IP to search for and enumerate
#       column[<Strings>] List of fields inside of Elastic that you would want searched for
#       path2result<String> Path to the folder you would want the results stored in
#       postfix<String> Nondynamoc portion of the the filename for results
#Output:
#       Final_Result{Dictionary} of elastisearch results
#
#Subordinate Functions: enumerate_day(), dict_add_enumerate()
def enumerate_single(es_node, index, days,single_ip,columns,path2result,postfix):
    es = Elasticsearch(es_node, timeout=30000)
    print("//STARTING ENUMERATION FOR: "+str(single_ip[0])+" :PLEASE WAIT//")
    days_start_time = time.time()
    logging.getLogger('elasticsearch').setLevel(logging.ERROR)
    should = []
    for clean in single_ip:
        should.append({"query_string" : {"analyze_wildcard" : "true", "query" : "source.ip : " + clean}})
    query_body = {"bool": {"should": should}}
    final_result = {}
    for day in days:
        day_result = (enumerate_day(es, index, query_body, day, columns,path2result,postfix))
        final_result = dict_add_enumerate(day_result, final_result)
    difference = time.time() - days_start_time
    return final_result


#Input: es_node<String> The Elastisearch Node for performing queries
#       es_index<String> The day index within elastisearch that you are searching against
#       query_body{Dict} Of the comma seperated query to run on elastic
#       column[<Strings>] List of fields inside of Elastic that you would want searched for
#       path2result<String> Path to the folder you would want the results stored in
#       postfix<String> Nondynamoc portion of the the filename for results
#Output:
#       LargeDict{Dictionary[Source.IP][Columns][Counts]} of elastisearch results for enumeration
def long_enumerate(es,es_index,query_body,columns,path2result,postfix):
    original_start_time = time.time()
    refresh = time_update(original_start_time, original_start_time)
    elastisearch_results=es.search(index=es_index,query=query_body,
                                   scroll='5m',size=max_size)
    results = elastisearch_results['hits']['hits']
    size_results = 0#len(results)
    new_scroll = elastisearch_results['_scroll_id']
    while(size_results):
        refresh = time_update(refresh, original_start_time)
        elastisearch_results = es.scroll(scroll_id=new_scroll,scroll='5m')
        redux_results(results, es_index, columns,path2result, postfix)
        results = elastisearch_results['hits']['hits']
        size_results = len(results)
        new_scroll = elastisearch_results['_scroll_id']
    es.clear_scroll(scroll_id=new_scroll)
    large_dict = {}
    for result in results:
        new_dict = {}
        for column in columns:
            new_dict[column] = []
            if "." in column:
                two_part_key = column.split(".")
                if two_part_key[0] in result['_source'].keys():
                    if two_part_key[1] in result['_source'][two_part_key[0]].keys():
                        value = (result['_source'][two_part_key[0]][two_part_key[1]])
                        if type(value) is list:
                            new_dict[column]=value
                        else:
                            new_dict[column]=value
            else:
                if column in result['_source'].keys():
                    new_dict[column] = result['_source'][column]
                    
                    
        #Portion that creates the counts for enumeration         
        source_ip = new_dict['source.ip']
        if source_ip in large_dict.keys():
            for key in new_dict.keys():
                if not (key == 'source.ip'):
                    value = new_dict[key]
                    if (type(value) is list):
                        for item in value:
                            if item in large_dict[source_ip][key].keys():
                                large_dict[source_ip][key][item] += 1
                            else:
                                large_dict[source_ip][key][item] = 1
                    else:
                        if value in large_dict[source_ip][key].keys():
                            large_dict[source_ip][key][value] += 1
                        else:
                            large_dict[source_ip][key][value] = 1
        else:
            large_dict[source_ip] = {}
            for key in new_dict.keys():
                if not (key == 'source.ip'):
                    large_dict[source_ip][key] = {}
                    value = new_dict[key]
                    if (type(value) is list):
                        for item in value:
                            large_dict[source_ip][key][item] = 1
                    else:
                        large_dict[source_ip][key][value] = 1
    return(large_dict)


#Input: Elastisearch Instance
#       Index of table to enumerate
#       Dictionary of search fields for elastisearch
#       The day to search through
#Output: Dictionary of [Deisred Columns][Recorded Values][Count of each Value] for a day to fuction
#Subordinate Functions: long_enumerate
def enumerate_day(es,index,query_body,day,columns,path2result,postfix):
    es_index = index + day
    day_start_time = time.time()
    day_result = long_enumerate(es,es_index,query_body,columns,path2result,postfix)
    current_time = time.time()
    difference = current_time - day_start_time
    return day_result

    

#Input: New Results Dictionary [columns of interest][values of columns][counts of occurence] 
#       Previous Results Dictionary [columns of interest][values of columns][counts of occurence] 
#Output: Dictionary [columns of interest][values of columns][counts of occurence] 
#Description: Takes the previous results and updates that dictionary with the newest results 
#             and updates the count of occurences if the field has been detected before and adds it
#             to the dictionary if was not present with an initial count of 1
def dict_add_enumerate(new_dict, saved_dict):
    sum_dict = {}
    for address in saved_dict.keys():
        sum_dict[address] = {}
        for column in saved_dict[address].keys():
            sum_dict[address][column] = {}
            for value in saved_dict[address][column].keys():
                sum_dict[address][column][value] = saved_dict[address][column][value] 
    for address in new_dict.keys():
        if address in sum_dict.keys():
            for column in new_dict[address].keys():
                for value in new_dict[address][column].keys():
                    if  value in sum_dict[address][column].keys():
                        sum_dict[address][column][value] += new_dict[address][column][value]
                    else:
                        sum_dict[address][column][value] = new_dict[address][column][value] 
        else:
            sum_dict[address] = {}
            for column in new_dict[address].keys():
                sum_dict[address][column] = {}
                for value in new_dict[address][column].keys():
                    sum_dict[address][column][value] = new_dict[address][column][value] 
    return sum_dict


#Input: Results Dictionary [columns of interest][values of columns][counts of occurence] 
#       <STRING> desired file name to write the data too 
#Output: json file of the dictionaries
def dict2json(my_dict, filename):
    with open(filename, 'w') as json_file:
        json.dump(my_dict, json_file)
                  
                  
                  
#Input: <STRING> desired file name to read the data from     
#Output: Results Dictionary [columns of interest][values of columns][counts of occurence]
def json2dict(filename):
    data = {}
    try:
        with open(filename) as json_file:
            data = json.load(json_file)
    except:
        dict2json(data, filename)
    return data

#Input: <String> Folder name/path to the desired filename  
#       <DICTIONARY> Takes any dictionary
#       <String> field that is being analyzed
#       <String> Date Range of the dictionary to provide unique range
#Output: [File] Text document containing the values of the dictionary in user friendly format
def dict2txt(folder, my_dict, filename):
    file = folder + filename + '.txt'
    with open(file, 'w') as fwrite: 
        for key, value in my_dict.items(): 
            fwrite.write('%s:\t%s\n' % (key, value))

            
#Input: <Time> Time of last time update
#       <Time> Original Time of start of operations
#Output:<Time> If the time difference is larger than a minute then
#       it returns the current time 
#       Otherwise it returns the refresh time it was fed
def time_update(refresh_time, original):
    current_time = time.time()
    if (current_time - refresh_time) > 60:
        updated = current_time - original
        print("//SEARCH STILL RUNNING//", updated,"SECs//")
        refresh_time = current_time
    return refresh_time


#Input: <Dictionary> A dicitonary with values that are numbers 
#Output:<Dictionary> Same dictionary but where keys are sorted 
#       by the ascending value of the their datas value
def dict_sort(mydict):
    sorted_keys = sorted(mydict, key=mydict.get)
    sorted_dict = {}
    for key in sorted_keys:
        sorted_dict[key] = mydict[key]
    return sorted_dict


#Input: <Int>Number of days you want in the past (EX: [1 : Yesterday])
#Output <List[string]> List of days that are index compatible
def arkime_last_n_days(n):
    days = []
    today = date.today()
    for i in range(0, n + 1):
        d = datetime.timedelta(days = i)
        n_past = today - d
        year = n_past.strftime("%y")
        month = n_past.strftime("%m")
        day = n_past.strftime("%d")
        index_string ='-'+str(year)+str(month)+str(day)
        days.append(index_string)
    return days

#Input: <Date> Date of last search
#       <Int>Number of days you want in the past (EX: [1 : Yesterday])
#Output <List[string]> List of days that are index compatible
def arkime_between_n_days(begin, n):
    days = []
    date_array = begin.split('/')
    month = int(date_array[0])
    day = int(date_array[1])
    year = int(date_array[2])
    end_date = date(year, month, day)
    for i in range(0, n + 1):
        d = datetime.timedelta(days = i)
        n_past = end_date - d
        year = n_past.strftime("%y")
        month = n_past.strftime("%m")
        day = n_past.strftime("%d")
        index_string ='-'+str(year)+str(month)+str(day)
        days.append(index_string)
    return days

#Input: <String> Filename
#Output <List[String]> List of all the lines in string format from a txt document
def txt2list(filename):
    lines = []
    if os.path.exists(filename):
        with open(filename) as f:
            lines = f.readlines()
    new_lines = []
    for line in lines:
        new_lines.append(line.strip())
    return new_lines

#Input: <String> Date represented in string formatted mm/dd/yyyy
#Output: <Int> Number of days since input day
def differenceINbegin(begin):
    date_array = begin.split('/')
    month = int(date_array[0])
    day = int(date_array[1])
    year = int(date_array[2])
    begin_date = date(year, month, day)
    difference = date.today() - begin_date
    return(difference.days)

#Input: <String> Date represented in string formatted mm/dd/yyyy
#Output: <Int> Number of days since input day
def difference2dates(begin, end):
    date_array = begin.split('/')
    month = int(date_array[0])
    day = int(date_array[1])
    year = int(date_array[2])
    begin_date = date(year, month, day)
    date_array2 = end.split('/')
    month2 = int(date_array2[0])
    day2 = int(date_array2[1])
    year2 = int(date_array2[2])
    end_date = date(year2, month2, day2)
    difference = end_date - begin_date
    number = difference.days
    return(number)

#Input: en_dict<dict[sourceIP<str>][column<str>][value<str>]=count<int>
#Output endict without ephimeral ports
def enumerate_display(en_dict):
    ehpemeral_start = 1024
    standardLGports = [3389,4444,5900]
    standard_dict = {}
    for address in en_dict.keys():
        standard_dict[address] = {}
        for column in en_dict[address].keys():
            standard_dict[address][column] = {}
            if column == "source.port":
                for value in en_dict[address][column].keys():
                    if (int(value) < 1024) or (value in standardLGports):
                        standard_dict[address][column][value] = en_dict[address][column][value]
            elif column == "destination.port":
                for value in en_dict[address][column].keys():
                    if int(value) < 1024 or (value in standardLGports):
                        standard_dict[address][column][value] = en_dict[address][column][value]
            else:
                for value in en_dict[address][column].keys():
                    standard_dict[address][column][value] = en_dict[address][column][value]
    return standard_dict


#Input: en_dict[IP Address<String>][Columns of Interest][Unique Values][Count of values]
#Output: STDOUT that prints out a Human Readable Output for enumeration        
def easy_read_enumeration(en_dict):
        for address in en_dict.keys():
            print('----IP ADDRESS----')
            print(address)
            print('----Protocol----')
            protocols = dict_sort(en_dict[address]['protocol'])
            for protocol in protocols.keys():
                print(protocol + ":", protocols[protocol])
            print('----SRC PORT----')
            ports = dict_sort(en_dict[address]['source.port'])
            for port in ports.keys():
                print(str(port) + ":", ports[port])
            print('----DST PORT----')
            ports = dict_sort(en_dict[address]['destination.port'])
            for port in ports.keys():
                print(str(port) + ":", ports[port])