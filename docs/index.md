# Introduction

The pybind11 DUT python packages creates a low level interface to a
Verilatlated module consisting of 4 standardized functions. This DUT package
can be passed to the *vpw* package where it is used in creating higher level
interfaces to the module.


## Low level functions

These functions are auto generated with the testbench package when it creates
the pybind11 object encapsulating the Verilated module.

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

## A. Simple Mid Level BRAM interaction

Using the mid-level interface provided by the *vpw* package, functions are
created to more easily set the values of the modules inputs. The values are
applied to the port list variables during a clock 'tick' and the *vpw* tick
function returns the values of all port list variable (both inputs and outputs)
in the form of a python Dict object there the variables number is used as a key
to its value.

## B. Simple High Level BRAM interface

Creating a high level write/read interface to the BRAM. A generator class is
created for both the write and read buses. The classes are required to
implements an 'init' function that is used by the background infrastructure.
The class 'init' is a generator function what will apply initial values to the
interface signals when 'registered' to the background infrastructure. There is
a loop implemented within the class 'init' function, a yield pauses the loop
and is only released after a system 'tick'.

