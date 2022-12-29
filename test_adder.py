from cocotb_test.simulator import run
import pytest
import os

vhdl_compile_args = "--std=08"
sim_args = "--wave=wave.ghw"


tests_dir = os.path.abspath(os.path.dirname(__file__)) #gives the path to the test(current) directory in which this test.py file is placed
rtl_dir = tests_dir                                    #path to hdl folder where .vhdd files are placed
model_dir = os.path.join(tests_dir, "model")

module = "testbench"
toplevel = "adder"   
vhdl_sources = [
    os.path.join(rtl_dir, "adder.vhd"),
    ]

                                   
#run tests with length generic values for the add operands data width
@pytest.mark.parametrize("parameter", [{"g_data_width": str(i)} for i in range(3,6,1)])
def test(parameter):



    run(
        python_search=[tests_dir,model_dir],                         #where to search for all the python test files
        vhdl_sources=vhdl_sources,
        toplevel=toplevel,
        module=module,

        vhdl_compile_args=[vhdl_compile_args],
   		toplevel_lang="vhdl",
        parameters=parameter,                              #parameter dictionary
   		extra_env=parameter,
        sim_build="sim_build/"
        + "_".join(("{}={}".format(*i) for i in parameter.items())),
    )

    if __name__ == "__main__":
    	test(parameter)