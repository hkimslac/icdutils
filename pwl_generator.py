#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Author: Hyunjoon Kim (hkim@slac.stanford.edu)
#Date Created: Oct.17.2022
#
#PWL file generator for HSPICE digital VSOURCE, CLK and control
#

#Input total number of pulses
#Frequency per pulse
#Rise/Fall time (percentage w.r.t. frequency)
#Reset pulse (separate insertion)

#======================= Import some libraries here ==============
from optparse import OptionParser


#======================= Optionparser stuff here =================
parser = OptionParser()
parser.add_option("-n", "--name", help="name of the signal", default="sig.dat", dest="name")
#parser.add_option("-n", "--num_pulse", help="bitsream. ex) 01100 or 0100 etc", default="")
parser.add_option("-f", "--freq", help="ex) 5M or 2K or 1G", default="1M", dest="freq")
parser.add_option("-r", "--rst", help="reset cycle at the beginning of pwl (y/n)", default="y", dest="rst")
parser.add_option("-p", "--pctr", help="rise time. ex)0.01 for 1% or 0.1 for 10%", default="0.01", dest="pctr")
parser.add_option("-t", "--pctf", help="fall time. ex)0.01 for 1% or 0.1 for 10%", default="0.01", dest="pctf")
parser.add_option("-e", "--rr", help="is this pwl for a component that requires a reset? (y/n)", default="n", dest="rr")
parser.add_option("-g", "--rp", help="signal type. 0=repeat entire pwl with resets. 1: single reset then pwl repeat", default="0", dest="rp")
parser.add_option("-c", "--rn", help="is this repetitive pulse (r) or a custom control (c). If rr is set to 'no' then rp is a blank cycle with vl [off voltage]", default="r", dest="rn")
parser.add_option("-l", "--on", help="logic high", default="1.2", dest="on")
parser.add_option("-m", "--off", help="logic low", default="0", dest="off")
parser.add_option("-b", "--bar", help="True: complementary logic. False: normal logic", default="False", dest="bar")
parser.add_option("-a", "--repeat", help="repeat given bitsream for given number of times.", default="1", dest="rep")

(options, args) = parser.parse_args()

#======================= Define some function here ===============
def freq_convert(f):
    """
    convert user input frequency to time domain period
    """
    
    if f[-1] == "M" or "m":
        unit = 1000000.0
    elif f[-1] == "K" or "k":
        unit = 1000.0
    elif f[-1] == "G" or "g":
        unit = 1000000000.0
    else:
        unit = 1.0
    num = float(f[0:-1]) * unit
    
    timesig = 1.0/num    # timesig is in float
    
    return timesig


def time_convert(t):
    """
    convert time signature values to HSPICE compatible format
    """
    t_proc = []
    count = [0]
    #iterate x10 until you get rid of the exponent
    for i in range(20):
        t = str(t)
        if ("e" in t) or (float(t) < 1.0):
            
            t = float(t)*10
            count[0] += 1
        
        else: 
            break
            
    #print(count[0])
    t = float(t)
    
    if ((count[0] == 1) or (count[0] == 2) or (count[0] == 3) or (count[0] == 4) or (count[0] == 5)):
        unit = 6 - count[0]
        t = t*10**unit
        t_proc.append(str(t))
        t_proc.append("us")
    
    elif (count[0] == 6):
        t_proc.append(str(t))
        t_proc.append("us")
    
    elif ((count[0] == 7) or (count[0] == 8)):
        unit = 9 - count[0]
        t = t*10**unit
        t_proc.append(str(t))
        t_proc.append("ns")
    
    elif (count[0] == 9):
        t_proc.append(str(t))
        t_proc.append("ns")
        
    elif ((count[0] == 10) or (count[0] == 11)):
        unit = 12 - count[0]
        t = t*10**unit
        t_proc.append(str(t))
        t_proc.append("ps")
    
    elif (count[0] == 12):
        t_proc.append(str(t))
        t_proc.append("ps")
        
    else:
        print('cannot convert to HSPICE format')
    
    return t_proc


def match_unit(a,b):
    """
    make sure the rise/fall, reset and actual pulse period are all in the same unit
    """
    if (a[1]==b[1]):
        pass
    
    elif (a[1]=="ns") and (b[1]=="us"):
        a[0] = str(float(a[0])/1000.)
        a[1] = "us"
    
    elif (a[1]=="us") and (b[1]=="ns"):
        b[0] = str(float(b[0])/1000.)
        b[1] = "us"
        
    elif (a[1]=="ps") and (b[1]=="ns"):
        a[0] = str(float(a[0])/1000.)
        a[1] = "ns"
    
    elif (a[1]=="ns") and (b[1]=="ps"):
        b[0] = str(float(b[0])/1000.)
        b[1] = "ns"
        
    else:
        print("something broke while running match_unit function")
    
    return [a, b]
    
    
def concat_sig(ts,rt,t,ft,vh,vl):
    """
    concatenates piece-wise pulse to a single pulse with rise and fall time
    **todo: error handling
    
    rt/ft = rise/fall time (list['time value', 'unit'])
    t = pulse width period (string value 'xxxuu', x=numeric, u=timescale)
    vh = voltage value of the pulse
    vl = voltage value of the off-pulse
    """
    
    tmp = match_unit(rt,t)
    tmp_f = match_unit(ft,t)
    rt_n = ts[0][0]
    t_n = float(tmp[1][0])
    ft_n = float(tmp_f[0][0])
    tunitr = tmp[0][1]
    tunit  = tmp[1][1]
    tunitf = tmp_f[0][1]
    
    tstr   = round(rt_n + t_n + ft_n, 3)
    
    #Use this to generate pwl source to copy paste into tanner s-edit pwl vsource
    ##### need to fix here
    if (ft[0] == "0.0") and (rt[0] == "0.0"):
        outstr = str(tstr) + tunit + " " + str(vh) + "v" + " "
    elif (ft[0] == "0.0"):
        outstr = str(rt_n) + tunitr + " " + str(vh) + "v" + " " + str(rt_n+t_n) + tunit + " " + str(vh) + "v" + " "
    else:
        outstr = str(rt_n) + tunitr + " " + str(vh) + "v" + " " + str(rt_n+t_n) + tunit + " " + str(vh) + "v" + " " + str(tstr) + tunitf + " " + str(vl) + "v" + " "
    #Use this to generate pwl file for HSPICE
    #outstr = str(rt_n) +  " " + str(vh) + "v" + " " + str(rt_n+t_n) + " " + str(vh) + "v" + " " + str(tstr) + " " + str(vl) + "v" + " "
    
    return [outstr, tstr, tunit]
    
def wr_puls(pctr, pctf, ts, flag, outstr,t, on, off, unit_str):
    """
    Write pulse data to output string
    """
    if flag=='0':                                  # signal bit is 0
        ts[0][0] = ts[0][0]+float(pctr[0])         # increase time by rise time (from wherever pulse starts)
        ts[0][0] = round(ts[0][0],3)               # round the time to 3-sig figs
        puls=concat_sig(ts,pctr,t,pctf,off,off)    # concat rise+pulse+fall : added reset cycle
        ts[0][0] = puls[1]                         # update the timestamp
        ts[0][0] = round(ts[0][0],3)               # round the timestamp to 3-sig figs
        outstr.append(puls[0])                     # add pulse to output string
    elif flag=='1':                                # signal bit is 1
        ts[0][0] = ts[0][0]+float(pctr[0])         # increase time by rise time (from wherever pulse starts)
        ts[0][0] = round(ts[0][0],3)               # round the time to 3-sig figs
        puls=concat_sig(ts,pctr,t,pctf,on,off)     # concat rise+pulse+fall : added reset cycle
        ts[0][0] = puls[1]                         # update the timestamp
        ts[0][0] = round(ts[0][0],3)               # round the timestamp to 3-sig figs
        outstr.append(puls[0])                     # add pulse to output string
    else:
        print("wr_puls function failed because string flag is neither 1 or 0")
    
    unit_str.append(puls[2])
    
    return outstr

def gen_pwl(
            unit_str,         #passing the global unit string
            num_pulse,        #num_pulse = bitstream
            t,                #t = period (in seconds)
            rst,              #rst = reset cycle (reset is at the beginning of the pwl)
            pctr,             #pctr = rise time percentage w.r.t. to period
            pctf,             #pctf = fall time percentage w.r.t. to period
            rr,               #rr = is this pwl for a component that requires a reset? (y/n) default=n
            rp,               #rp = selectable options 
                              #     0, default: repeat entire pwl with repeating resets, 
                              #     1 : single reset & repeat only pulses
            rn,               #rn = is this repetitive pulse?(default 'r') or a custom control signal?('c')
                              #(Note: if rr is set to "no", then rp is a blank cycle with vl [off voltage])
            on,               #logic high
            off,              #logic low
            bar,              #True: complementary logic 
                              #False:normal logic (default)
            rep               #repeat bitstream  
            ):           
    """
    Generate PWL by concatenating all the option arguments given
    
    """
    outstr = []
    num_str = []
    
    
    on = str(on)
    off = str(off)
    
    if bar=='False':
        if rr=='y':
            if rp=='0':
                if rn=='r':
                    print("This is a repeating signal")
                    ts = [[0.0],['']]
                    for n in range(int(rep)):
                        for m,i in enumerate(num_pulse):
                            try:
                                if m==0:
                                    wr_puls(pctr, pctf, ts, '0', outstr, t, on, off, unit_str)
                                    if (num_pulse[m] == num_pulse[m+1]):#####
                                        wr_puls(pctr, fz, ts, i, outstr, t, on, off, unit_str)
                                    else:
                                        wr_puls(pctr, pctf, ts, i, outstr, t, on, off, unit_str)
                                else:
                                    if (num_pulse[m] == num_pulse[m+1]) and (num_pulse[m-1] == num_pulse[m]):#####
                                        wr_puls(rz, fz, ts, i, outstr, t, on, off, unit_str)
                                    elif (num_pulse[m] == num_pulse[m+1]) and (num_pulse[m-1] != num_pulse[m]):
                                        wr_puls(pctr, fz, ts, i, outstr, t, on, off, unit_str)
                                    else:
                                        wr_puls(pctr, pctf, ts, i, outstr, t, on, off, unit_str)
                            except IndexError:
                                pass

                else:
                    print("This is a custom signal does not repeat")
                    ts = [[0.0],['']]
                    for m,i in enumerate(num_pulse):
                        if m==0:
                            wr_puls(pctr, pctf, ts, '0', outstr, t, on, off, unit_str)
                            wr_puls(pctr, pctf, ts, i, outstr, t, on, off, unit_str)
                        else:
                            wr_puls(pctr, pctf, ts, i, outstr, t, on, off, unit_str)
            else:
                print("Wrong option entered for rp")
                
        else:
            print("Wrong option entered for rr")
            
    else:
        print("Wrong option entered for bar")
        
    
    return outstr



#======================= Function definition ends here =====================




#===========================================================================
#=======================  Script Starts Here  ==============================
#===========================================================================
if __name__ == "__main__":
    print("Starting PWL file generation\n")
    print("\n=============================\n")

    unit_str = []

    #sig_name = str(input("Enter the name of this signal (ex. bldrvclk or etc): "))
    sig_name = options.name
    num_pulse = str(input("Enter bitstream: "))
    #freq_per_pulse = str(input("Enter the frequency of each pulse (ex. 10M): "))
    freq_per_pulse = options.freq
    freq_per_pulse = freq_convert(freq_per_pulse)
    freq_per_pulse = time_convert(freq_per_pulse)
    #rise = str(input("Enter the percentage of rise time w.r.t freq. (0.1 or 0.01 = 10% or 1%): "))
    rise = options.pctr
    #fall = str(input("Enter the percentage of fall time w.r.t freq. (0.1 or 0.01 = 10% or 1%): "))
    fall = options.pctf
    rep = options.rep

    #rs_pulse = str(input("Insert reset pulse(y/n)? "))
    rs_pulse = options.rst

    if rs_pulse == "y":
        rs_pulse = "included"
    else:
        rs_pulse ="not included"

    pctr = [str(float(rise)*float(freq_per_pulse[0])),freq_per_pulse[1]]
    pctf = [str(float(fall)*float(freq_per_pulse[0])),freq_per_pulse[1]]
    rz   = ["0.0", freq_per_pulse[1]]
    fz   = ["0.0", freq_per_pulse[1]]

    print('You have entered: {num_pulse} pluses in {freq} period @ {rt}%, {ft}% of frequency for rise/fall time and reset cycle {yn}'.format(num_pulse=str(len(num_pulse)), freq=freq_per_pulse, rt=rise, ft=fall, yn=rs_pulse))

    print('Generating PWL.....')
    print("The signal name is: " + sig_name)
    out = gen_pwl(unit_str=unit_str, num_pulse=num_pulse, t=freq_per_pulse, rst=rs_pulse, pctr=pctr, pctf=pctf, rr=options.rr, rp=options.rp, rn=options.rn, on=options.on, off=options.off, bar=options.bar, rep=options.rep)

    print('PWL generation complete!')

    patt=''.join(out)
    print(patt)
    # ===========================================================================
    # =======================  Write to PWL file  ===============================
    # ===========================================================================
    wr_f = ''.join(out)
    wr_f = wr_f.split()
    

    path = "D:\\_ScriptTools\\HSPICE\\PWLIB\\"
    with open(path+sig_name+"_pwl.dat", 'w') as f:
        for i in range(0,len(wr_f),2):
            if unit_str[0] == "ns":
                f.write(wr_f[i][:-2] + 'e-9\t' + wr_f[i+1][:-1] + '\n')
            elif unit_str[0] == "us":
                f.write(wr_f[i][:-2] + 'e-6\t' + wr_f[i+1][:-1] + '\n')
            elif  unit_str[0] == "ps":
                f.write(wr_f[i][:-2] + 'e-12\t' + wr_f[i+1][:-1] + '\n')
            else:
                print("pulse information read failed")
