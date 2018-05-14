import json
import csv
import random
import os
import re
import numpy as np
import gc
import copy

class server(object):
    def __init__(self,
                 startTime,
                 setupTime,
                 requestCanHandle = 50,
                 failureProbability = 0.,
                 type = 0):

        self.startTime = startTime
        self.setupTime = setupTime
        self.requestCanHandle = requestCanHandle
        self.status = 'starting'
        self.timeToOperational = setupTime
        self.failureProbability = failureProbability
        self.type = type
        self.generateRandomSequence(sequenceSize=1400)

    def generateRandomSequence(self, sequenceSize):
        self.randomSequence = np.random.uniform(0,1,sequenceSize)

    def updateStatus(self, currentTime):
        #Checking if a server fails
        minuteID = int(currentTime % 1440)
        randomValue = self.randomSequence[minuteID % len(self.randomSequence)]
        if randomValue <= self.failureProbability:
            self.status = 'crashed'

        #Update timeToOperational if server is still starting
        #and status if it went operational
        if self.status == 'starting':
            if currentTime - self.startTime < self.setupTime:
                self.timeToOperational = self.setupTime - (currentTime - self.startTime)
            else:
                self.status = 'operational'
                self.timeToOperational = 0

class interfaceSimulator(object):
    def __init__(self,
                 files,
                 timeframe = 10,
                 serverStartTime = 20,
                 initialServers=[4, 4],
                 startTimeShift = 0,
                 sequenceAutoUpdate = True,
                 serverTypes = 2,
                 failureProbabilities = [0., 0.005],
                 mode = 'M'):

        self.files = files
        self.timeframe = timeframe
        self.serverStartTime = serverStartTime
        self.initialServers = initialServers
        self.serverStartTime = serverStartTime
        self.startTimeShift = startTimeShift
        self.sequenceAutoUpdate = sequenceAutoUpdate
        self.numPatterns = len(files)
        self.serverTypes = serverTypes
        self.failureProbabilities = failureProbabilities
        self.mode = mode

        self.iteration = 0
        self.emulationStartingTime = 0

        self.currentTime = self.emulationStartingTime + self.startTimeShift * 60

        self.__initializeData__(files)
        self.__initiateServers__(self.initialServers)
        self.__generateRandomSequence__()

    def __initializeData__(self, files):
        self.fileData = []
        for file in files:
            self.fileData.append([])
            with open (file) as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                next(reader)
                for row in reader:
                    self.fileData[-1].append(row)

    def __initiateServers__(self, number):
        output = []
        for type in range(len(number)):
            for s in [server(self.currentTime, 0, 0) for i in range(number[type])]:
                s.status = 'operational'
                s.type = type
                s.failureProbability = self.failureProbabilities[type]
                output.append(s)
        self.servers = output

    def __initiateSequences__(self):
        self.sequence = []
        id = range(self.numPatterns)
        for i in id:
            sequenceInstance = [random.gauss(float(params[1]), float(params[2])) for params in self.fileData[i]]
            self.sequence.append(sequenceInstance)

    def __generateRandomServerSequence__(self, sequenceSize):
        for server in self.servers:
            server.generateRandomSequence(sequenceSize=sequenceSize)

    def __generateRandomSequence__(self, id=None):
        if id is not None and id >= self.numPatterns: raise Exception('Incorrect id: id of a sequence is higher than the number of sequences (files with data)')

        if id is None:
            self.sequence = []
            id = range(self.numPatterns)
            for i in id:
                sequenceInstance = [random.gauss(float(params[1]), float(params[2])) for params in self.fileData[i]]
                self.sequence.append(sequenceInstance)
        else:
            sequenceInstance = [random.gauss(float(params[1]), float(params[2])) for params in self.fileData[id]]
            self.sequence[id] = sequenceInstance

        self.__generateRandomServerSequence__(sequenceSize=1440)

    def getSequenceId(self):
        # This is a stub allowing you to use several datasets (sequences, simulation modes).
        # For example, one mode could be for regular days and another - for black Friday sales spike.
        # For the purpose of this excersise we will use only ine simulation mode: regular days.
        return 0

    def setFailureProbability(self, failureProbabilities):
        self.failureProbabilities = failureProbabilities
        for server in self.servers:
            server.failureProbability = failureProbabilities[server.type]

    def setLoad(self, load):
        self.load = float(load)

    def getNextState(self):
        seqNumRequests = []
        seqMeanCPU = []
        seqOperationaServers = []
        seqStartingServers = []

        for i in range(self.timeframe):
            seqID = int(self.getSequenceId())
            minuteID = int(self.currentTime % 1440)
            params = self.fileData[seqID][minuteID % len(self.fileData)]
            if self.mode == 'M':
                seqNumRequests.append(random.gauss(float(self.load), float(params[2])))
            else:
                seqNumRequests.append(self.sequence[seqID][minuteID])
            seqOperationaServers.append(self.getNumOperationalServers())
            seqStartingServers.append(self.getNumStartingServers())
            prevOperationalServers = sum(seqOperationaServers[-1])
            if prevOperationalServers < 1: prevOperationalServers = 0.1
            seqMeanCPU.append(seqNumRequests[-1] / (prevOperationalServers * 50.))
            self.currentTime += 1
            if self.currentTime % 1440 == 0 and self.sequenceAutoUpdate:
                self.__generateRandomSequence__(seqID)
            self.updateServers()

        hour = np.floor((self.currentTime / 60) % 24)
        meanRequests = np.mean(seqNumRequests)
        maxCPULoad = np.mean(seqMeanCPU)
        numOperationalServers = np.mean(seqOperationaServers, axis=0)
        numStartingServers = np.mean(seqStartingServers, axis=0)

        return {'meanRequests':meanRequests,
                'numOperationalServers':numOperationalServers,
                'numStartingServers':numStartingServers,
                'failureProbabilities':self.failureProbabilities,
                'maxCPULoad':maxCPULoad,
                'servers':copy.deepcopy(self.servers),
                'currentTime':self.currentTime}

    def setState(self, state):
        self.currentTime = state['currentTime']
        self.servers = copy.deepcopy(state['servers'])

    def updateServers(self):
        for s in self.servers:
            s.updateStatus(self.currentTime)
        self.servers = [server for server in self.servers if server.status != 'crashed']

    def getNumOperationalServers(self):
        return [sum([1*(s.status == 'operational' and s.type == type) for s in self.servers]) for type in range(self.serverTypes)]

    def getNumStartingServers(self):
        return [sum([1*(s.status == 'starting' and s.type == type) for s in self.servers]) for type in range(self.serverTypes)]

    def getStartingServers(self):
        return [i for i in self.servers if i.status == 'starting']

    def reset(self):
        self.currentTime = self.emulationStartingTime
        self.currentTime = self.emulationStartingTime + self.startTimeShift * 60
        self.__initiateServers__(self.initialServers)
        self.__generateRandomSequence__()

    def __startServer__(self, number, type, failureProbability):
        for i in range(number):
            self.servers.append(server(self.currentTime, self.serverStartTime, failureProbability=failureProbability, type=type))

    def __stopServer__(self, number, type):
        if number >=  sum(self.getNumOperationalServers()): return 0
        if number > self.getNumOperationalServers()[type]: return 0
        else:
            self.servers = [otherInstances for otherInstances in self.servers if otherInstances.type != type] +\
                           sorted([requestedInstance for requestedInstance in self.servers if requestedInstance.type == type], key=lambda x: (self.currentTime - x.setupTime))[number:]

    def startEC2(self, number=1, type=0):
        self.__startServer__(number=number, type=type, failureProbability=self.failureProbabilities[type])

    def startSpot(self, number=1, type=1):
        self.__startServer__(number=number, type=type, failureProbability=self.failureProbabilities[type])

    def stopEC2(self, number=1, type = 0):
        self.__stopServer__(number=number, type=type)

    def stopSpot(self, number=1, type = 1):
        self.__stopServer__(number=number, type=type)




