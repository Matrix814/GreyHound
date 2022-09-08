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

max_size = 1000
path2result = './JSON_Storage/'
postfix = '_lfa_pre_results.json'

import warnings
warnings.filterwarnings('ignore', '.*Elasticsearch*', )

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


def dict_counter(mydict):
    total = 0
    for key in mydict.keys():
        total += mydict[key]
    return(total)

#Input: node of elastisearch
#       index of table to search
#       array of days to search through
#Output: Dictionary of [Deisred Columns][Recorded Values][Count of each Value] to a file
#Subordinate Functions: redux_search_day
def redux_search_multiple(es_node, index, days, query_list, ip_whitelist, columns):
    es = Elasticsearch(es_node, timeout=30000)
    print("Searching for Desired Fields")
    print("//STARTING SEARCH FOR PLEASE WAIT//")
    days_start_time = time.time()
    logging.getLogger('elasticsearch').setLevel(logging.ERROR)
    must = []
    for clean in ip_whitelist:
        must.append({"query_string" : {"analyze_wildcard" : "true", "query" : clean}})
    for clean in query_list:
        must.append({"query_string" : {"analyze_wildcard" : "true", "query" : clean}})
    query_body = {"bool": {"must": must}}
    for day in days:
        redux_search_day(es, index, query_body, day, columns)
    difference = time.time() - days_start_time
    print("Time to Complete Total Search;", difference, "SECS")

#Input: Elastisearch Instance
#       Index of table to search
#       Dictionary of search fields for elastisearch
#       The day to search through
#Output: Dictionary of [Deisred Columns][Recorded Values][Count of each Value] for a day to file
#Subordinate Functions: redux_long_search
def redux_search_day(es, index, query_body, day, columns):
    es_index = index + day
    day_start_time = time.time()
    redux_long_search(es, es_index, query_body, columns)
    current_time = time.time()
    difference = current_time - day_start_time
    print("Date: ", day, "Time to Complete;", difference, "SECS")
    

#Input: Elastisearch Instance
#       Index of day for elastisearch
#       Dictionary of search fields for elastisearch
#Output: Dictionary of [Deisred Columns][Recorded Values][Count of each Value] for a day to file
#Subordinate Functions: refresh, redux_results  
def redux_long_search(es, es_index, query_body, columns):
    original_start_time = time.time()
    refresh = time_update(original_start_time, original_start_time)
    elastisearch_results = es.search(index=es_index,query=query_body,scroll='5m',size=max_size)
    results = elastisearch_results['hits']['hits']
    redux_results(results, es_index, columns)
    size_results = len(results)
    new_scroll = elastisearch_results['_scroll_id']
    while(size_results):
        refresh = time_update(refresh, original_start_time)
        elastisearch_results = es.scroll(scroll_id=new_scroll,scroll='5m')
        redux_results(results, es_index, columns)
        results = elastisearch_results['hits']['hits']
        size_results = len(results)
        new_scroll = elastisearch_results['_scroll_id']

#Input: Results from elastisearch: list of nested dictionaries
#Output: Dictionary [columns of interest][values of columns][counts of occurence] to JSON
#Subordinate Functions: redux_result_column, redux_list2dict, redux_day_updater
def redux_results(results, index, columns):
    new_list = []
    for result in results:
        new_list.append(redux_result_column(result, columns))
    new_dict = redux_list2dict(new_list, columns)
    redux_updater(new_dict, index, columns)
    

#Input: Result from elastisearch: Dictionary containing every field of a result
#Output: Dictionary [columns of interest][values of columns]   
def redux_result_column(result, columns):
    new_dict = {}
    for column in columns:
        if column.split('.')[0] in result['_source'].keys():
            if column.split('.')[1] in result['_source'][column.split('.')[0]].keys():
                new_dict[column] = result['_source'][column.split('.')[0]][column.split('.')[1]]
            else:
                new_dict[column] = 'NSTR'
        else:
            new_dict[column] = 'NSTR'
        if column == 'message':
            new_dict[column] = extractIPstring(result['_source'][column])
    return new_dict


#Input: List of all results from ELK : [{redux_result_column: Dictionary[columns of interest][value]}]
#Output: Dictionary [columns of interest][values of columns][counts of occurence]
def redux_list2dict(results, columns):
    new_dict = {}
    for column in columns:
        new_dict[column] = {}
    for result in results:
        for column in columns:
            if column in result.keys():
                value = result[column]
            else:
                value = "NSTR"
            if type(value) == list:
                for item in value:
                    if item in new_dict[column].keys():
                        new_dict[column][item] +=1
                    else:
                        new_dict[column][item] = 1
            else:
                if value in new_dict[column].keys():
                    new_dict[column][value] +=1
                else:
                    new_dict[column][value] = 1
    return new_dict

#Input: Dictionary [columns of interest][values of columns][counts of occurence]
#Output: Dictionary [columns of interest][values of columns][counts of occurence] to JSON 
#Description: Opens the temp json file and updates its values with the most up to date values
#             Then writes the most up to date version over the previous version
#Subordinate Functions: json2dict, dict2json, redux_dict_update
def redux_updater(new_dict, index, columns):
    filename = path2result + index + postfix
    saved_dict = json2dict(filename)
    reduced_dict = redux_dict_update(new_dict, saved_dict, columns)
    dict2json(reduced_dict , filename)
    

#Input: New Results Dictionary [columns of interest][values of columns][counts of occurence] 
#       Previous Results Dictionary [columns of interest][values of columns][counts of occurence] 
#Output: Dictionary [columns of interest][values of columns][counts of occurence] 
#Description: Takes the previous results and updates that dictionary with the newest results 
#             and updates the count of occurences if the field has been detected before and adds it
#             to the dictionary if was not present with an initial count of 1
def redux_dict_update(new_dict, saved_dict, columns):
    temp_dict = {}
    for column in columns:
        if not (column in new_dict.keys()):
            new_dict[column] = {}
            new_dict[column]["NSTR"] = 1
        if not (column in saved_dict.keys()):
            saved_dict[column] = {}
            saved_dict[column]["NSTR"] = 1
        for key in new_dict[column].keys():
            saved_keys = saved_dict.keys()
            if (len(saved_keys) == 0):
                for column2 in columns:
                    saved_dict[column2] = {}
            if key in saved_dict[column].keys():
                saved_dict[column][key] += new_dict[column][key]
            else:
                saved_dict[column][key] = new_dict[column][key]
    return saved_dict


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


#Input: <Dictionary> A dicitonary with values that are numbers 
#       <Float> % of LFA for analysis
#Output <Dictionary> A dictionary that has removed 
def split_LFA(results, frequency, columns):
    lfa_dict = {}
    for column in columns:
        column_total_length = len(results[column])
        column_threshold = column_total_length * frequency
        unfiltered = {}
        filtered = {}
        for item in results[column]:
            if item in unfiltered.keys():
                unfiltered[item] += 1
            else:
                unfiltered[item] = 1
        for item in unfiltered.keys():
            if unfiltered[item] <= column_threshold:
                filtered[item] = unfiltered[item]
        lfa_dict[column] = dict_sort(filtered)
    return lfa_dict

#Input: <Dictionary> 
#Output: [STDOUT] Prints out the dictionary in User Friendly format
def dict_print(mydict):
    print("//NEW DICT//")
    for key in mydict.keys():
        print (key)
        print ('\t', mydict[key])
    print("//END DICT//")
    
    
#Input: <Dictionary> Of the message Column of proxy logs
#Output <Dictionary> Of Message Column reduced to just the Remote IP Connections
def messageColumnRefine(message_dict):
    remote_ips = {}
    for value in message_dict.keys():
            ip = extractIPstring(value)
            if ip:
                if ip in remote_ips.keys():
                    remote_ips[ip] += message_dict[value]
                else:
                    remote_ips[ip] = message_dict[value] 
    return remote_ips

#Input: <String> The Message field from the proxy logs
#Output <String> The IP if it can be extracted or the <Boolean> False if it fails
def extractIPstring(message):
    ip = False
    match = re.search('\d*HIER_DIRECT/*', message)
    if match:
        new_string = message.split()
        new_string = new_string[-2]
        new_match = re.search('HIER_DIRECT/*.*.*.*', new_string)
        if new_match:
            ip_string = new_string.split("/")
            ip_string = ip_string[-1]
            ip = ip_string
    return ip

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


#Input: <Int>Number of days you want in the past (EX: [1 : Yesterday])
#Output <List[string]> List of days that are index compatible
def proxy_last_n_days(n):
    days = []
    today = date.today()
    for i in range(0, n + 1):
        d = datetime.timedelta(days = i)
        n_past = today - d
        year = n_past.strftime("%Y")
        month = n_past.strftime("%m")
        day = n_past.strftime("%d")
        index_string ='-'+str(year)+'.'+str(month)+'.'+str(day)
        days.append(index_string)
    return days

#Input: !!!USER INTERACTION REQUIRED!!!
#       <Desired Class> Desired Class
#       <String> Prompt you want presented to the user
#Output: <Desired Class> Desired Class if it can be easily cast
#        Otherwise it returns false and screams bloody murder
#Supported Classes: Int, String, Float
def get_user_data_clean(desired, prompt):
    valid_input = False
    while(not valid_input):
        test = input(prompt)
        if desired == "string":
            return test
        elif desired == 'int':
            try:
                test = int(test)
                return test
            except:
                no = True
        elif desired == 'float':
            try:
                test = float(test)
                return test
            except:
                no = True
        failure_message = "Unsatisfactory input, of:" + test +"\nNot of type:" + desired
        print(failure_message, "\nPlease try again")
    
    
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