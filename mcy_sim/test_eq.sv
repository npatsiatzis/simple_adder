
module miter 
    #
    (
	    parameter int G_DATA_WIDTH = 8
    )

    (

	    input logic i_clk,
	    input logic i_rst,
	    input logic ref_i_valid,
	    input logic uut_i_valid,
	    input logic [G_DATA_WIDTH-1:0] ref_i_A,
	    input logic [G_DATA_WIDTH-1:0] ref_i_B,
	    input logic [G_DATA_WIDTH-1:0] uut_i_A,
	    input logic [G_DATA_WIDTH-1:0] uut_i_B

		// input [63:0] ref_din_data,
		// input [63:0] uut_din_data,
		// input [ 2:0] din_func
	);

    wire ref_o_valid;
    wire uut_o_valid;
	wire [G_DATA_WIDTH -1 : 0] ref_o_C;
	wire [G_DATA_WIDTH -1 : 0] uut_o_C;
	reg f_past_valid;

	// wire [63:0] ref_dout_data;
	// wire [63:0] uut_dout_data;

	adder  ref
	(
		.mutsel(1'b0),
		.i_clk  (i_clk),
		.i_rst  (i_rst),
		.i_valid(ref_i_valid),
		.i_A(ref_i_A),
		.i_B(ref_i_B),
		.o_valid(ref_o_valid),
		.o_C(ref_o_C)
	);

	adder  uut
	(
		.mutsel(1'b1),
		.i_clk  (i_clk),
		.i_rst  (i_rst),
		.i_valid(uut_i_valid),
		.i_A(uut_i_A),
		.i_B(uut_i_B),
		.o_valid(uut_o_valid),
		.o_C(uut_o_C)
	);


	// bitcnt ref (
	// 	.mutsel    (1'b 0),
	// 	.din_data  (ref_din_data),
	// 	.din_func  (din_func),
	// 	.dout_data (ref_dout_data)
	// );

	// bitcnt uut (
	// 	.mutsel    (1'b 1),
	// 	.din_data  (uut_din_data),
	// 	.din_func  (din_func),
	// 	.dout_data (uut_dout_data)
	// );


	always @* begin
		assume_valid : assume (ref_i_valid == uut_i_valid);
		assume_A : assume (ref_i_A == uut_i_A);
		assume_B : assume (ref_i_B == uut_i_B);
		// assume (i_rst == 1'b1);
	end

	initial begin
		f_past_valid <= 1'b0;
		// assume_rst: assume(i_rst == 1'b1);
		// assume_ref_C : assume(ref_o_C == 0);
		// assume_uut_C : assume (uut_o_C == 0);
	end
	
	always @(posedge i_clk) begin
		f_past_valid <= 1'b1;
	 	if(!i_rst) begin
			// assert_valid : assert (ref_o_valid == uut_o_valid);
			if(f_past_valid && $past(ref_i_valid) && $past(uut_i_valid))
				assert_C : assert (ref_o_C == uut_o_C);
	 	end
	end

	// always @* begin
	// 	casez (din_func)
	// 		3'b11z: begin
	// 			// unused opcode: don't check anything
	// 		end
	// 		3'bzz1: begin
	// 			// 32-bit opcodes, only constrain lower 32 input bits and check all 64 output bits
	// 			assume (ref_din_data[31:0] == uut_din_data[31:0]);
	// 			assert (ref_dout_data == uut_dout_data);
	// 		end
	// 		3'bzz0: begin
	// 			// 64-bit opcodes, constrain all 64 input bits and check all 64 output bits
	// 			assume (ref_din_data == uut_din_data);
	// 			assert (ref_dout_data == uut_dout_data);
	// 		end
	// 	endcase
	// end
endmodule
