#!/bin/bash
if [ "$#" -eq 0 ]; then
  echo "in1,in2,in3 out1,out2"
  exit 1
fi

# print script arguments
for i in $@; do
  echo $i
done

# read from inFd
#echo "Bash received

echo "Bash script executed"
