#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <vector>

using namespace pybind11::literals;
namespace py = pybind11;

#define STRING(s) #s
#define STRINGIFY(s) STRING(s)

#ifndef PACKAGE
#define PACKAGE testbench
#endif

#ifndef CLOCK
#define CLOCK clk
#endif

TB *dut;
VerilatedVcdC *wave;
vluint64_t timestamp;
bool trace_on;

void prep(const std::string, const std::vector<uint64_t> &);

py::dict update();

void init(const bool trace = true) {
  timestamp = 0;
  trace_on = trace;

  // Instantiate design
  dut = new TB;

  if (trace_on) {
    // Generate a trace
    Verilated::traceEverOn(true);
    wave = new VerilatedVcdC;
    dut->trace(wave, 99);
    wave->open(STRINGIFY(PACKAGE.vcd));
  }
}

void finish() {
  if (trace_on) {
    wave->close();
  }

  delete dut;
}

py::dict tick() {
  timestamp++;

  dut->eval();
  if (trace_on) {
    wave->dump(timestamp * 10 - 2);
  }

  py::dict IO = update();

  dut->CLOCK = 1;
  dut->eval();
  if (trace_on) {
    wave->dump(timestamp * 10);
  }

  dut->CLOCK = 0;
  dut->eval();
  if (trace_on) {
    wave->dump(timestamp * 10 + 5);
    wave->flush();
  }

  return IO;
}

PYBIND11_MODULE(PACKAGE, m) {
  m.doc() = "Python interface for a Verilator Design Under Test (dut)";

  m.def("init", &init, "Initialize DUT simulation", py::arg("trace") = true);
  m.def("finish", &finish, "Finish DUT simulation");
  m.def("prep", &prep, "Prepare input values to be sampled on next posedge");
  m.def("tick", &tick,
        "Advances the clock one cycle and returns the port list state as it "
        "was on the posedge");
}
