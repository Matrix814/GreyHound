#!/bin/bash
node=$1
index=$2
user=$3
line="------------------------------------------------------------------------"
option=0
while [ $option -ne 5 ]
do
echo "Welcome to the passive enumerator"
echo "Please select from one of the following options:"
echo "------------------------------------------------"
echo "1) Enumerate internal & public-facing IPs start of collection"
echo "2) Enumerate a single IP Address"
echo "3) Enumerate the connections of a IP Address"
echo "4) Delete/Clean Collected Data and revert storage to original config within Enemurate"
echo "5) Return to Bloodhound Menu"
read option

if [ $option -eq 1 ];
then
warning="y"
    if [ $warning == 'y' ];
    then
    echo $line
    echo "Enumerating from beginning start date to today:"
    echo $line
    python3 ./Scripts/multi-enumerate.py $node $index $user
    fi
fi

if [ $option -eq 2 ];
then
    echo $line
    echo "Please enter an IP address in the format [0-255].[0-255].[0-255].[0-255]"
    read ip
    if [[ $ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; 
        then
        echo $line
        echo "Enumerating the IP Address: $ip"
        python3 ./Scripts/single-enumerate.py $node $index $user $ip
    else
        echo $line
        echo "Please enter a valid IP address $ip is incorrect"
    fi
fi

if [ $option -eq 3 ];
then
    echo $line
    echo "This will create a text document with information on all the IP Addresses that"
    echo "an IP connected to over a date range"
    echo "Please enter the IP address to be analyzed in the format [0-255].[0-255].[0-255].[0-255]"
    read ip
    if [[ $ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; 
        then
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
            
            echo "Enumerating $ip connections from $first_date to $second_date"
            python3 ./Scripts/search_between_2.py $node $index $ip $first_date $second_date
        
    else
        echo $line
        echo "Please enter a valid IP address $ip is incorrect"
    fi
fi

if [ $option -eq 4 ];
then
    warning=''
    echo $line
    echo "This will remove all archived, collected, and products from" 
    echo "any of the PASSIVE_ENUMERATION Directory"
    echo "Are you sure that you want to remove all the files?: "
    echo "Enter:        DELETE       in all caps to contine with the removal of files"
    read warning
    if [ $warning == "DELETE" ];
    then
        rm -f ./Archive/*.json
        rm -f ./JSON_Storage/*.json
        rm -f ./MostRecentCollection/*.json
        rm -r ./Results/
        echo $line
        echo "The collected data files have been removed"
    fi

fi

echo $line
done