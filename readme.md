# END4TRAIN project
## Development
To correctly set up everything for development, all environmental variables in
`end4train.config.app.EnvVariable` enum should be defined.  
For paths, use absolute paths pointing to the corresponding locations
in your local filesystem.  
(TODO: write install scripts in bash and PowerShell to set up developement environment automatically)


## Head of Train
### Head PC (HPC) software
Code is separated into two folders:
1. **backend** - deals with communication with Head of Train (HoT) Controller over TCP.
Processes inputs and elaborates the train integrity status.
2. **frontend** - displays data received by backend in a GUI, takes user input and sends it
to the DAQ for further processing