# Verilator Python Wrapper

An example project that provides a Python wrapper around a Verilatlated module
and builds a complex testbench around it.

## Build and Run

```bash
./example.py
```

The testbench script in combination with the *vpw* package will take the
SystemVerilog RTL files within the 'hdl' directory and creates a pybind11
shared object that is then used by the testbench script to interact with the
module.

## Documentation

Explanation of use can be found [here](https://bmartini.github.io/vpw-testbench).
