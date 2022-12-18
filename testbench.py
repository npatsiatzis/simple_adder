# Simple tests for an adder module
import cocotb
from cocotb.triggers import Timer
from cocotb.result import TestFailure
from adder_model import adder_model
import random
from cocotb_coverage import crv 
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db


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

#at_least = value is superfluous, just shows how you can determine the amount of times that
#a bin must be hit to considered covered
@CoverPoint("top.a",xf = lambda dut : dut.i_A.value, bins = list(range(2**g_data_width)), at_least=1)
@CoverPoint("top.b",xf = lambda dut : dut.i_B.value, bins = list(range(2**g_data_width)), at_least=1)
@CoverPoint("top.c",xf = lambda dut : dut.o_C.value, bins = list(range(2**(g_data_width+1)-1)), at_least=1)
@CoverCross("top.cross", items = ["top.a","top.b"], at_least=1)
def io_cover(dut):
	covered_XY.append((dut.i_A.value,dut.i_B.value))


@cocotb.test()
def adder_randomised_test(dut):
	"""Coverage driven test-generation. Full A-B cross-coverage, Full C coverage"""
	
	inputs = crv_inputs(0,0)

	while(full != True):
		inputs.randomize()	#randomize object
		A = inputs.x
		B = inputs.y

		while (A,B) in covered_XY:
			inputs.randomize()	#randomize object
			A = inputs.x
			B = inputs.y

		dut.i_A.value = A
		dut.i_B.value = B
  
		
		yield Timer(2)
		io_cover(dut)
		coverage_db["top.cross"].add_threshold_callback(notify_full, 100)
		if dut.o_C.value != adder_model(A,B):
			raise TestFailure(
				"Randomised test failed with: %s + %s = %s" %
				(dut.i_A.value, dut.i_B.value, dut.o_C.value))
		else: 
			dut._log.debug("Ok!")
	coverage_db.report_coverage(cocotb.log.info,bins=True)
	coverage_db.export_to_xml(filename="coverage.xml")