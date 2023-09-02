
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

	);

    wire ref_o_valid;
    wire uut_o_valid;
	wire [G_DATA_WIDTH -1 : 0] ref_o_C;
	wire [G_DATA_WIDTH -1 : 0] uut_o_C;
	reg f_past_valid;

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


	always @* begin
		assume_valid : assume (ref_i_valid == uut_i_valid);
		assume_A : assume (ref_i_A == uut_i_A);
		assume_B : assume (ref_i_B == uut_i_B);
	end

	initial begin
		f_past_valid <= 1'b0;
	end
	
	always @(posedge i_clk) begin
		f_past_valid <= 1'b1;
	 	if(!i_rst) begin
			if(f_past_valid && $past(ref_i_valid) && $past(uut_i_valid))
				assert_C : assert (ref_o_C == uut_o_C);
	 	end
	end
endmodule
