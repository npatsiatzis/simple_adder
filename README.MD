![example workflow](https://github.com/npatsiatzis/simple_adder/actions/workflows/regression.yml/badge.svg)
![example workflow](https://github.com/npatsiatzis/simple_adder/actions/workflows/coverage.yml/badge.svg)
![example workflow](https://github.com/npatsiatzis/simple_adder/actions/workflows/regression_pyuvm.yml/badge.svg)
![example workflow](https://github.com/npatsiatzis/simple_adder/actions/workflows/coverage_pyuvm.yml/badge.svg)

### simple two input adder RTL implementation


-- CoCoTB testbench for functional verification
    - $ make
- Coverage-driven test generation
- Achieve full point coverage for inputs, outputs and cross coverage
- CoCoTB-test unit testing to exercise the CoCoTB tests across a range of values for the generic parameters
    - $  SIM=ghdl pytest -n auto -o log_cli=True --junitxml=test-results.xml --cocotbxml=test-cocotb.xml

