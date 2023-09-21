`include "assertion.sv"
module top
	#(
        //use /*verilator public*/ on parameter -> parameter values visible to verilated code
        parameter int g_data_width /*verilator public*/ = 8
    )
    (
        input logic i_clk,
        input logic i_rst,
        input logic i_valid,
        input logic [g_data_width-1:0] i_A,
        input logic [g_data_width-1:0] i_B,
        output logic o_valid,
        output logic [g_data_width:0] o_C
    );

    adder #(.g_data_width(g_data_width)) DUT 
    (
    	.i_clk,
    	.i_rst,
    	.i_valid,
    	.i_A,
    	.i_B,
    	.o_valid,
    	.o_C
	);

    // Note: Verilator only ssupports bind to a target module name, NOT to an instance path.
	bind adder assertion #(.g_data_width(g_data_width)) inst
    (
    	.i_clk,
    	.i_rst,
    	.i_valid,
    	.i_A,
    	.i_B,
    	.o_valid,
    	.o_C
	);
endmodule
