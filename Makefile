.PHONY: all
all: testbench

NAME=example
CLOCK=clk

VERILATOR_ROOT ?= $(shell bash -c 'verilator -V | grep VERILATOR_ROOT | head -1 | sed -e "s/^.*=\s*//"')
VINC := $(VERILATOR_ROOT)/include
PYINC := $(shell bash -c 'python3 -m pybind11 --includes')
OUTPUT := $(NAME)$(shell bash -c 'python3-config --extension-suffix')


$(NAME)/V$(NAME).cpp: hdl/$(NAME).sv
	verilator -Mdir $(NAME) -CFLAGS "-fPIC -std=c++17" -I./hdl --trace -cc ./hdl/$(NAME).sv

$(NAME)/V$(NAME)__ALL.a: $(NAME)/V$(NAME).cpp
	make --no-print-directory -C $(NAME) -f V$(NAME).mk

testbench : $(NAME)/$(NAME).cc $(NAME)/V$(NAME)__ALL.a
	g++ -O3 -D NAME=$(NAME) -D CLOCK=$(CLOCK) -Wall -shared -std=c++17 \
		-fPIC $(PYINC) -I. -I$(VINC) -I$(NAME) $(VINC)/verilated.cpp \
		$(VINC)/verilated_vcd_c.cpp $(NAME)/$(NAME).cc \
		$(NAME)/V$(NAME)__ALL.a -o $(OUTPUT)

.PHONY: clean
clean:
	rm -rf $(NAME)/ $(OUTPUT) $(NAME).vcd
