#!/bin/bash

# when called without arguments (i.e. input / output files),
# return the port specs
if [ "$#" -eq 0 ]; then
  echo "in1 out1"
  exit 1

# When provided with the list of input and output files, run
# the actual processing routine
elif [ "$#" -eq 2 ]; then

# parse arguments into arrays
IFS=',' read -r -a inFiles <<< "$1"
IFS=',' read -r -a outFiles <<< "$2"

# print files
#echo "Input Files:"
#for i in ${inFiles[@]}; do
#  echo $i
#done
#
#echo "Output Files:"
#for i in ${outFiles[@]}; do
#  echo $i
#done

# a sample functionality
cat ${inFiles[0]} | tr 'e' '$' > ${outFiles[0]}

# otherwise, print the usage information
else
  echo "Usage:"
  echo -e "\tscipt.sh []: returns port specs as a list of port names"
  echo -e "\tscipt.sh infile1,...,inFileN outFile1,...,outFileM : run script with the input/output file names as arguments"
fi
