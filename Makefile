.PHONY: all
all: testbench

NAME=example
CLOCK=clk

VERILATOR_ROOT ?= $(shell bash -c 'verilator -V | grep VERILATOR_ROOT | head -1 | sed -e "s/^.*=\s*//"')
VINC := $(VERILATOR_ROOT)/include
PYINC := $(shell bash -c 'python3 -m pybind11 --includes')
OUTPUT := testbench$(shell bash -c 'python3-config --extension-suffix')


obj_dir/V$(NAME).cpp: hdl/$(NAME).sv
	verilator -CFLAGS "-fPIC -std=c++17" -I./hdl --trace -cc ./hdl/$(NAME).sv

obj_dir/V$(NAME)__ALL.a: obj_dir/V$(NAME).cpp
	make --no-print-directory -C obj_dir -f V$(NAME).mk

testbench : obj_dir/$(NAME).cc obj_dir/V$(NAME)__ALL.a
	g++ -O3 -D CLOCK=$(CLOCK) -Wall -shared -std=c++17 -fPIC $(PYINC) \
		-I. -I$(VINC) -Iobj_dir $(VINC)/verilated.cpp \
		$(VINC)/verilated_vcd_c.cpp obj_dir/$(NAME).cc \
		obj_dir/V$(NAME)__ALL.a -o $(OUTPUT)

.PHONY: clean
clean:
	rm -rf obj_dir/ $(OUTPUT) testbench.vcd
