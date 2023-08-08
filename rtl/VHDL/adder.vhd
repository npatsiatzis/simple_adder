--! \file adder.vhd
--! \brief this is the sole RTL file of an introduction in the basic of CoCoTB and pyuvm

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

--! \brief trivial binary adder with bit growth
--!
--! **Instantiation template**
--!
--! ```vhdl
--! adder_0 : entity work.adder(arch)
--!  generic map (
--!    g_data_width => g_data_width
--!  )
--!  port map (
--!    i_A  => w_A,
--!    i_B  => w_B,
--!    o_C  => w_C
--!  );
--! ```
entity adder is
	generic (
		g_data_width : natural :=4	--! addition operands(max) data width.
	);
	port(
		i_A : in std_ulogic_vector(g_data_width-1 downto 0);	--! operandA.
		i_B : in std_ulogic_vector(g_data_width-1 downto 0);	--! operandB.
		o_C : out std_ulogic_vector(g_data_width downto 0)	 	--! result.
	);
end adder;

architecture arch of adder is 
begin
	o_C <= std_ulogic_vector(resize(unsigned(i_A),o_C'length) + unsigned(i_B));
end arch;