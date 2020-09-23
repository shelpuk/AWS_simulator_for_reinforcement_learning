# AWS simulator for reinforcement learning
![Python versions: 3.4, 3.5, 3.6](https://img.shields.io/pypi/pyversions/Django.svg) ![Status: stable](https://img.shields.io/pypi/status/Django.svg) ![License: MIT](https://img.shields.io/apm/l/vim-mode.svg)

This is AWS virtual infrastructure simulator for building automated infrastructure control systems. It is primarily designed for training reinforcement learning controllers but could be used for any other approaches. In 2016, Google DeepMind built a system for a [similar problem of managing datacenter capacity](https://deepmind.com/blog/deepmind-ai-reduces-google-data-centre-cooling-bill-40/).

The business case simulated is the following. You have an application such as an e-commerce website or online game and host it on AWS. You use AWS [EC2](https://aws.amazon.com/ec2/) and [Spot](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-spot-instances-work.html) instances. They all are located behind [AWS load balancer](https://aws.amazon.com/elasticloadbalancing/) so that you can increase or shrink your cloud capacity.

However, there are many uncertainties there. 
- The instance becomes operational in roughly 20 min but not exactly, each time this time varies a little bit because of the internal dynamics of AWS virtualization software.
- Sometimes, the instance fails. You never know when exactly that happens.
- You never know how many requests, exactly, will come from your users in the next minute.
- Spot instances are cheap, but they can be taken away from you any time if someone offers a better price. The demand for Spots varies over time, so the probability of Spot instance failure changes over time.

The simulator simulates running such a setup with all these uncertainties. You can run it in an automated mode where the simulation takes a traffic pattern from a real cloud application or in a manual mode where you can control these uncertainties with a simple user interface.
![picture alt](https://github.com/shelpuk/AWS_simulator_for_reinforcement_learning/blob/master/img/Cloud_Simulator.png)

## How to start
To start, please download the repository and run:
```console
$ python control.py
```

You can also run the controller from the inside of your own code. To do that, you need to specify a simulator as an interface to AWS cloud and define if you want to simulate the behavior of a real cloud application which is provided along with the simulator ()

```python
from simulator import interfaceSimulator
import controller

generator = interfaceSimulator(files=['data/full_balancer_model_normal.csv'], #a file describing user behavior
                               timeframe=10, #number of minutes per simulator step
                               initialServers=[4,4]) #initial number of EC2 and Spot virtual machines
                                         
ctrl = controller.controller(interface=generator, #interface to the AWS cloud or a simulator
                             plotHistory = 30, #number of steps to be shown on a plot
                             mode='A') #the mode of operation

ctrl.control(numSteps=50000, #number of steps to run
             verbose=5, #how much of information to show
             delay=0.) #additional delays between steps
```

If you create a `controller` object with `mode='M'`, the system will give you a visual "Cloud Controller" control interface to control the simulation manually in real-time.
![picture alt](https://github.com/shelpuk/AWS_simulator_for_reinforcement_learning/blob/master/img/Cloud_Controller.png)

## How to write your own control logic
Here are the methods of the controller that you may need to implement your own control logic.

- **controller.control()** - starts the simulation under the control of your algorithm.
- **controller.takeAction()** - performs one of the possible actions for cloud infrastructure management.
- **controller.getNextState()** - performs one simulation step. Returns the state of the infrastructure after taking action.
- **controller.getCost()** - returns the received reward (in our case, it will be a negative reward - the money spent on the system).
- **controller.getFeatures()** - returns the features of the state and action. Here you can define the features your model will use.
- **controller.estimateBestAction()** - returns the action to take for every state.
- **controller.setSpotFailureProbability()** - sets the Spot instance failure probability. The probability is the same for all Spot instances.
- **controller.setSpotHourlyPrice()** - sets the hourly cost for Spot instances. The price is the same for all Spot instances.
- **controller.setOverloadCost()** - sets the penalty for one user request that will be delayed or not processed due to your infrastructure's overloading. Here, the penalty should be set in the same currency as the price of the instance.

You can start with the controller.estimateBestAction () method. It implements a simple control algorithm that starts one EC2 machine if the load utilizes more than 80% of the current resources are and stops one EC2 machine if the load falls below 50%. Otherwise, it does nothing.

This simulator supports all possible reinforcement learning algorithms, including [deep reinforcement learning](https://deepmind.com/blog/article/deep-reinforcement-learning) and [PEGASUS](https://ai.stanford.edu/~ang/papers/uai00-pegasus.pdf).

## Components
The environment consists of the following components.
- **interfaceSimulator.py** implements a simulator of AWS infrastructure, including all uncertainties described above.
- **controller.py** implements control logic.
- **full_balancer_model_normal.csv** contains data for simulating load on your application in requests per second. The system generates the number of requests to this system from users every minute. This file stores the historical average number of requests for each minute of the day, and the standard deviation of that value.
- **control.py** is a script for running the simulation.

## License
MIT License. Copyright (c) 2018 Sergii Shelpuk.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
