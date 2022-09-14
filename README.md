# ovladacka
ovladacka is a simple tool to control [wallckr](https://github.com/ladapn/wallckr) mobile robot and to receive, process and store data the robot sends back. 

## Getting Started
### Clone this repository
`$ git clone TBD`
### Install dependencies
`$ pip install -r requirements.txt`
### Configure robot connection
NOTE: if you wish to work only in simulation mode, you can skip this part
Create a copy of `connection.json.TEMPLATE` file and delete the `.TEMPLATE` suffix from the name of your copy. 
Open your copy and fill in the information about the required connection type. 
### Run it
#### Normal mode 
#### Simulation mode

## Deta exchange with robot
### Data sent from ovladacka to robot
### Data sent from robot to ovladacka

## Known issues
### Wayland issues
ovladacka uses pynput package to capture keyboard and pynput does not seem to work on Wayland

Workaround: use Xorg instead 

## Contributing

## License