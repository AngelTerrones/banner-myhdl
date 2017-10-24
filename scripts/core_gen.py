#!/usr/bin/env python3
# Copyright (c) 2017 Angel Terrones <aterrones@usb.ve>

from rtl.banner import banner
from rtl.utils import createSignal


xst_verilog = """
FLOWTYPE = FPGA_SYNTHESIS;
#########################################################
## Filename: xst_verilog.opt
##
## Verilog Option File for XST targeted for speed
## This works for FPGA devices.
#########################################################

#-------------------------------------------------------------------------------
# Options for XST
#-------------------------------------------------------------------------------
Program xst
-ifn <design>_xst.scr;            # input XST script file
-ofn <design>_xst.log;            # output XST log file
-intstyle xflow;                  # Message Reporting Style: ise, xflow, or silent

#-------------------------------------------------------------------------------
# The options listed under ParamFile are the XST Properties that can be set by the
# user. To turn on an option, uncomment by removing the '#' in front of the switch.
#-------------------------------------------------------------------------------
ParamFile: <design>_xst.scr
"run";

#-------------------------------------------------------------------------------
# Global Synthesis Options
#-------------------------------------------------------------------------------
"-ifn <synthdesign>";             # Input/Project File Name
"-ifmt Verilog";                  # Input Format
"-ofn <design>";                  # Output File Name
"-ofmt ngc";                      # Output File Format
"-p <partname>";                  # Target Device
"-opt_level 2";                   # Optimization Effort Criteria
                                  # 1 (Normal) or 2 (High)

"-top       {0}";

"-opt_mode SPEED";                # Optimization Criteria
                                  # AREA or SPEED
End ParamFile
End Program xst

#-------------------------------------------------------------------------------
# See XST USER Guide Chapter 8 (Command Line Mode) for all XST options
#-------------------------------------------------------------------------------
"""

prom_file = """
#-----------------------------------------------------------------------------#
# Sets the operating mode for PROM file generation.                           #
#-----------------------------------------------------------------------------#
setMode -pff

#-----------------------------------------------------------------------------#
# Switches to the Slave SPI sub-mode of PROM File Generation mode.            #
#-----------------------------------------------------------------------------#
setSubmode -pffserial

#-----------------------------------------------------------------------------#
# Adds a single 128MB PROM to position 1.                                     #
#-----------------------------------------------------------------------------#
addPromDevice -p 1 -size 0 -name xcf02s

#-----------------------------------------------------------------------------#
# Adds a single design set.                                                   #
# The version and name need to be set to zero for a PROM file generation      #
# sequence, and only needs to be set once.                                    #
#-----------------------------------------------------------------------------#
addDesign -version 0 -name 0

#-----------------------------------------------------------------------------#
# Adds a single chain to the design set.                                      #
# The index needs to be set to zero for PROM file generation sequence, and    #
# only needs to be set once.                                                  #
#-----------------------------------------------------------------------------#
addDeviceChain -index 0

#-----------------------------------------------------------------------------#
# Adds a device to the first position in the target chain and assigns         #
# the *.bit configuration file to the device.                                 #
#-----------------------------------------------------------------------------#
addDevice -p 1 -file "./{0}.bit"

#-----------------------------------------------------------------------------#
# Generate *.mcs                                                              #
# The PROM checksum is calculated based on the devices expected fill value.   #
# The default fill value for checksum calculations is FF, which corresponds   #
# to the erased state of the PROM.                                            #
#-----------------------------------------------------------------------------#
generate -format mcs -fillvalue FF -output {0}

#-----------------------------------------------------------------------------#
# Exits iMPACT                                                                #
#-----------------------------------------------------------------------------#
quit
"""

program_file = """
#-----------------------------------------------------------------------------#
# Sets the operating mode for Boundary-Scan (JTAG).                           #
#-----------------------------------------------------------------------------#
setMode -bscan

#-----------------------------------------------------------------------------#
# Tells iMPACT to automatically detect the cable. A Xilinx programming cable  #
# must be connected to your computer.                                         #
#-----------------------------------------------------------------------------#
setCable -port auto

#-----------------------------------------------------------------------------#
# Identifies the devices in the Boundary-Scan chain and adds each device to   #
# the list of devices to be configured. Applicable in Boundary-Scan           #
# configuration mode.                                                         #
#-----------------------------------------------------------------------------#
Identify
identifyMPM

#-----------------------------------------------------------------------------#
# Assigns a new configuration file to an existing device.                     #
#  -p    <pos>      - Specifies the position of the device in the chain.      #
#  -file <fileName> - Specifies the name of the configuration file.           #
#-----------------------------------------------------------------------------#
assignFile -p 1 -file "./{0}.bit"

#-----------------------------------------------------------------------------#
# Indirect programming command which assigns a new configuration file to an   #
# existing BPI or SPI Flash device attached to an FPGA. The Flash device will #
# be programmed through the FPGA. Applicable in Boundary Scan mode.           #
# -p    <pos>      - Specifies the position of the FPGA device in the chain.  #
# -file <fileName> - Specifies the name of the configuration file.            #
#-----------------------------------------------------------------------------#
assignFile -p 2 -file "./{0}.mcs"

#-----------------------------------------------------------------------------#
# Programs a device with options to erase first, then verify after            #
# programming. Applicable to all configuration modes.                         #
# -p  <pos> - Refers to the position of the device(s) in the chain.           #
# -e        - Erases the device before programming.                           #
# -v        - Verifies the device has been programmed.                        #
# -w        - Write protects the device.                                      #
# -loadfpga - Sends JTAG instruction to the PROM which causes it to           #
#             automatically load the FPGA after PROM programming is complete. #
#-----------------------------------------------------------------------------#
Program -p 1
Program -p 2 -e -v -loadfpga

#-----------------------------------------------------------------------------#
# Exits iMPACT                                                                #
#-----------------------------------------------------------------------------#
quit
"""


def convert_to_verilog(args):
    clk       = createSignal(0, 1)
    rst       = createSignal(0, 1)
    anodos    = createSignal(0, 4)
    segmentos = createSignal(0, 8)
    shift     = createSignal(0, 1)
    clk_xtal  = args.clock * 1000000
    dut       = banner(clk_i=clk,
                       rst_i=rst,
                       anodos_o=anodos,
                       segmentos_o=segmentos,
                       shift_o=shift,
                       CLK_XTAL=clk_xtal,
                       RST_NEG=args.rst_neg)
    dut.convert(path=args.path, name=args.filename, trace=False, testbench=False)


def setup_project(args):
    # generate opt file
    with open('{0}/xst_verilog.opt'.format(args.build_folder), 'w') as f:
        f.write(xst_verilog.format(args.top_module))
    # generate PROM batch file
    with open('{0}/prom_file.batch'.format(args.build_folder), 'w') as f:
        f.write(prom_file.format(args.top_module))
    # create PROGRAM batch file
    with open('{0}/program_file.batch'.format(args.build_folder), 'w') as f:
        f.write(program_file.format(args.top_module))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Core generation. Main script')
    subparsers = parser.add_subparsers(title='Sub-commands',
                                       description='Available functions',
                                       help='Description')
    # convert to Verilog
    parser2verilog = subparsers.add_parser('to_verilog', help='Convert design to verilog')
    parser2verilog.add_argument('--path', help='Path to store the verilog output file', type=str, required=True)
    parser2verilog.add_argument('--filename', help='Name for the verilog output file', type=str, required=True)
    parser2verilog.add_argument('--clock', help='Clock in MHz', type=int, required=True)
    parser2verilog.add_argument('--rst_neg', help='Reset polarity', action='store_true')
    parser2verilog.set_defaults(func=convert_to_verilog)

    # setup
    setup = subparsers.add_parser('setup', help='Generate project files for synthesis')
    setup.add_argument('--build_folder', help='Output folder', type=str, required=True)
    setup.add_argument('--top_module', help='', type=str, required=True)
    setup.set_defaults(func=setup_project)

    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()

# Local Variables:
# flycheck-flake8-maximum-line-length: 300
# flycheck-flake8rc: ".flake8rc"
# End:
