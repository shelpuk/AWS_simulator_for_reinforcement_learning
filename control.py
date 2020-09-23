from simulator import interfaceSimulator
import controller

# Generator is a simulator interface of AWS cloud management. To set up the simulator
# you need a data describing event probability.
#
# When setting up the simulator, you also describe the timeframe (how often the system checks the status
# of the infrastructure, minutes) and the initial number of virtual machines (VMs) of both types (EC2 and Spot).

generator = interfaceSimulator(files=['data/full_balancer_model_normal.csv'], #interface to the AWS cloud or a simulator
                               timeframe=10, #number of steps to be shown on a plot
                               initialServers=[4,4]) #initial number of virtual machines (VMs) of both types (EC2 and Spot)

# Controller is a class implementing infrastructure control logic. It requires an interface to
# the AWS cloud management (here, the simulator), number of steps you want it to collect historical records
# for visualization.
#
# For this exercise, you should also specify the mode of the simulator. In manual mode (mode='M')
# you control the simulation on your own. In automatic mode (mode='A'), the simulator simulates
# the system using the control logic from the controller.

ctrl = controller.controller(interface=generator, #number of steps to run
                             plotHistory=30, #how much of information to show
                             mode='M') #the mode of the simulator

# After the controller is set up, you can run it by using the control() method. The control () method requires the
# number of steps to run, verbose (how much debug data to show), and the delay between steps. If the system runs too
# fast for you, you can slow it down by increasing the delay.

ctrl.control(numSteps=50000, verbose=5, delay=0.)
