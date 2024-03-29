# Simple test for a fizzbuzz module
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer,RisingEdge,ClockCycles
from cocotb.result import TestFailure
from adder_model import adder_model
import random
from cocotb_coverage import crv 
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db,CoverCheck

covered_XY = []
g_data_width = int(cocotb.top.g_data_width)

class crv_inputs(crv.Randomized):
	def __init__(self,x,y):
		crv.Randomized.__init__(self)
		self.x = x
		self.y = y 
		self.add_rand("x",list(range(2**g_data_width)))
		self.add_rand("y",list(range(2**g_data_width)))

full = False
def notify_full():
	global full 
	full = True

def assert_callback():
	raise TestFailure("Assertion failed!")


#at_least = value is superfluous, just shows how you can determine the amount of times that
#a bin must be hit to considered covered
@CoverPoint("top.a",xf = lambda dut : dut.i_A.value, bins = list(range(2**g_data_width)), at_least=1)
@CoverPoint("top.b",xf = lambda dut : dut.i_B.value, bins = list(range(2**g_data_width)), at_least=1)
@CoverPoint("top.c",xf = lambda dut : dut.o_C.value, bins = list(range(2**(g_data_width+1)-1)), at_least=1)
@CoverCross("top.cross", items = ["top.a","top.b"], at_least=1)
# CoverCheck can be used as a RTL language agnostic solution for embedding either
# immediate or concurrent assertions in simulation.
# most free simmulators dont support concurrent assertions (GHDL,icarus verilog)
# CoverCheck can be used to provide this functionality when using such simulators. 
@CoverCheck(
	"assertion.range",
	f_fail = lambda x : int(x.o_C.value) > 2**(g_data_width+1)-1,
	f_pass = lambda x : True
)
def io_cover(dut):
	covered_XY.append((dut.i_A.value,dut.i_B.value))



@CoverCheck(
	"assertion.valid_sig",
	f_fail = lambda x : x.o_valid.value == 0,
	f_pass = lambda x : True
)
def concurrent_assertions(dut):
	pass

# def number_cover(dut):
# 	covered_number.append(dut.o_number.value)

async def reset(dut,cycles=1):
	dut.i_rst.value = 1
	dut.i_A.value = 0
	dut.i_B.value = 0
	dut.i_valid.value = 0
	await ClockCycles(dut.i_clk,cycles)
	dut.i_rst.value = 0
	await RisingEdge(dut.i_clk)
	dut._log.info("the core was reset")

@cocotb.test()
async def adder_randomised_test(dut):
	"""Coverage driven test-generation. Full A-B cross-coverage, Full C coverage"""
	
	cycles_to_count_till_check_valid_sig = 1
	cnt_cycles_till_conseuent = 0
	inputs = crv_inputs(0,0)

	cocotb.start_soon(Clock(dut.i_clk, 10, units="ns").start())
	await reset(dut,5)	
	dut.i_valid.value = 1

	while(full != True):
		if(cnt_cycles_till_conseuent == cycles_to_count_till_check_valid_sig):
			concurrent_assertions(dut)
			cnt_cycles_till_conseuent = 0

		if(dut.i_valid.value == 1):
			cnt_cycles_till_conseuent += 1

		inputs.randomize()	#randomize object
		A = inputs.x
		B = inputs.y

		while (A,B) in covered_XY:
			inputs.randomize()	#randomize object
			A = inputs.x
			B = inputs.y

		dut.i_A.value = A
		dut.i_B.value = B
  
		await RisingEdge(dut.i_clk)
		await RisingEdge(dut.i_clk)
		io_cover(dut)
		coverage_db["top.cross"].add_threshold_callback(notify_full, 100)
		coverage_db["assertion.range"].add_bins_callback(assert_callback, "FAIL")
		coverage_db["assertion.valid_sig"].add_bins_callback(assert_callback, "FAIL")
		
		if dut.o_C.value != adder_model(A,B):
			raise TestFailure(
				"Randomised test failed with: %s + %s = %s" %
				(dut.i_A.value, dut.i_B.value, dut.o_C.value))
		else: 
			dut._log.info("Test PASS with {} + {} = {}".format(int(dut.i_A.value),int(dut.i_B.value),int(dut.o_C.value)))
	coverage_db.report_coverage(cocotb.log.info,bins=True)
	coverage_db.export_to_xml(filename="coverage.xml")
