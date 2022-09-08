
#!/bin/bash
file='InitialConfig'
i=1
readnode="no"
readindex="no"
readstartdate="no"
while read line; do
  nodecheck=2
  if [ $i -eq $nodecheck ]
  then
    readnode=$line
  fi
  indexcheck=4
  if [ $i -eq $indexcheck ]
  then
    readindex=$line
  fi
  datecheck=6
  if [ $i -eq $datecheck ]
  then
    readstartdate=$line
  fi
  i=$((i+1))
done < $file

echo "The current configurations from Initial Config Are:"
echo "The Elastic node is: $readnode"
echo "The Elastic index to search is: $readindex"
echo "The recorded start date is: $readstartdate"



node=$readnode
index=$readindex
user=$readstartdate
line="------------------------------------------------------------------------"
echo $line
option=0
while [ $option -ne 5 ]
do
echo "Welcome to the Bloodhound"
echo "Please select from one of the following options:"
echo $line
echo "1) Start the Enumeration suite of tools"
echo "2) Start the Non-Standard Protocol Tool"
echo "3) Start the Protocol Analyzer Suite (Currently LFA Supported)"
echo "4) Start the Proxy Log Analyzer  //KIT ISSUES CURRENTLY DISABLED//"
echo "5) Quit"
read option

if [ $option -eq 1 ];
then
    echo $line
    cd PASSIVE_ENUMERATION
    ./enumerate.sh $node $index $user
    cd ..
fi
if [ $option -eq 2 ];
then
    echo $line
    cd NONSTANDARD
    ./nonstd.sh $node $index $user
    cd ..
fi
if [ $option -eq 3 ];
then
    echo $line
    cd PROTOCOLS
    ./protocols.sh $node $index $user
    cd ..
fi
if [ $option -eq 4 ];
then
    echo $line
    cd PROXY
    ./proxy.sh $node $index $user
    cd ..
fi
done
