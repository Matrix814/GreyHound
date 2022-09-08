#!/bin/bash
cd ./Results

for f in $(ls);
do
    echo "Processing files locates in the $f results:"
    for g in $(ls);
    do
        echo "     $g human readable format is BLAH"

    done;
done;
