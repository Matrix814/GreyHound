#!/bin/bash
node=$1
index=$2
user=$3

option=0
while [ $option -ne 5 ]
do
echo "Welcome to the HTTP meta data puller:"
echo "Please select from one of the following options"
echo "1) Scan the entire date range from collection start date to now (//WARNING//)"
echo "2) Scan the past N days and add it to the collected data"
echo "3) Perform a Least Frequency analysis on the collected data (Standard 5%)"
echo "4) Display the results of any Least Frequenct Analysis"
echo "5) Return to the Protocols Menu"
read option

if [ $option -eq 1 ];
then
warning="n"
echo "Performing a full scan will overwrite any previously recorded data are you sure you want to proceed [y/n]?"
read warning
    
    if [ $warning == 'y' ];
    then
    echo "Searching from beginning start date to today:"
    python3 ./Scripts/http_multi.py $node $index $user
    fi
fi

if [ $option -eq 2 ];
then
warning="n"
echo "Performing a partial scan will overwrite any previously recorded data are you sure you want to proceed [y/n]?"
read warning
    
    if [ $warning == 'y' ];
    then
    echo "How many days back would you like to search?"
    days=0
    read days
    echo "Running Search for the past $days Days"
    python3 ./Scripts/past_n_http.py $node $index $days
    echo $user
    python3 ./Scripts/search@rest.py $node $index $user
    fi
fi

if [ $option -eq 3 ];
then
standard="y"
echo "Would you like to use the standard 5% LFA [y/n] Default is y?"
read standard
    percentage=42
    if [ $standard == 'n' ];
    then
        while ((percentage < 0 || percentage > 1))
        do
        echo "What percentage would you like to use (Please enter a float between 0 and 1 [Ex: .03]):"
        read percentage
        done
        echo "Performing LFA for $percentage on collected data"
    else
        percentage=.05
        echo "Performing LFA for $percentage on collected data"
    fi
    python3 ./Scripts/LFA.py "./MostRecentCollection/MostRecentCollection.json" './Results/LFA_http_logs.json' $percentage
fi

if [ $option -eq 4 ];
then
    echo "Creating .txt file output on the last completed LFA:"
    python3 ./Scripts/DisplayAllColumns.py "./Results/LFA_http_logs.json" "./Whitelist/"
    echo "//Output Generated//"
    echo "To access these files please check under the Results directory"
fi
echo "//Action complete//"
echo ""

done