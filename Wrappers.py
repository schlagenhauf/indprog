#!/usr/bin/python3

#import os, sys, tempfile
import matlab.engine
import tempfile
import subprocess

from Processing import Process

class MatlabProcess(Process):
    def __init__(self):
        self.eng = matlab.engine.start_matlab()
        self.scriptFun = getattr(self.eng, "matlabTemplate")

        inPortSpecs, outPortSpecs, paramSpecs = self.scriptFun(nargout=3)
        self.paramSpecs = [inPortSpecs, outPortSpecs]
        self.params = {name : 0 for name in paramSpecs}


    def run(self, inFds, outFds):
        self.scriptFun(inFds, outFds, list(self.params.values()), nargout=0)


class BashProcess(Process):
    def __init__(self):
        self.scriptName = './bashTemplate.sh'


    def run(self, inFds, outFds):
        cmd = self.scriptName + ' ' + ' '.join(map(str,inFds)) + ' ' + ' '.join(map(str,outFds))
        #cmd = self.scriptName + ' --inFds=' + ','.join(map(str,inFds)) + ' --outFds=' + ','.join(map(str,outFds))
        subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    inFile = tempfile.SpooledTemporaryFile()
    outFile = tempfile.SpooledTemporaryFile()

    inFile.write(b"test")
    inFile.seek(0)

    print([inFile.fileno(),outFile.fileno()])

    #mp = MatlabProcess()
    #mp.run([inFile.fileno(), 23],[outFile.fileno(), 24])

    bp = BashProcess()
    #bp.run([inFile.fileno(), 23],[outFile.fileno(), 24])
    bp.run([inFile.fileno()],[outFile.fileno()])
