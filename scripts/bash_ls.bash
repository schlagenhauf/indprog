#!/bin/bash

# when called without arguments (i.e. input / output files),
# return the port specs
if [ "$#" -eq 0 ]; then
  echo ";out"
  exit 0

# When provided with the list of input and output files, run
# the actual processing routine
elif [ "$#" -eq 1 ]; then
  IFS=';' read -ra IOARGS <<< "$1"
  IFS=',' read -ra INFILES <<< "${IOARGS[0]}"
  IFS=',' read -ra OUTFILES <<< "${IOARGS[1]}"
  echo "Bash in files: $INFILES"
  echo "Bash out files: $OUTFILES"

  ls > ${OUTFILES[0]}

  exit 0

# otherwise, print the usage information
else
  echo "Usage:"
  echo -e "\tscipt.sh []: returns port specs as a list of port names"
  echo -e "\tscipt.sh infile1,...,inFileN outFile1,...,outFileM : run script with the input/output file names as arguments"
  exit 1
fi
