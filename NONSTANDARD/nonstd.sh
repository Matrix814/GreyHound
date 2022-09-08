#!/bin/bash
node=$1
index=$2
user=$3
line="---------------------------------------------------------------------"
echo $line
option=0
while [ $option -ne 6 ]
do
echo "Welcome to the Non-Standard Port-Protocol Analyzer"
echo "Please select from one of the following options:"
echo "------------------------------------------------"
echo "1) Pull all anomoulous port-protocol usage from entire date range" 
echo "//WARNING VERY SLOW AND LARGE RESULTS//"
echo "2) Pull anomolous port-protocol usage from a specified date range"
echo "3) Pull anomolous traffic for specific set of protocols"
echo "4) Create Human Readable non-JSONs for current results"
echo "5) Delete/Clean Collected Data and revert storage to original config to all nested tools"
echo "6) Return to Bloodhound Menu"
read option

if [ $option -eq 1 ];
then
    echo $line
    anomoly="We need more Data Engineers and Data Scientists"
    echo "Due to misindexed fields theres is a chance that there will be additional results due to"
    echo "malformed packets where the protocol analyzer on the kit will mislabel things as UDP/TCP"
    echo "EX: It would mislabel FTP Traffic over port 21 as just TCP traffic over port 21"
    echo "Would you like to exclude this traffic? (It will reduce result size but can remove anomolous traffic) [y/n]"
    read anomoly
    if [ $anomoly == "y" ];
    then
        anomoly=1
    else
        anomoly=0
    fi
    echo "test"
    python3 ./Scripts/multi_nonstd.py $node $index $user $anomoly
fi
if [ $option -eq 2 ];
then
    echo $line
    echo "Please specify the date range that you wish to pull all Non-Standard Port-Protocol Pairs"
    echo "You will need to select the 2 dates you would like to search between"
        echo "Please enter the first date in the format MM/DD/YYYY"
        first_date="no"
        read first_date
        date "+%m/%d/%Y" -d $first_date > /dev/null  2>&1
            is_valid=$?
        if [ $is_valid -ne 0 ];
        then
            echo "INVALID DATE FORMAT DATE SHOULD BE FORMATTED MM/DD/YYYY"
            exit 1
        fi
        echo "Please enter the second date in the format MM/DD/YYYY"
        read second_date
        date "+%m/%d/%Y" -d $second_date > /dev/null  2>&1
        is_valid=$?
        if [ $is_valid -ne 0 ];
        then
             echo "INVALID DATE FORMAT DATE SHOULD BE FORMATTED MM/DD/YYYY"
             exit 1
        fi
        anomoly="We need more Data Engineers and Data Scientists"
    echo "Due to misindexed fields theres is a chance that there will be additional results due to"
    echo "malformed packets where the protocol analyzer on the kit will mislabel things as UDP/TCP"
    echo "EX: It would mislabel FTP Traffic over port 21 as just TCP traffic over port 21"
    echo "Would you like to exclude this traffic? (It will reduce result size but can remove anomolous traffic) [y/n]"
    read anomoly
    if [ $anomoly == "y" ];
        then
            anomoly=1
        else
            anomoly=0
    fi
       echo "Pulling abnormal connections from $first_date to $second_date"
       python3 ./Scripts/between_nonstd.py $node $index $first_date $second_date $anomoly
fi
if [ $option == 3 ];
then
    userprotocol="Scream"
    rm -f "userinput_protocol.txt"
    while [ $userprotocol != "QUIT" ]
    do
        echo $line
        echo "Enter the protocol you would like to include in the list to search"
        echo "Type: QUIT"
        echo "To stop entering prtocols" 
        read userprotocol
        if [ $userprotocol != "QUIT" ];
        then
            echo $userprotocol >> "userinput_protocol.txt"  
        fi
    done
    echo $line
    echo "Please specify the date range that you wish to pull all Non-Standard Port-Protocol Pairs"
    echo "You will need to select the 2 dates you would like to search between"
        echo "Please enter the first date in the format MM/DD/YYYY"
        first_date="no"
        read first_date
        date "+%m/%d/%Y" -d $first_date > /dev/null  2>&1
            is_valid=$?
        if [ $is_valid -ne 0 ];
        then
            echo "INVALID DATE FORMAT DATE SHOULD BE FORMATTED MM/DD/YYYY"
            exit 1
        fi
        echo "Please enter the second date in the format MM/DD/YYYY"
        read second_date
        date "+%m/%d/%Y" -d $second_date > /dev/null  2>&1
        is_valid=$?
        if [ $is_valid -ne 0 ];
        then
             echo "INVALID DATE FORMAT DATE SHOULD BE FORMATTED MM/DD/YYYY"
             exit 1
        fi
        anomoly="We need more Data Engineers and Data Scientists"
    echo "Due to misindexed fields theres is a chance that there will be additional results due to"
    echo "malformed packets where the protocol analyzer on the kit will mislabel things as UDP/TCP"
    echo "EX: It would mislabel FTP Traffic over port 21 as just TCP traffic over port 21"
    echo "Would you like to exclude this traffic? (It will reduce result size but can remove anomolous traffic) [y/n]"
    read anomoly
    if [ $anomoly == "y" ];
        then
            anomoly=1
        else
            anomoly=0
    fi
       echo "Pulling abnormal connections for user specified protocols between:"
       echo "$first_date to $second_date"
       python3 ./Scripts/user_nonstd.py $node $index $first_date $second_date $anomoly
fi
done