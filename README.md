# Slime Simulator

![Main branch workflow](https://github.com/nothinn/SlimeSimulator/actions/workflows/scala.yml/badge.svg)


This repo attempts to create a real-time slime simulation running on an FPGA.

The original idea was from the YouTube video of Sebastian Lague: https://www.youtube.com/watch?v=X-iSQQgOd1A.

That video was based on this paper: https://uwe-repository.worktribe.com/output/980579


# Overview

The hardware is based on an external memory that needs to be able to contain the following
* An array of agents. 
* A trail map
* A diffused trail map

Each agent contains an x/y location from 0 to width/height of image.
They also contain some settings such as speed and species index.

The trail map is a width*height array that contains the trail of the slime.

The diffused trail map is the same as the trail map but calculated as a diffused version.

## Kernels
The calculations done are based on a number of identical kernels that requests memory and then stores the result in memory. Each kernel will have a FIFO or other type of buffer to store *n* agents ready for calculation. When no more agents are available in that epoch, the kernels will switch over to diffuse the trail map.


The agents have two stages that needs to be performed by the kernels
* Motor stage
	* Attempt move forward in current direction
	* if (moved forward successfully)
		* Deposit trail in new location
	* else
		* Choose random new orientation
* Sensory stage
	* Sample trail map values
	* if (F > FL) && (F > FR)
		* Stay facing same direciton
		* Return
	* Else if (F < FL) && (F < FR)
		* Rotate randomly left or right by RA
	* Else if (FL < FR)
		* Rotate right by RA
	* Else if (FR < FL)
		* Rotate left by RA
	* Else
		Continue facing same direction

## Memory
The calculations are bandwidth heavy, as each agent needs to do some simple calculations on the trail map based on an agents position and settings. The idea for the memory organization is to have one or more memory read requests from each kernel and then either do a majority vote of which address to read or do a lowest address read. Every memory request then needs to verify that the read address is the one they requested.

By doing a lowest address prioritization, it should be possible for the kernels to filter the agents memory reads to match that of all other agents.

## Agents
Each agent needs access to the trail map in a special location. Once an agent has moved around a lot, it will no longer be spatially local. That is, consecutive agents will probably not need to read the same parts of the trail map. To overcome this, it might be beneficial to do a sorting on the agents. However, it might be faster to just read all agents multiple times.


## Results
The goal for the project is to have a video output of a slime simulation. This should be done standalone through VGA/HDMI or other video output. 

For validation/verification, the system also needs to be able to output the contents of the memory. That is, it needs to be able to pause the system after an iteration and upload it to a computer. This can be done through UART/ethernet or other interfaces. The computer can then perform the same calculations to verify that the FPGA does indeed calculate everything correct.
