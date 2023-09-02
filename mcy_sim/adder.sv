`default_nettype none

module adder
    #(
        //use /*verilator public*/ on parameter -> parameter values visible to verilated code
        parameter int G_DATA_WIDTH /*verilator public*/ = 8
    )

    (
        input logic i_clk,
        input logic i_rst,
        input logic i_valid,
        input logic [G_DATA_WIDTH-1:0] i_A,
        input logic [G_DATA_WIDTH-1:0] i_B,
        output logic o_valid,
        output logic [G_DATA_WIDTH:0] o_C
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


endmodule : adder
