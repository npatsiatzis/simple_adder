`default_nettype none

module adder 
	#(parameter
		g_data_width = 12
	)

	(
		input logic [g_data_width-1:0] i_A,
		input logic [g_data_width-1:0] i_B,
		output logic [g_data_width:0]  o_C
	);

	always_comb begin
		assert (o_C <= 2**(g_data_width+1)-2);
	end

	always_comb begin
		cover(o_C == 0);
		cover(o_C == 2**(g_data_width+1)-2);
	end

	assign o_C = i_A + i_B;

endmodule : adder