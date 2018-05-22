# AWS_simulator_for_reinforcement_learning

This is AWS virtual infrastructure simulator for building automated infrastructure control systems. Primarily it is designed for training reinforcement learning controllers but could be used for any other approaches as well.

This is AWS virtual infrastructure simulator for building automated infrastructure control systems. Primarily it is designed for training reinforcement learning controllers but could be used for any other approaches as well. This simulator was used by a startup company QRhythm for training its AWS capacity management system.

The business case simulated is the following. You have an application such as e-commerce web-site or online game and host it on AWS. You use AWS EC2 and Spot instances. They all are located behind AWS load balancer so that you can increase or shrink your cloud capacity.

However, there are a number of uncertainties there. 
- The instance becomes operational in roughly 20 min but not exactly, each time this time vary a little bit because of the internal dynamics of AWS virtualization software.
- Sometimes the instance fails. You never know when exactly that happens.
- You never know how many requests, exactly, will come from your users in the next minute.
- Spot instances are cheap but they can be taken away from you any time if someone offers a better price. The demand for Spots vary over time so the probability of Spot instance failure changes over time.
