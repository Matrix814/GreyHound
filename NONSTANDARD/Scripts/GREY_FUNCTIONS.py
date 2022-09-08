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


#Input: <List>[src.ip][src.port][protocol][dst.ip][dst.port][timestamp]
#Output: {{src.ip, src.port, protocol, dst.ip, dst.port}:[timestamps]}
def nonstd_redux_list2dict(results,remove_anomoly):
    results_dict = {}
    anomoly_dict = json2dict("Parent.json")
    for result in results:
        redux_dict_key = ""
        anomoly_flag = False
        anomoly_keys = anomoly_dict.keys()
        if (str(result["source.port"]) in anomoly_keys):
            str_result_protocol = str(result["protocol"][0])
            str_anomoly_protocol = anomoly_dict[str(result["source.port"])][0]
            if (len(result["protocol"]) == 1) and (str_result_protocol == str_anomoly_protocol):
                anomoly_flag = True
        elif (str(result["destination.port"]) in anomoly_keys):
            str_result_protocol = str(result["protocol"][0])
            str_anomoly_protocol = anomoly_dict[str(result["destination.port"])][0]
            if (len(result["protocol"]) == 1) and (str_result_protocol == str_anomoly_protocol):
                anomoly_flag = True
        if not(remove_anomoly) or not(anomoly_flag):
            for key in result.keys():
                if(key !="@timestamp" and key !="destination.port" and key !="source.port"):
                    redux_dict_key += str(key) + " : " + str(result[key]) + " "
            if redux_dict_key in results_dict.keys():
                if not(result["@timestamp"] in results_dict[redux_dict_key]["@timestamp"]):
                    results_dict[redux_dict_key]["@timestamp"].append(result["@timestamp"])
                if not(result["destination.port"] in results_dict[redux_dict_key]["destination.port"]):
                    results_dict[redux_dict_key]["destination.port"].append(result["destination.port"])
                if not(result["source.port"] in results_dict[redux_dict_key]["source.port"]):
                    results_dict[redux_dict_key]["source.port"].append(result["source.port"])
            else:
                results_dict[redux_dict_key] = {}
                results_dict[redux_dict_key]["@timestamp"] = [result["@timestamp"]]
                results_dict[redux_dict_key]["source.port"] = [result["source.port"]]
                results_dict[redux_dict_key]["destination.port"] = [result["destination.port"]]
            
    return results_dict


#Input: es_node<String> The Elastisearch Node for performing queries
#       index<String> The index within elastisearch that you are searching against
#       days[<string>] Array of day fields for matted for Arkime
#       public_ips[<String>] list of public facinf non-internal IPS to search for in an OR search
#       column[<Strings>] List of fields inside of Elastic that you would want searched for
#       path2result<String> Path to the folder you would want the results stored in
#       postfix<String> Nondynamic portion of the the filename for results
#Output:
#       Final_Result{Dictionary} of elastisearch results
#
#Subordinate Functions: nonstd_search_day()      
def nonstd_search(es_node, index, days, query_list, ip_whitelist, columns,remove_anomoly):
    es = Elasticsearch(es_node, timeout=30000)
    print("Searching for Desired Fields")
    print("//STARTING SEARCH FOR PLEASE WAIT//")
    days_start_time = time.time()
    logging.getLogger('elasticsearch').setLevel(logging.ERROR)
    should = []
    must = []
    for clean in ip_whitelist:
        must.append({"query_string" : {"analyze_wildcard" : "true", "query" : clean}})
    for clean in query_list:
        should.append({"query_string" : {"analyze_wildcard" : "true", "query" : clean}})
    or_body = {"bool": {"should": should}}
    must.append(or_body)
    query_body= {"bool": {"must": must}}
    final_dict = {}
    for day in days:
        temp_dict ={}
        temp_dict = json2dict("./TMP/nonstd_tmp.json")
        day_results = nonstd_search_day(es, index, query_body, day, columns,remove_anomoly)
        final_dict = nonstd_dict_add(day_results, temp_dict)
        dict2json(final_dict, "./TMP/nonstd_tmp.json")
    difference = time.time() - days_start_time
    dict2json({}, "./TMP/nonstd_tmp.json")
    print("Time to Complete Total Search;", difference, "SECS")
    
    if (len(final_dict.keys()) != 0): 
        return final_dict
    else:
        return False
    
    
#Input: Elastisearch Instance
#       Index of day for elastisearch
#       Dictionary of search fields for elastisearch
#Output: Dictionary of [Deisred Columns][Recorded Values][Count of each Value] for a day to file
#Subordinate Functions: nonstd_redux_results    
#//Start HERE//
#NEED TO REDO REDUX REDULTS TO NEW FUNCTION THAT WILL RETURN REDUXISH ID'd LOGS
#TAKE THIS DICTIONARY AND PASS IT BACK UP TO THE DAY PERFORM DAY ADDITION USING THE NEW 
#DICTIONARY ADDIDITION FUNCTION YOU MADE
def long_nonstd_search(es,es_index,query_body,columns,remove_anomoly):
    original_start_time = time.time()
    refresh = time_update(original_start_time, original_start_time)
    elastisearch_results=es.search(index=es_index,query=query_body,
                                   scroll='5m',size=max_size)
    results = elastisearch_results['hits']['hits']
    final_reduced_results = {}
    reduced_results = nonstd_redux_results(
        results,es_index,columns,remove_anomoly)
    final_reduced_results = nonstd_dict_add(reduced_results, final_reduced_results)
    size_results = len(results)
    new_scroll = elastisearch_results['_scroll_id']
    while(size_results):
        refresh = time_update(refresh, original_start_time)
        elastisearch_results = es.scroll(scroll_id=new_scroll,scroll='5m')
        reduced_results = nonstd_redux_results(results,es_index,columns,remove_anomoly)
        final_reduced_results = nonstd_dict_add(reduced_results, final_reduced_results)
        results = elastisearch_results['hits']['hits']
        size_results = len(results)
        new_scroll = elastisearch_results['_scroll_id']
    es.clear_scroll(scroll_id=new_scroll)
    return final_reduced_results
    
#Input: es_node<String> The Elastisearch Node for performing queries
#       index<String> The index within elastisearch that you are searching against
#       days[<string>] Array of day fields for matted for Arkime
#       query_body{Dictionary} Elastic formatted query to search against the stack
#       path2result<String> Path to the folder you would want the results stored in
#       postfix<String> Nondynamic portion of the the filename for results
#Output:
#       Day_Result{Dictionary} of elastisearch results
#
#Subordinate Functions: long_nonstd_search() 
def nonstd_search_day(es,index,query_body,day,columns,remove_anomoly):
    es_index = index + day
    day_start_time = time.time()
    day_result = long_nonstd_search(
        es,es_index,query_body,columns,remove_anomoly)
    current_time = time.time()
    difference = current_time - day_start_time
    print("Date: ", day, "Time to Complete;", difference, "SECS")
    return day_result
  


#Input: Results from elastisearch: list of nested dictionaries
#Output: Dictionary [columns of interest][values of columns] to JSON
#Subordinate Functions: redux_result_column, redux_list2dict, redux_day_updater
def nonstd_redux_results(results,index,columns,remove_anomoly):
    result_list = []
    for result in results:
        result_dict = redux_result_column(result, columns,remove_anomoly)
        result_list.append(result_dict)
    result_dict = {}
    result_dict = nonstd_redux_list2dict(result_list,remove_anomoly)
    return result_dict

#Input: Elastisearch Instance
#       Index of table to search
#       Dictionary of search fields for elastisearch
#       The day to search through
#Output: Dictionary of [Deisred Columns][Recorded Values][Count of each Value] for a day to file
#Subordinate Functions: redux_long_search
def redux_search_day(es,index,query_body,day,columns,path2result,postfix):
    es_index = index + day
    day_start_time = time.time()
    redux_long_search(es,es_index,query_body,columns,path2result,postfix)
    current_time = time.time()
    difference = current_time - day_start_time
    print("Date: ", day, "Time to Complete;", difference, "SECS")
    

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
#Subordinate Functions: redux_search_day()      
def redux_search_multiple(es_node, index, days, query_list, ip_whitelist, columns,path2result,postfix):
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
        redux_search_day(es, index, query_body, day, columns,path2result,postfix)
    difference = time.time() - days_start_time
    print("Time to Complete Total Search;", difference, "SECS")



#Input: Elastisearch Instance
#       Index of day for elastisearch
#       Dictionary of search fields for elastisearch
#Output: Dictionary of [Deisred Columns][Recorded Values][Count of each Value] for a day to file
#Subordinate Functions: refresh, redux_results  
def redux_long_search(es,es_index,query_body,columns,path2result,postfix):
    original_start_time = time.time()
    refresh = time_update(original_start_time, original_start_time)
    elastisearch_results=es.search(index=es_index,query=query_body,
                                   scroll='5m',size=max_size)
    results = elastisearch_results['hits']['hits']
    redux_results(results,es_index,columns,path2result,postfix)
    size_results = len(results)
    new_scroll = elastisearch_results['_scroll_id']
    while(size_results):
        refresh = time_update(refresh, original_start_time)
        elastisearch_results = es.scroll(scroll_id=new_scroll,scroll='5m')
        redux_results(results, es_index, columns,path2result, postfix)
        results = elastisearch_results['hits']['hits']
        size_results = len(results)
        new_scroll = elastisearch_results['_scroll_id']
    es.clear_scroll(scroll_id=new_scroll)

#Input: Results from elastisearch: list of nested dictionaries
#Output: Dictionary [columns of interest][values of columns][counts of occurence] to JSON
#Subordinate Functions: redux_result_column, redux_list2dict, redux_day_updater
def redux_results(results,index,columns,path2result,postfix):
    new_list = []
    for result in results:
        new_list.append(redux_result_column(result, columns))
    new_dict = redux_list2dict(new_list, columns)
    redux_updater(new_dict,index,columns,path2result,postfix)
    

#Input: Result from elastisearch: Dictionary containing every field of a result
#Output: Dictionary [columns of interest][values of columns]   
def redux_result_column(result, columns, remove_anomoly):
    new_dict = {}
    for column in columns:
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
def redux_updater(new_dict, index, columns, path2result, postfix):
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


#Input: <List> Any style
#       <String> Full filename to the new file
#Output: txt document of the record
def list2txt(my_list, filename):
    if (len(my_list) != 0):
        textfile = open(filename, "w")
        for element in my_list:
            textfile.write(str(element) + "\n")
        textfile.close()
        
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
    

#Input: New Results Dictionary [columns of interest][values of columns][counts of occurence] 
#       Previous Results Dictionary [columns of interest][values of columns][counts of occurence] 
#Output: Dictionary [columns of interest][values of columns][counts of occurence] 
#Description: Takes the previous results and updates that dictionary with the newest results 
#             and updates the count of occurences if the field has been detected before and adds it
#             to the dictionary if was not present with an initial count of 1
def nonstd_dict_add(new_dict, saved_dict):
    sum_dict = {}
    #Initializes the dictionary to the value of the saved dictionary
    for address in saved_dict.keys():
        sum_dict[address] = {}
        for column in saved_dict[address].keys():
            sum_dict[address][column] = saved_dict[address][column] 
    #Takes the value of the new dict and adds their ports and timestamps to the lists
    #if the address exists but the values dont exist yet in the list
    for address in new_dict.keys():
        if address in sum_dict.keys():
            for column in new_dict[address].keys():
                for value in new_dict[address][column]:
                    if  not (value in sum_dict[address][column]):
                        sum_dict[address][column].append(value)
        #Adds the value entirely if the address string wasnt present
        else:
            sum_dict[address] = {}
            for column in new_dict[address].keys():
                sum_dict[address][column] = new_dict[address][column]
    return sum_dict

