library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity adder is
	generic (
			g_data_width : natural :=4);
	port(
		i_A : in std_ulogic_vector(g_data_width-1 downto 0);
		i_B : in std_ulogic_vector(g_data_width-1 downto 0);
		o_C : out std_ulogic_vector(g_data_width downto 0)); 
end adder;

architecture arch of adder is 
begin
	o_C <= std_ulogic_vector(resize(unsigned(i_A),o_C'length) + unsigned(i_B));
end arch;