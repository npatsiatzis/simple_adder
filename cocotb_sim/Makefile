# Makefile

# defaults
SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl
EXTRA_ARGS += --std=08
SIM_ARGS += --wave=wave.ghw

VHDL_SOURCES += $(PWD)/../rtl/VHDL/adder.vhd
# use VHDL_SOURCES for VHDL files

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
# MODULE is the basename of the Python test file

#PYTHPNPATH is an environment variable that can be set to additional directories
#where python will look for modules and packages
export PYTHONPATH := $(PWD)/../model:$(PYTHONPATH)

test_adder:
		$(MAKE) sim MODULE=tb_adder TOPLEVEL=adder

lint: $(VHDL_SOURCES)
	vsg --style jcl -f $^
	
documentation:
		doxygen 

clean_dir:
		rm -f wave.*
		rm -f *.o 
		rm -f *.xml
		find . -maxdepth 1 -type f -executable -exec rm {} +
		find -mindepth 1 -maxdepth 1 -type d -print0 | xargs -r0 rm -R
# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim