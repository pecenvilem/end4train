# END4TRAIN project
## Head of Train
### Head PC (HPC) software
Code is separated into two folders:
1. **backend** - deals with communication with Head of Train (HoT) Controller over TCP.
Processes inputs and elaborates the train integrity status.
2. **frontend** - displays data received by backend in a GUI, takes user input and sends it
to the DAQ for further processing