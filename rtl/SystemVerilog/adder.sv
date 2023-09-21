`default_nettype none

module adder
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

    always_ff @(posedge i_clk or posedge i_rst) begin : proc_add
        if(i_rst) begin
            o_C <= '0;
            o_valid <= 1'b0;
        end else begin
            o_valid <= 1'b0;
            if(i_valid) begin
                o_C <= i_A+i_B;
                o_valid <= 1'b1;
            end
        end
    end

`ifdef WAVEFORM
	  initial begin
	    // Dump waves
	    $dumpfile("dump.vcd");
	    $dumpvars(0, adder);
	  end
`endif
  
// `ifdef USE_VERILATOR  
//   assert_range : assert property(@(posedge i_clk) o_C < ((2**(g_data_width+1)) -1))
//   	else $warning("Test Failure! ASSERTION FAILED!");
//   assert_max : assert property(@(posedge i_clk) o_C == ((2**(g_data_width+1)) -2) |-> $past(i_A) == (2**g_data_width -1) && $past(i_B) == (2**g_data_width -1))
// 	else $warning("Test Failure! ASSERTION FAILED!");
//   assert_valid : assert property (@(posedge i_clk) i_valid |=> o_valid)
//   	else $warning("Test Failure! ASSERTION FAILED!"); 
//   cover_C_max : cover property(@(posedge i_clk) o_C == ((2**(g_data_width+1)) -2));
// `endif

endmodule : adder
