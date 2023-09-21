module assertion
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
        input logic o_valid,
        input logic [g_data_width:0] o_C
    );

  assert_range : assert property(@(posedge i_clk) disable iff(i_rst) o_C < ((2**(g_data_width+1)) -1))
  	else $warning("Test Failure! ASSERTION FAILED!");
  assert_max : assert property(@(posedge i_clk) disable iff(i_rst) o_C == ((2**(g_data_width+1)) -2) |-> $past(i_A) == (2**g_data_width -1) && $past(i_B) == (2**g_data_width -1))
	else $warning("Test Failure! ASSERTION FAILED!");
  assert_valid : assert property (@(posedge i_clk) i_valid |=> o_valid)
  	else $warning("Test Failure! ASSERTION FAILED!"); 
  cover_C_max : cover property(@(posedge i_clk) disable iff(i_rst) o_C == ((2**(g_data_width+1)) -2));
endmodule
