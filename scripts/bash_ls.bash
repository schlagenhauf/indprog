#!/bin/bash

bash_process() {
  echo "Bash in files: $1"
  echo "Bash out files: $2"

  ls > $2

  return 0
}


#### DO NOT CHANGE THE PART BELOW ####

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
  bash_process "$INFILES" "$OUTFILES"
  exit $?

# otherwise, print the usage information
else
  echo "Usage:"
  echo -e "\tscipt.sh []: returns port specs as a list of port names"
  echo -e "\tscipt.sh infile1,...,inFileN outFile1,...,outFileM : run script with the input/output file names as arguments"
  exit 1
fi
