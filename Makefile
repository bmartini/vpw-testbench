.PHONY: all
all: testbench

TOP=example
VERILATOR_ROOT ?= $(shell bash -c 'verilator -V | grep VERILATOR_ROOT | head -1 | sed -e "s/^.*=\s*//"')
VINC := $(VERILATOR_ROOT)/include
PYINC := $(shell bash -c 'python3 -m pybind11 --includes')
OUTPUT := testbench$(shell bash -c 'python3-config --extension-suffix')


obj_dir/V$(TOP).cpp: hdl/$(TOP).sv
	verilator -CFLAGS "-fPIC -std=c++17" -I./hdl --trace -cc ./hdl/$(TOP).sv

obj_dir/V$(TOP)__ALL.a: obj_dir/V$(TOP).cpp
	make --no-print-directory -C obj_dir -f V$(TOP).mk

testbench : obj_dir/$(TOP).cc obj_dir/V$(TOP)__ALL.a
	g++ -O3 -Wall -shared -std=c++17 -fPIC $(PYINC) -I. \
		-I$(VINC) -Iobj_dir $(VINC)/verilated.cpp \
		$(VINC)/verilated_vcd_c.cpp obj_dir/$(TOP).cc \
		obj_dir/V$(TOP)__ALL.a -o $(OUTPUT)

.PHONY: clean
clean:
	rm -rf obj_dir/ $(OUTPUT) testbench.vcd
