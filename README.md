# icdutils
------------
## Notes
------------
- This repository is a collection of python scripts to help running *HSPICE*, *ELDO* and *Spectre* simulations 
- *VCS*, *Verilator* and other HDL testbench simulation util scripts will be in a separate repository
------------
### pwl_generator.py
------------
- This script is to generate bitstream (*PWL*) used as input/control signals in circuit simulators.

#### Usage
- '-n' Name of the pwl file. Default=*sig.dat*
- '-f' Frequency of the signal. Default=*1M*
- '-r' Inserting a reset cycle at the beginning of PWL (y/n). Default=*y*
- '-p' Rise time with respect to the period in percentage. Default=*0.01*
- '-t' Fall time with respect to the period in percentage. Default=*0.01*
- '-e' This PWL will be used for a component that requires a reset (y/n). Default=*n*
- '-g' Signal type. *0*=repeat entire pwl with repetitive resets. *1*=single reset and repetitive pwl. Default=*0*
- '-c' PWL is repetitive (r) or custom form (c). Default=*r*
- '-l' Logic high voltage. Default=*1.2*
- '-m' Logic low voltage. Default=*0*
- '-b' True: Complementary (barred) logic. False: Normal logic. Default=*False*

#### Example
'python pwl_generator.py -nTest.dat -f5M -ry -p0.01 -t0.01 -ey -g0 -cr -l1.2 -m0 -bFalse'

This will generate the following PWL stream
'2.0ns 0v 202.0ns 0v 204.0ns 0v 206.0ns 1.2v 406.0ns 1.2v 408.0ns 0v 410.0ns 0v 610.0ns 0v 612.0ns 0v 614.0ns 0v 814.0ns 0v 816.0ns 0v 818.0ns 0v 1018.0ns 0v 1020.0ns 0v'

------------
## Contact
Hyunjoon Kim (hkim@slac.stanford.edu)
