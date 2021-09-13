# Verilator Python Wrapper

An example project that provides a Python wrapper around a Verilatlated module
and builds a complex testbench around it.

## Build and Run

```bash
./build.py
./example.py
```

The *build.py* script in combination with the Makefile Verilates the
SystemVerilog RTL files within the 'hdl' directory and creates a pybind11
shared object that can be imported into a Python script. More details on how to
use *build.py* can be found using the '--help' option.

```bash
./build.py --help
```

Once the shared object is built the *example.py* testbench script can be
updated and run any number of times. However, if the RTL is updated the
*build.py* script must be rerun and the shared object recreated before the
changes can be observed.

## Documentation

Explanation of use can be found [here](https://bmartini.github.io/vpw-testbench).
