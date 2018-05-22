# AWS simulator for reinforcement learning
![Python versions: 3.4, 3.5, 3.6](https://img.shields.io/pypi/pyversions/Django.svg) ![Status: stable](https://img.shields.io/pypi/status/Django.svg) ![License: MIT](https://img.shields.io/apm/l/vim-mode.svg)

This is AWS virtual infrastructure simulator for building automated infrastructure control systems. Primarily it is designed for training reinforcement learning controllers but could be used for any other approaches as well.

This is AWS virtual infrastructure simulator for building automated infrastructure control systems. Primarily it is designed for training reinforcement learning controllers but could be used for any other approaches as well. This simulator was used by a startup company QRhythm for training its AWS capacity management system.

The business case simulated is the following. You have an application such as e-commerce web-site or online game and host it on AWS. You use AWS [EC2](https://aws.amazon.com/ec2/) and [Spot](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-spot-instances-work.html) instances. They all are located behind [AWS load balancer](https://aws.amazon.com/elasticloadbalancing/) so that you can increase or shrink your cloud capacity.

However, there are a number of uncertainties there. 
- The instance becomes operational in roughly 20 min but not exactly, each time this time vary a little bit because of the internal dynamics of AWS virtualization software.
- Sometimes the instance fails. You never know when exactly that happens.
- You never know how many requests, exactly, will come from your users in the next minute.
- Spot instances are cheap but they can be taken away from you any time if someone offers a better price. The demand for Spots vary over time so the probability of Spot instance failure changes over time.

The simulator simulates running such a setup with all these uncertainties. You can run it in automated mode where the simulation takes a traffic pattern from a real cloud application or in a manual mode where you can control these uncertainties with simple user interface.
![picture alt](https://github.com/shelpuk/AWS_simulator_for_reinforcement_learning/blob/master/img/Cloud_Simulator.png)

## How to start
To start, please download the repository and run:
```console
$ python control.py
```

You can also run the controller from the inside of your own code. In order to do that you need to specify a simulator as an interface to AWS cloud and define if you want to simulate the behavior of a real cloud application which is provided along with the simulator ()

```python
from simulator import interfaceSimulator
import controller

generator = interfaceSimulator(files=['data/full_balancer_model_normal.csv'], #a file or files describing user behavior
                                         timeframe=10, #number of minutes per simulator step
                                         initialServers=[4,4]) #initial number of EC2 and Spot virtual machines
                                         
ctrl = controller.controller(interface=generator, #interface to the AWS cloud or a simulator
                             plotHistory = 30, #number of steps to be shown on a plot
                             mode='A') #the mode of operation

ctrl.control(numSteps=50000, #number of steps to run
             verbose=5, #how much of information to show
             delay=0.) #additional delays between steps
```

## Components
The environment consists of the following components.
- **interfaceSimulator.py** implements simulator of AWS infrastructure including all uncertainties described above.
- **controller.py** implements control logic. Predefine for using reinforcement learning controller.
- **full_balancer_model_normal.csv** contains a data for simulating load on your application in requests per second.
- **control.py** is a script for running the simulation.

## Useful methods
You may need the following methods in order to 
