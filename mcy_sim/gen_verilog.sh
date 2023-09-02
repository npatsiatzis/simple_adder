#!/bin/bash

yosys -m ghdl -p 'ghdl --std=08 adder.vhd -e adder; write_verilog adder.v'