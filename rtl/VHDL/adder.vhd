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

entity ADDER is
	generic (
		G_DATA_WIDTH : natural := 4	--! addition operands(max) data width.
	);
	port (
		I_A : in    std_ulogic_vector(G_DATA_WIDTH - 1 downto 0);	--! operandA.
		I_B : in    std_ulogic_vector(G_DATA_WIDTH - 1 downto 0);	--! operandB.
		O_C : out   std_ulogic_vector(G_DATA_WIDTH downto 0)	 	  --! result.
	);
end entity ADDER;

architecture ARCH of ADDER is

begin

	O_C <= std_ulogic_vector(resize(unsigned(I_A), O_C'length) + unsigned(I_B));

end architecture ARCH;