# DRAMA
**DRA**M Si**m**ul**a**tor

In order to run DRAMA, you must have python 3 with the following packages:
* os
* subprocess
* math
* configparser
* tqdm
* absl-py

## DRAMA+ScaleSim
In this folder you can find the full implementation of DRAMA linked to Scale-Sim.

Link to SCALE-Sim: https://github.com/ARM-software/SCALE-Sim

### Getting Started
1. Create a .cfg file inside 'configs' to define a new architecture for the network and DRAM. Architecture presets are used to define SCALE-Sim parameters, while DRAM preset are used to define DRAMA parameters.
2. Create a .csv file inside 'topologies' to define the topology of the network, as used by SCALE-Sim.
3. From within the 'DRAMA+ScaleSim' folder, run the following line:

Python3 scale.py -arch_config=\<path to config> -network=\<path to topology>

### DRAMA Outputs
DRAMA outputs can be found under the path 'outputs/\<run name>/DRAMA_stats

1. **\<run name>_DRAMA_dram_stats.csv** - general DRAM statistics grouped by network layer and DRAM channel.
2. **\<run name>_\<layer name>_DRAMA_dram_requests_trace.csv** - cycle accurate DRAM request traces per network layer.
  

## Channnel Simulator
In this folder you can find an implementation of a channel instance which can be incorporated in your code, using 3 simple methods:
* __init__ - used to instantiate a single channel
* __request__ - used to send a read/write request to the channel
* __incrementClock__ - used to increment the channel's internal clock to a desired time

Further documentation for these methods can be found in Channel.py
