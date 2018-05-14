import numpy as np
import time
import matplotlib.pyplot as plt
import random
import gc
import tkinter as tk
from tkinter import *
import os

class controller(object):
    def __init__(self, interface, plotHistory = None, spotHourlyPrice = 0.05, spotFailureProbability = 0.01, overloadCost=0.05, mode='M'):
        self.interface = interface
        self.actions = ['startEC2', 'startSpot', 'doNothing', 'stopEC2', 'stopSpot']
        self.plotHistory = plotHistory
        self.history = {'maxCPULoad':[0. for i in range(plotHistory)],
                        'totalRequests':[0. for i in range(plotHistory)],
                        'EC2ServersRunning':[0. for i in range(plotHistory)],
                        'spotServersRunning':[0. for i in range(plotHistory)],
                        'EC2ServersStarting':[0. for i in range(plotHistory)],
                        'spotServersStarting':[0. for i in range(plotHistory)],
                        'totalCost':[0. for i in range(plotHistory)],
                        'baselineRequests':[50. for i in range(plotHistory)]
                        }

        self.EC2HourlyPrice = 0.25
        self.EC2FailureProbability = 0.001
        self.simulationCost = 0
        self.spotHourlyPrice = spotHourlyPrice
        self.spotFailureProbability = spotFailureProbability
        self.overloadCost = overloadCost
        self.mode = mode
        self.interface.mode = self.mode

        if self.mode == 'M':
            master = tk.Tk()
            master.wm_title("Cloud Controller")
            self.loadChangeTrackBar = Scale(master, label="Load Change", from_=-25, to=25, orient=HORIZONTAL, resolution=1, length=300)
            self.loadChangeTrackBar.pack()
            self.loadChangeTrackBar.set(0)
            self.spotFailureProbabilityTrackBar = Scale(master, label="Spot failure probability", from_=0, to=0.1, orient=HORIZONTAL, resolution=0.001, length=300)
            self.spotFailureProbabilityTrackBar.pack()
            self.spotFailureProbabilityTrackBar.set(0.002)
            self.spotHourlyPriceTrackBar = Scale(master, label="Spot hourly price", from_=0.01, to=0.25, orient=HORIZONTAL, resolution=0.001, length=300)
            self.spotHourlyPriceTrackBar.pack()
            self.spotHourlyPriceTrackBar.set(0.016)
            self.overloadCostTrackBar = Scale(master, label="Overload cost", from_=0.005, to=0.5, orient=HORIZONTAL, resolution=0.001, length=300)
            self.overloadCostTrackBar.pack()
            self.overloadCostTrackBar.set(0.25)

    def getSpotFailureProbability(self):
        if self.mode == 'M': return self.spotFailureProbabilityTrackBar.get()
        else: return self.spotFailureProbability

    def getSpotHourlyPrice(self):
        if self.mode == 'M': return self.spotHourlyPriceTrackBar.get()
        else: return self.spotHourlyPrice

    def getOverloadCost(self):
        if self.mode == 'M': return self.overloadCostTrackBar.get()
        else: return self.overloadCost

    def setSpotFailureProbability(self, spotFailureProbability):
        self.interface.setFailureProbability([self.EC2FailureProbability, spotFailureProbability])

    def setSpotHourlyPrice(self, spotHourlyPrice):
        self.spotHourlyPrice = spotHourlyPrice

    def setOverloadCost(self, overloadCost):
        self.overloadCost = overloadCost

    def getNextState(self):
        if self.mode == 'M':
            self.setSpotFailureProbability(spotFailureProbability=self.getSpotFailureProbability())
            self.setSpotHourlyPrice(self.getSpotHourlyPrice())
            self.setOverloadCost(self.getOverloadCost())
            load_change = self.loadChangeTrackBar.get()
            print('Load change = ', load_change)
            print('Baseline requests = ', self.history['baselineRequests'][-1])
            currentLoad = self.history['baselineRequests'][-1] + load_change
            if currentLoad < 10:
                currentLoad = 10
            if currentLoad > 300:
                currentLoad = 300
            self.interface.setLoad(currentLoad)

        state = self.interface.getNextState()
        currentLoad = state['meanRequests']

        print('Current load = ', currentLoad)
        totalCost = self.getCost(state)

        if self.plotHistory is not None:
            self.history['maxCPULoad'].append(float(state['maxCPULoad']))
            self.history['totalRequests'].append(float(state['meanRequests']))
            self.history['EC2ServersRunning'].append(float(state['numOperationalServers'][0]))
            self.history['spotServersRunning'].append(float(state['numOperationalServers'][1]))
            self.history['EC2ServersStarting'].append(float(state['numStartingServers'][0]))
            self.history['spotServersStarting'].append(float(state['numStartingServers'][1]))

            self.simulationCost += totalCost
            self.history['totalCost'].append(totalCost)
            self.history['baselineRequests'].append(currentLoad)

            if len(self.history['maxCPULoad']) > self.plotHistory:
                self.history['maxCPULoad'] = self.history['maxCPULoad'][1:]
            if len(self.history['totalRequests']) > self.plotHistory:
                self.history['totalRequests'] = self.history['totalRequests'][1:]
            if len(self.history['EC2ServersStarting']) > self.plotHistory:
                self.history['EC2ServersStarting'] = self.history['EC2ServersStarting'][1:]
            if len(self.history['spotServersStarting']) > self.plotHistory:
                self.history['spotServersStarting'] = self.history['spotServersStarting'][1:]
            if len(self.history['EC2ServersRunning']) > self.plotHistory:
                self.history['EC2ServersRunning'] = self.history['EC2ServersRunning'][1:]
            if len(self.history['spotServersRunning']) > self.plotHistory:
                self.history['spotServersRunning'] = self.history['spotServersRunning'][1:]
            if len(self.history['totalCost']) > self.plotHistory:
                self.history['totalCost'] = self.history['totalCost'][1:]
            if len(self.history['baselineRequests']) > self.plotHistory:
                self.history['baselineRequests'] = self.history['baselineRequests'][1:]

        return state, totalCost

    def getCost(self, state):
        cost = (float(state['numOperationalServers'][0]) +
                     float(state['numStartingServers'][0])) * self.EC2HourlyPrice + \
                    (float(state['numOperationalServers'][1]) + float(state['numStartingServers'][1])) * self.spotHourlyPrice + \
                    (float(state['maxCPULoad']) > 1.) * (float(state['maxCPULoad']) - 1) * 50. * (state['numOperationalServers'][0] +
                                                                                                  state['numOperationalServers'][1]) * self.overloadCost
        return cost

    def getFeatures(self, state):
        infoFeatures = self.history['maxCPULoad'][-3:] + \
            [float(state['numOperationalServers'][0])] + \
            [float(state['numOperationalServers'][1])] + \
            [float(state['numStartingServers'][0])] + \
            [float(state['numStartingServers'][1])] + \
            [float(self.interface.failureProbabilities[0])] + \
            [float(self.interface.failureProbabilities[1])] + \
            [float(self.EC2HourlyPrice)] + \
            [float(self.spotHourlyPrice)] + \
            [float(self.overloadCost)]

        return infoFeatures

    def estimateBestAction(self, state):
        features = self.getFeatures(state)
        if state['maxCPULoad'] > 0.8: return 0
        if state['maxCPULoad'] < 0.5: return 3
        else: return 2

    def takeAction(self, actionId):
        if actionId == 0: self.interface.startEC2()
        if actionId == 1: self.interface.startSpot()
        if actionId == 3: self.interface.stopEC2()
        if actionId == 4: self.interface.stopSpot()

    def control(self, numSteps = 1000, verbose = 0, delay = 0):
        self.simulationCost = 0
        self.interface.reset()
        state, cost = self.getNextState()
        if verbose >= 4:
            f = open('control_log.csv', 'w')
            f.write('num_requests;num_ec2_running;num_spot_running;num_ec2_starting;num_spot_starting;max_cpu;cost;action\n')
            f.flush()
            os.fsync(f.fileno())

        for step in range(numSteps):
            if delay != 0: time.sleep(delay)
            actionId  = self.estimateBestAction(state)

            self.takeAction(actionId)

            if verbose >= 1:
                print('------------------------------------------------------------')
                print('Step: '+str(step)+', action: '+self.actions[actionId])

            if verbose >= 2:
                print('Servers running: ', state['numOperationalServers'])
                print('Max CPU: '+ str(state['maxCPULoad']))
                print('Cost: ', cost)

            if verbose >= 4:
                f.write(str(state['meanRequests'])+
                        ';'+str(state['numOperationalServers'][0])+
                        ';'+str(state['numOperationalServers'][1])+
                        ';'+str(state['numStartingServers'][0])+
                        ';'+str(state['numStartingServers'][1])+
                        ';'+str(state['maxCPULoad']) +
                        ';'+str(state['maxCPULoad'])+
                        ';'+str(self.actions[actionId])+'\n')
                f.flush()
                os.fsync(f.fileno())

            if verbose >= 5:
                plt.clf()
                fig = plt.gcf()
                fig.canvas.set_window_title('Cloud Simulator')
                self.visualize()

            state, cost = self.getNextState()

        f.close()
        return self.simulationCost

    def visualize(self):
        if self.plotHistory == None: pass
        x = np.array(sorted(-i for i in range(self.plotHistory))) * 5

        plt.subplot(5, 1, 1)
        loadAxis = max(self.history['maxCPULoad'])
        loadAxis = max([loadAxis]+[i*50 for i in list(np.array(self.history['EC2ServersRunning']) + np.array(self.history['spotServersRunning']))])+100
        if loadAxis < 500.0: loadAxis = 500.0
        plt.axis([min(x), 0, 0.0, loadAxis])
        ax = plt.gca()
        ax.set_autoscale_on(False)

        y1 = np.array(self.history['totalRequests'])
        y2 = np.array([i*50 for i in list(np.array(self.history['EC2ServersRunning']) + np.array(self.history['spotServersRunning']))])

        plt.fill_between(x, 0, y1)
        plt.fill_between(x, y1, y2, where=y2>=y1, facecolor='green', interpolate=True)
        plt.fill_between(x, y1, y2, where=y2<=y1, facecolor='red', interpolate=True)

        p1 = plt.Rectangle((0, 0), 1, 1, fc="green")
        p2 = plt.Rectangle((0, 0), 1, 1, fc="blue")
        plt.legend([p1, p2], ["Capacity, RPS", "Load, RPS"], loc=2,prop={'size':10})

        plt.xlabel('Time (minutes)')
        plt.ylabel('Load/Capacity')
        plt.grid(True)

        plt.subplot(5, 1, 2)
        maxCPUAxis = max(self.history['maxCPULoad']) + 0.2
        if maxCPUAxis < 1.0: maxCPUAxis = 1.0
        plt.axis([min(x), 0, 0.0, maxCPUAxis])
        ax = plt.gca()
        ax.set_autoscale_on(False)

        plotCPULoad = np.array(self.history['maxCPULoad'])

        plt.fill_between(x, 0, plotCPULoad, facecolor='green', interpolate=True)
        plt.fill_between(x, 1, plotCPULoad, where=plotCPULoad>=1., facecolor='red', interpolate=True)

        p1 = plt.Rectangle((0, 0), 1, 1, fc="green")
        plt.legend([p1], ["VM Load, %"], loc=2,prop={'size':10})

        plt.xlabel('Time (minutes)')
        plt.ylabel('VM Load (%)')
        plt.grid(True)

        plt.subplot(5, 1, 3)
        maxVMsAxis = max(np.array(self.history['EC2ServersRunning']) + np.array(self.history['spotServersRunning']))+2
        if maxVMsAxis < 9.: maxVMsAxis = 9.
        plt.axis([min(x), 0, 0.0, maxVMsAxis])
        ax = plt.gca()
        ax.set_autoscale_on(False)

        plotEC2ServersRunning = np.array(self.history['EC2ServersRunning'])
        plotSpotServersRunning = np.array(self.history['spotServersRunning'])

        plt.bar(x, plotEC2ServersRunning, color='blue', width=5., edgecolor='blue')
        plt.bar(x, plotSpotServersRunning, color='orange', bottom=plotEC2ServersRunning, width=5., edgecolor='orange')

        p1 = plt.Rectangle((0, 0), 1, 1, fc="orange")
        p2 = plt.Rectangle((0, 0), 1, 1, fc="blue")
        plt.legend([p1, p2], ["Running Spot instances", "Running EC2 instances"], loc=2,prop={'size':10})

        plt.xlabel('Time (minutes)')
        plt.ylabel('Running')
        plt.grid(True)

        plt.subplot(5, 1, 4)
        maxStartingAxis = max(np.array(self.history['EC2ServersStarting']) + np.array(self.history['spotServersStarting']))+2
        if maxStartingAxis < 3.: maxStartingAxis = 3.
        plt.axis([min(x), 0, 0.0, maxStartingAxis])
        ax = plt.gca()
        ax.set_autoscale_on(False)

        plotEC2ServersStarting = np.array(self.history['EC2ServersStarting'])
        plotSpotServersStarting = np.array(self.history['spotServersStarting'])

        plt.bar(x, plotEC2ServersStarting, color='blue', width=5., edgecolor='blue')
        plt.bar(x, plotSpotServersStarting, color='orange', bottom=plotEC2ServersStarting, width=5., edgecolor='orange')

        p1 = plt.Rectangle((0, 0), 1, 1, fc="orange")
        p2 = plt.Rectangle((0, 0), 1, 1, fc="blue")
        plt.legend([p1, p2], ["Starting Spot instances", "Starting EC2 instances"], loc=2,prop={'size':10})

        plt.xlabel('Time (minutes)')
        plt.ylabel('Starting')
        plt.grid(True)

        plt.subplot(5, 1, 5)
        costAxis = max(self.history['totalCost'])+0.2
        if costAxis < 0.5: costAxis = 0.5
        plt.axis([min(x), 0, 0.0, costAxis])
        ax = plt.gca()
        ax.set_autoscale_on(False)

        plotTotalCost = np.array(self.history['totalCost'])
        plt.plot(x, plotTotalCost)

        p1 = plt.Rectangle((0, 0), 1, 1, fc="blue")
        plt.legend([p1], ["Cloud infrastructure cost, $"], loc=2,prop={'size':10})

        plt.xlabel('Time (minutes)')
        plt.ylabel('Cost, $')
        plt.grid(True)

        plt.draw()
        plt.pause(0.0001)