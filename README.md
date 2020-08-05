# cmap
If you want to you can try to see if you can get info from a car using this.

It's not good code, it isn't likely to work with your car, and has so many issues that it's not worth submitting bug reports!

The idea behind this is to scan your car for nodes, then scan the nodes for diagnostic services, then scan some of the known services for subfunctions

It is tested on one car, it doesn't have a command line interface yet, maybe never will. It doesn't log yet, maybe never will...

Think of this as a template to how you should scan your car using the CAN Bus.

Currently it supports Socket CAN.  So if your CAN Bus device is a socket can device, booom! You got this.

It defaults to 'can0' but you should be able to change to the desired interface.

It is only tested on one car.  It worked.  Please let me know how it goes.  Love to see what you find!
