# Introduction

VPW uses pybind11 and Verilator to create a python object that allows for the
easy building of cycle accurate testbenchs of SystemVerilog modules. The design
under test (DUT) python object presents a low level interface to a Verilatlated
module consisting of 4 standardized functions. This DUT object can be passed to
the *vpw* package where it can be used in creating higher level interfaces to
the module.

Creating the DUT object used in simulations is done via the *vpw.create*
function. The arguments to the *create* function are as follows:

1. __package__ Name of the DUT package to be created.
2. __module__ Name of the SystemVerilog module to by simulated.
3. __clock__ Name of the module clock if not the default 'clk'.
4. __include__ List of directories that contain SystemVerilog modules.
5. __parameter__ Dict of parameters and values to be passed to module.
5. __define__ Dict of Verilog macro defines used to pre-process the module.

```python
dut = vpw.create(package='test1',
                 module='testbench',
                 clock='clock',
                 include=['../hdl', '../test'],
                 parameter={'MEM_DWIDTH': 128,
                            'MEM_AWIDTH': 8},
                 define={'SIM': None})
```


## Low level functions

These functions are auto generated with the DUT testbench object when it is
created.

### init/finish

Setup and tear down functions.

### prep

Equivalent to non-blocking assignment.

### tick

Passes the port list values to the module and returns a IO list containing the
port list values (inputs/outputs) as they looked on the rising positive edge of
the clock.

## Mid level functions

The *vpw* package wraps the above low level functions and provide the same
functionality, but also augments and enables additional utility functions.

### pack/unpack

The 'pack' function takes a python Large Integer that will be applied to a data
bus with a greater then 64 bit width and splits it into a List of 32 bit
numbers used by the low-level prep function.

The 'unpack' function takes a List of numbers and undos the 'pack' function to
return a python Large Integer.

### register

Used to register a long lived 'task' that controls a set of port list
variables. With each 'tick' of the modules clock a task is asked to apply a
value to its port list variable. These tasks are used to create the high level
interfaces.

### Override tick

If any background tasks have been registered, this *tick* function should be
used instead of the low level *tick* as the mid level function ensures the
registered background tasks are progressed by one clock cycle.

### Override init/finish

Convenience functions that simply call the low level functions.

### Override prep

Convenience function that simply calls the low level *prep* function.


## High level interactions

A grouping of interdependent signals is defined as a bus interface. Within
*vpw* an interface will often be encapsulated and driven by a generator
function or class called a 'task'. A properly constructed generator can be
registered to run in the background and its actions stepped though with each
tick of the clock. Examples of these high level interfaces are the AXIS and
AXIM classes within the *vpw* package.


# Tutorial 1

This tutorial will walk though creating a testbench for controlling a simple
BRAM module.

## A. Simple Low Level BRAM interaction

Using the low-level interface provided by the *dut* object. Module input ports
have their values assigned in a non-blocking manner with the *prep* function
and the clock progressed on cycle with the *tick* function.

## B. Simple Mid Level BRAM interaction

Using the mid-level interface provided by the *vpw* package, functions are
created to more easily set the values of the modules inputs. The values are
applied to the port list variables during a clock 'tick' and the *vpw* tick
function returns the values of all port list variable (both inputs and outputs)
in the form of a python Dict object where the port name is used as a key to its
value.

## C. Simple High Level BRAM interface

Creating a high level write/read interface to the BRAM. A generator class is
created for both the write and read buses. The classes are required to
implements an 'init' function that is used by the background infrastructure.
The class 'init' is a generator function that will apply initial values to the
interface signals when 'registered' to the background infrastructure. There is
a loop implemented within the class 'init' function, a yield pauses the loop
and is only released after a system 'tick'.


# Tutorial 2

This tutorial walks though creating AXIS high level interfaces. These
interfaces are similar to what can be found in *vpw.axis* package but slightly
simplified for clarity. Also included is a AXIS protocol checker that monitors
both the down stream and up stream interfaces of the DUT. This checker is
registered as a background task and will assert if its assigned interface
behaves contrary to the AXIS spec.

