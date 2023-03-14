# ME 405 Term Project: Nerf Sentry Turret

Group: Mecha15
Sean Wahl, Nathan Dodd, Lewis Kanagy

## Overview

The goal of the Nerf Sentry Turret project is to learn by doing some of the most importnat topics in ME 405. These topics include 
designing systems of modest complexity with both mechanical and electrical components, using control systems to operate mechanical systems, and 
organizing software into discrete modules to call between python files. 

The project entails the consturction and calibration of a thermal sensing target acquisition system that can launch a projectile beyond 
16 feet. The team must use a given thermal camera, STM32 MCU Unit, and a selected Nerf launcher to "duel" an opposing team. The teams are 
placed 16 feet apart, and upon a "Start" signal, the opposing systems must rotate 180 degrees using mechanical components, gather thermal data through I2C communication,
and use electical components to fire the launcher.





## Task Diagram
![Task Diagram](./images/task_diagram.png)

## State Transition Diagrams
![Task Diagram](./images/controller_motor_states.png)

![Task Diagram](./images/encoder_states.png)

![Task Diagram](./images/nerf_states.png)

![Task Diagram](./images/camera_states.png)
