### simple two input adder SystemVerilog implementation


-- Verilator tb for functional verification, adapted from the work of Norbet Kremeris (https://www.itsembedded.com/dhd/verilator_4/). Added coverage class for the input and output interfaces, coverage-based end-of-test condition and coverage-driven test generation
    - $ make sim
- Achieve full point coverage for output
- open waveform with gtkwave
    - $ make waves
- lint test
    - $make lint
