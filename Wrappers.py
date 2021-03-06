
#import matlab.engine

import subprocess
import struct
import codecs
from abc import ABC, abstractmethod
import logging
logger = logging.getLogger(__name__)

from SecureFileOps import *

##
# @brief Wrapper for the process that a node represents. Can wrap a variety of actions.
class Process(ABC):
    def __init__(self, name):
        self.name = name
        self.params = {}
        self.portSpecs = [[],[]]

    ##
    # @brief Returns the port specifications of this process so that the containing node
    # can create them
    #
    # @return List of port specifications
    def getPortSpecs(self):
        return self.portSpecs


    ##
    # @brief Returns a reference to the parameter dictionary
    #
    # @return Dictionary of parameter names and values
    def getParams(self):
        return self.params

    def upToDate(self):
        return False

    @abstractmethod
    def run(self, inFds, outFds):
        pass


class FileReadProcess(Process):
    def __init__(self, name):
        super(FileReadProcess, self).__init__(name)
        self.params['filename'] = './file.txt'

    def getPortSpecs(self):
        return [[],['out']]

    def run(self, inFds, outFds):
        # TODO: make this more efficient than copying one file into another
        logger.debug('Reading file "%s"', self.params['filename'])

        data = secureFileRead(self.params['filename'], 'rb')
        if not data:
            return

        with open(outFds[0], 'wb') as oop:
            oop.write(data)


class FileWriteProcess(Process):
    def __init__(self, name):
        super(FileWriteProcess, self).__init__(name)
        self.params['filename'] = './file.txt'
        self.params['append'] = True
        self.params['encoding'] = 'None'

    def getPortSpecs(self):
        return [['in'],[]]

    def run(self, inFds, outFds):
        # TODO: make this more efficient than copying one file into another
        logger.debug('Writing file "%s"', self.params['filename'])
        mode = 'a' if self.params['append'] else 'w'

        enc = self.params['encoding']

        binary = False
        if enc == '' or enc == 'None':
            mode += 'b'
            binary = True
        else:
            try:
                codecs.lookup(enc)
            except LookupError:
                enc = 'ascii'
                logger.error('Encoding %s not available, falling back to %s' % (self.params['encoding'], enc))

        with open(self.params['filename'], mode) as sinkFile, open(inFds[0], 'rb') as iop:
            for line in iop:
                if binary:
                    sinkFile.write(line)
                else:
                    sinkFile.write(line.decode(enc))


class PrinterProcess(Process):
    def __init__(self, name):
        super(PrinterProcess, self).__init__(name)
        self.params['encoding'] = 'ascii'

    def getPortSpecs(self):
        return [['in'],[]]

    def run(self, inFds, outFds):
        for  i in inFds:
            with open(i, 'rb') as oip:
                logger.info('PRINTER: Read from input file:')
                while True:
                    line = oip.read()
                    if not line:
                        break

                    enc = self.params['encoding']
                    try:
                        codecs.lookup(enc)
                    except LookupError:
                        enc = 'ascii'
                        logger.error('Encoding %s not available, falling back to %s' % (self.params['encoding'], enc))

                    string = line.decode(enc)
                    logger.info('PRINTER: \t%s (%s)', string, line)


class ConstantProcess(Process):
    def __init__(self, name):
        super(ConstantProcess, self).__init__(name)
        self.params['value'] = "text"
        self.params['encoding'] = 'ascii'

    def getPortSpecs(self):
        return [[],['out']]

    def run(self, inFds, outFds):
        for o in outFds:
            oop = open(o, 'wb')
            if oop:

                enc = self.params['encoding']
                try:
                    codecs.lookup(enc)
                except LookupError:
                    enc = 'ascii'
                    logger.error('Encoding %s not available, falling back to %s' % (self.params['encoding'], enc))

                data = str(self.params['value']).encode(enc)

                logger.debug('Write to output file: %s (%s)', self.params['value'], str(data))
                oop.write(data)
                oop.flush()
                oop.close()


class AdditionProcess(Process):
    def __init__(self, name):
        super(AdditionProcess, self).__init__(name)

    def getPortSpecs(self):
        return [['summand1', 'summand2'],['sum']]

    def run(self, inFds, outFds):
        valSum = 0
        print('Adding: ')
        for i in inFds:
            iop = open(i, 'rb')
            if iop:
                data = iop.read()
                val = struct.unpack('f', data)[0]
                print(' + ' + str(val))
                valSum += val
                iop.close()

        print(' = ' + str(valSum))

        oop = open(outFds[0], 'wb')
        if oop:
            data = struct.pack('f',valSum)
            oop.write(data)
            oop.flush()
            oop.close()


class MatlabProcess(Process):
    def __init__(self, name):
        super(MatlabProcess, self).__init__(name)
        logger.error('The matlab process is not yet implemented. Do not use it')

#        self.eng = matlab.engine.start_matlab()
#        self.scriptFun = getattr(self.eng, "matlabTemplate")
#
#        inPortSpecs, outPortSpecs, paramSpecs = self.scriptFun(nargout=3)
#        self.paramSpecs = [inPortSpecs, outPortSpecs]
#        self.params = {name : 0 for name in paramSpecs}


    def run(self, inFds, outFds):
        logger.error('The matlab process is not yet implemented. Do not use it')
        #self.scriptFun(inFds, outFds, list(self.params.values()), nargout=0)

class BashProcess(Process):
    def __init__(self, name):
        super(BashProcess, self).__init__(name)
        self.params['filename'] = './bashTemplate.bash'
        try:
            bashProc = subprocess.Popen(self.params['filename'], shell=True, stdout=subprocess.PIPE)
            portSpecStr = bashProc.stdout.readline().decode('ascii').rstrip('\n').split(' ')
            self.portSpecs = [portSpecStr[0].split(','),portSpecStr[1].split(',')]
        except:
            logger.error('Failed to get port specs from bash script. Make sure that your script echoes \
                    a list of ports in the form in1,...,inN out1,...,outM when executed without arguments')
            self.portSpecs = [[],[]]


    def run(self, inFds, outFds):
        cmd = self.params['filename'] + ' ' + ','.join(inFds) + ' ' + ','.join(outFds)
        bashProc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        print(bashProc.stdout.read())
