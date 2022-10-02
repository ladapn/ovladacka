# ovladacka
ovladacka is a simple tool to control [wallckr](https://github.com/ladapn/wallckr) mobile robot and to receive, process and store data the robot sends back. 

## Getting Started
### Clone this repository
`$ git clone https://github.com/ladapn/ovladacka.git`
### Install dependencies
`$ pip install -r requirements.txt`
### Configure robot connection
NOTE: if you wish to work only in simulation mode, you can skip this part

Create a copy of `connection.json.TEMPLATE` file and delete the `.TEMPLATE` suffix from the name of your copy. 
Open your copy and fill in the information about the required connection type. 
### Run it
#### Normal mode
`$ python ovladacka.py`
#### Simulation mode
Coming soon... 

## Deta exchange with robot
### Data sent from ovladacka to robot
ovladacka captures keyboard and turns certain keystrokes to commands for the robot. 

| Key         | Robot Command                            |
|-------------|------------------------------------------|
| Up arrow    | Increase speed by one step               |
| Down arrow  | Decrease speed by one step               |
| Left arrow  | Turn front wheels one step left*         |
| Right arrow | Turn front wheels one step right*        |
| Space | Center front wheels*                     |
| Left Shift | Disable/Enable automatic operation       |
| Escape | Disconnect from robot and quit ovladacka |

\* will be overwritten when automatic operation enabled.

Other keys are ignored. 

### Data sent from robot to ovladacka
Robot sends asynchronously various data such as sensor measurements, information about its status etc. The data is 
divided into simple packets. These packets are received, decoded and writen to files. Only packets defined in 
[packet_definition.json](packet_definition.json) are considered. More information about this file can be found 
[here](doc/packet_definition.md). 

## Known issues
### Wayland issues
ovladacka uses pynput package to capture keyboard and pynput does not seem to work on Wayland

Workaround: use Xorg instead 

## TODO
- implement simulation mode so that ovladacka can be run without connection to the actual robot

## Contributing
In case you would like to fix or improve anything, feel free to create a pull request. 

## License
This project is licensed under the MIT license.