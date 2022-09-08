#!/bin/bash

#grep -Ei "*.exe: *" ./Results/email.filename.txt | cut -d: -f 1 > ./Results/ExecutableFileNames.txt
#grep -Ei "*.zip: *" ./Results/email.filename.txt | cut -d: -f 1 >> ./Results/ExecutableFileNames.txt
#grep -Ei "*.rar: *" ./Results/email.filename.txt | cut -d: -f 1 >> ./Results/ExecutableFileNames.txt
#grep -Ei "*.tar: *" ./Results/email.filename.txt | cut -d: -f 1 >> ./Results/ExecutableFileNames.txt

node='http://10.1.19.100:9200'
index='arkime_sessions3'
user='03/16/2022'

python3 ./Scripts/filename.py $node $index $user 