# packet_definition.json structure
This file defines information needed to parse, process and write to a file data packets received from the robot. Let's 
explain its content based on a simple example. 
```
[
  {
    "id" : [100, 101, 102, 103],
    "name" : "ultrasound",
    "structure" : "<BIIB",
    "length" : 10,
    "writer" : "ultrasound"
  },
  {
    "id" : [80],
    "name" : "status",
    "structure" : "<BIIHHHB",
    "length" : 16,
    "header" : ["id", "tick_ms", "commit_id", "battery_v_adc", "total_i_adc", "motor_i_adc", "crc"],
    "writer" : "generic"
  }
]
```
## id
List of packet ids sharing below defined information
## name
Name of the packet or group of packets. It is used as a suffix for the name of the file to hold packet data. 
## structure
Recipe how to parse the actual packet. Syntax of Python's struct module is used - see [https://docs.python.org/3/library/struct.html#format-strings](https://docs.python.org/3/library/struct.html#format-strings)

## length
Length of the packet data - total number of bytes a packet consists of.   

## header
Names of columns of the output csv file to hold parsed packet data.
NOTE: this is a mandatory field when using "generic" writer, and optional if using "ultrasound" writer. 

## writer
Class to process and write raw packet data. Currently, the following classes are defined:
1. "ultrasound"
   - Aggregates all measurement from ultrasound distance sensor packets (ids 100 to 103) together, computes minimum of 
value of side pointing sensors and puts all these data into one output file. 
2. "generic"
   - Breaks packet down according to "structure" field and puts resulting values to separate columns of a csv file. No
further processing is performed. 

# Adding new packet
As long as breaking packet down into individual fields and putting the result into a csv file is sufficient, use packet 
id 80 from the example above as a template. In such a case no changes to source code are needed. 

In case more advance processing is needed, new writer class has to be implemented in data_writers.packet_writer. 


