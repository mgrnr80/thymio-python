# thymio-python

Python package to control a [Thymio II robot](https://thymio.org) from a Python process via serial protocol. Currently the Thymio firmware does't permit to drive leds by setting variables in data space, instead leds are controlled via native functions. So a protocol has been implemented to trigger native function invocations by writing appropriate variables in data space.

> This project includes code originally developed by  
> **ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Miniature Mobile Robots group, Switzerland**.
