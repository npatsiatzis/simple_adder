## Requirements Specification


### 1. SCOPE

1. **Scope**

   This document establishes the requirements for an Intellectual Property (IP) that provides an adder function.
1. **Purpose**
 
   These requirements shall apply to an adder core with a simple interface for inclusion as a component.
1. **Classification**
    
   This document defines the requirements for a hardware design.


### 2. DEFINITIONS

1. **Width**

   The width in bits of adder inputs. The width of the result (output), following the bit growth, is greater by 1 bit.
   

### 3. APPLICABLE DOCUMENTS 

1. **Government Documents**

   None
1. **Non-government Documents**

   None


### 4. ARCHITECTURAL OVERVIEW

1. **Introduction**

   The adder component shall represent a design written in an HDL (VHDL and/or SystemVerilog) that can easily be        incorporateed into a larger design. The adder shall include the following features : 
     1. Parameterized operands width.
     1. Sequential addition.

   The CPU interface in this case will be a trivial case of the ready/valid interface, namely the valid interface. The CPU/controller shall use a valid signal to signify the validity of the data on the adder inputs and shall reeceive the addition result on the next clock cycle.

1. **System Application**
   
    The adder can be applied to a variety of system configurations. An example of such a configuration is an upstream module producing data and a downstream one consuming the addition results.

### 5. PHYSICAL LAYER
	1. i_A, operand A
	2. i_B, operand B
    2. i_valid, input data avalid
    3. o_valid, output data valid
    4. o_C, addition result
    7. clk, system clock
    8. rst, system reset, synchronous active high

### 6. PROTOCOL LAYER
The core shall perform addition on valid operands (inputs) only.

### 7. ROBUSTNESS

Does not apply.
### 8. HARDWARE AND SOFTWARE

1. **Parameterization**

   The UART shall provide for the following parameters used for the definition of the implemented hardware during hardware build:

   | Param. Name | Description |
   | :------: | :------: |
   | data width | width of the addition operands |

1. **CPU interface**

   The CPU shall indicatate with i_valid when the addition operation shall be performed,

### 9. PERFORMANCE

1. **Frequency**
1. **Power Dissipation**
1. **Environmental**
 
   Does not apply.
1. **Technology**

   The design shall be adaptable to any technology because the design shall be portable and defined in an HDL.

### 10. TESTABILITY
None required.

### 11. MECHANICAL
Does not apply.
