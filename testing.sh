#!/bin/bash

file='InitialConfig'
i=1
node="no"
index="no"
startdate="no"
while read line; do
  nodecheck=2
  if [ $i -eq $nodecheck ]
  then
    node=$line
  fi
  indexcheck=4
  if [ $i -eq $indexcheck ]
  then
    index=$line
  fi
  datecheck=6
  if [ $i -eq $datecheck ]
  then
    startdate=$line
  fi
  i=$((i+1))
done < $file

echo $node
echo $index
echo $startdate
