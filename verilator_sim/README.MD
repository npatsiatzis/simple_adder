![example workflow](https://github.com/npatsiatzis/simple_adder/actions/workflows/verilator_regression.yml/badge.svg)
[![codecov](https://codecov.io/gh/npatsiatzis/simple_adder/graph/badge.svg?token=ODC4X3AYR3)](https://codecov.io/gh/npatsiatzis/simple_adder)

### simple two input adder SystemVerilog implementation


-- Verilator tb for functional verification, adapted from the work of Norbet Kremeris (https://www.itsembedded.com/dhd/verilator_4/). Added coverage class for the input and output interfaces,sequence class, coverage-based end-of-test condition and coverage-driven test generation
    - $ make sim
- Achieve full point coverage for output
- open waveform with gtkwave
    - $ make waves
- lint test
    - $make lint
