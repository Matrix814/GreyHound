import GREY_FUNCTIONS
import sys
import os
node = sys.argv[1]
index = sys.argv[2]
#Add a handler here for $anomoly where read in alternate jsons based on TCP UDP Association create it in the grey functions handler, pass it down to where we select the protocls and ignore line if in tcp-udp csv that protocol is the only element 
date1=sys.argv[3]
date2=sys.argv[4]
n = GREY_FUNCTIONS.difference2dates(date1, date2)
days = GREY_FUNCTIONS.arkime_between_n_days(date2, n)
if int(sys.argv[5]) == 1:
    remove_anomoly = True
else:
    remove_anomoly = False
non_std = GREY_FUNCTIONS.json2dict("non-std-ports.json")
rev_index = GREY_FUNCTIONS.json2dict("ReverseIndex.json")
protocols =GREY_FUNCTIONS.txt2list("userinput_protocol.txt")
columns = [
    "source.ip",
    "source.port",
    "protocol",
    "destination.ip",
    "destination.port",
    "@timestamp"
]
for key in non_std.keys():
    if key in protocols:
        print("Ports assigned to the the protocol:", key)
        port_query = []
        protocol_query = []
        for port in non_std[key]:
            port_query.append("destination.port : " + str(port)) 
            port_query.append("source.port : " + str(port))
            for protocol in rev_index[port]:
                sub_protocol_query = "NOT protocol : " + protocol
                if not (sub_protocol_query in protocol_query):
                    protocol_query.append(sub_protocol_query)
        result = GREY_FUNCTIONS.nonstd_search(node, index, days, port_query, protocol_query, columns,remove_anomoly)
        if result:
            flag_txt =""
            if remove_anomoly:
                flag_txt = "_NO_ANOMOLY"
            dir_path = "./Results/" + "USER_nonstd" + days[0]+days[-1]+flag_txt
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            filename = dir_path+"/"+key+days[0]+days[-1]+".json"
            GREY_FUNCTIONS.dict2json(result,filename)
            print("Length of Addresses is:", len(result.keys()))
        print("-"*70)
