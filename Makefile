#-------------------------------------------------------------------------------
# Makefile for EC1723-Lab 3.
# Author: Angel Terrones <aterrones@usb.ve>
#-------------------------------------------------------------------------------
.FOUT=out
.PYTHON=python3
.PYTEST=pytest

.PWD=$(shell pwd)
.RTL_FOLDER=$(shell cd rtl; pwd)
.PYTHON_FILES=$(shell find $(.RTL_FOLDER) -name "*.py")
.SCRIPT_FOLDER=$(shell cd scripts; pwd)

#-------------------------------------------------------------------------------
# FPGA
#-------------------------------------------------------------------------------
# Boards:
# Xula2 (using SPARTAN-6)
# S3 (Using SPARTAN-3)
#-------------------------------------------------------------------------------
.BRD=xula2
.TOPE_V=banner

ifeq ($(.BRD), xula2)
	.FPGA=xc6slx25-2-ftg256  # SPARTAN-6
	.CLK=12
	.RST_NEG=--rst_neg
else ifeq ($(.BRD), s3)
	.FPGA=xc3s200-ft256-4  # SPARTAN-3
	.CLK=50
else
$(error Invalid FPGA board)
endif

#-------------------------------------------------------------------------------
# XILINX ISE
#-------------------------------------------------------------------------------
ifeq ($(shell uname), Linux)
		.ISE_BIN=/opt/Xilinx/14.7/ISE_DS/ISE/bin/lin64
else
		.ISE_BIN=/cygdrive/c/Xilinx/14.7/ISE_DS/ISE/bin/nt
endif
export PATH:=$(.ISE_BIN):$(PATH)

# ********************************************************************
.PHONY: default clean distclean

# ********************************************************************
# Syntax check
# ********************************************************************
check-verilog: to-verilog
	@verilator --lint-only $(.FOUT)/$(.TOPE_V).v && echo "CHECK: OK"

# ********************************************************************
# Test
# ********************************************************************
test-myhdl:
	@rm -f *.vcd*
	@PYTHONPATH=$(PWD) $(.PYTEST) --tb=short -s test/test_$(.TOPE_V).py

test-cosim:
	@mkdir -p $(.FOUT)
	@PYTHONPATH=$(PWD) $(.PYTEST) --tb=short test/test_$(.TOPE_V)_cosim.py

# ********************************************************************
# Implementation
# ********************************************************************
to-verilog: $(.FOUT)/$(.TOPE_V).v

build-bitstream: $(.FOUT)/$(.TOPE_V).v $(.FOUT)/$(.TOPE_V).bit

build-prom: $(.FOUT)/$(.TOPE_V).mcs

program-fpga: build-prom
	@cd $(.FOUT) && impact -batch program_file.batch

# ---
%.v: $(.PYTHON_FILES)
	@mkdir -p $(.FOUT)
	@PYTHONPATH=$(PWD) $(.PYTHON) $(.SCRIPT_FOLDER)/core_gen.py to_verilog --path $(.FOUT) --filename $(.TOPE_V) --clock $(.CLK) $(.RST_NEG)

%.bit: ucf/pines_$(.BRD).ucf
	@mkdir -p $(.FOUT)
	@cp -f ucf/pines_$(.BRD).ucf $(.FOUT)/$(.TOPE_V).ucf
	@PYTHONPATH=$(PWD) $(.PYTHON) $(.SCRIPT_FOLDER)/core_gen.py setup --build_folder $(.FOUT) --top_module $(.TOPE_V)
	@cd $(.FOUT) && \
	xflow -p $(.FPGA) -implement high_effort.opt -config bitgen.opt -synth xst_verilog.opt $(.TOPE_V).v

%.mcs: $(.FOUT)/$(.TOPE_V).bit
	@cd $(.FOUT) && impact -batch prom_file.batch

# ********************************************************************
# Clean
# ********************************************************************
clean:
	@rm -rf $(.FOUT)/
	@find . | grep -E "(\.vcd)" | xargs rm -rf

distclean: clean
	@find . | grep -E "(__pycache__|\.pyc|\.pyo|\.vcd|\.cache)" | xargs rm -rf
