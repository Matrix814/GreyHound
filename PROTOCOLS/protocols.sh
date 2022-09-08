#!/bin/bash
node=$1
index=$2
user=$3
line="------------------------------------------------------------------------"
option=0
while [ $option -ne 3 ]
do
echo "Welcome to the protocol analyzer suite"
echo "Please select from one of the following options:"
echo "------------------------------------------------"
echo "1) Open the HTTP protocol analyzer"
echo "2) Open the SMTP protocol analyzer"
echo "3) Return to Bloodhound Menu"
read option

if [ $option -eq 1 ];
then
    echo $line
    cd HTTP
    ./http.sh $node $index $user
    cd ..
fi

if [ $option -eq 2 ];
then
    echo $line
    cd SMTP
    ./smtp.sh $node $index $user
    cd ..
fi
echo $line
done