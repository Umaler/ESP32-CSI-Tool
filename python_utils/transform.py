import math
import os

file_list = [
        't',
        'l',
        'e',
        'lt',
        'll',
        'le'
    ]
suffix_max = 6
postfix = '.csv'

mac_whitelist = "D0:EF:76:58:30:08"

def process(res):
    # Parser
    all_data = res.split(',')
    if all_data[2] != mac_whitelist:
        return

    csi_data = []
    amplitudes = []
    had_ampls = False
    phases = []
    had_phases = False
    for i in range(25, len(all_data)):
        data = all_data[i].split(" ")
        ident = data[0][0]
        del data[0]
        del data[-1]
        data = [int(c) for c in data if c]
        match ident:
            case "r":
                csi_data = data
            case "a":
                amplitudes = data
                had_ampls = True
            case "p":
                phases = data
                had_phases = True
            case _:
                print(f'Unknown id during processing line: {ident}')

    imaginary = []
    real = []

    for i, val in enumerate(csi_data):
        if i % 2 == 0:
            imaginary.append(val)
        else:
            real.append(val)

    if not amplitudes or not phases:
        csi_size = len(csi_data)
        if len(imaginary) > 0 and len(real) > 0:
            for j in range(int(csi_size / 2)):
                if not had_ampls:
                    amplitude_calc = math.sqrt(imaginary[j] ** 2 + real[j] ** 2)
                    amplitudes.append(amplitude_calc)
                if not had_phases:
                    phase_calc = math.atan2(imaginary[j], real[j])
                    phases.append(phase_calc)

    return imaginary, real, amplitudes, phases

def write_str_to_csv(out_f, arr):
    for i in arr:
        out_f.write(f'{i},')
    out_f.seek(out_f.tell() - 1, os.SEEK_SET)
    out_f.truncate()
    out_f.write('\r\n')

def transform_file(file_name):
    print(f'Procssing file {file_name}... ', end='', flush=True)
    with (
            open(file_name, 'r') as f,
            open(f'imag_{file_name}', 'w') as imag_f,
            open(f'real_{file_name}', 'w') as real_f,
            open(f'ampl_{file_name}', 'w') as ampl_f,
            open(f'phas_{file_name}', 'w') as phas_f,
         ):
        for line in f:
            ret_val = process(line)
            if ret_val:
                im, real, ampl, ph = ret_val
            else:
                continue
            write_str_to_csv(imag_f, im)
            write_str_to_csv(real_f, real)
            write_str_to_csv(ampl_f, ampl)
            write_str_to_csv(phas_f, ph)
    print('finished')

for name in file_list:
    for suffix in range(1, suffix_max + 1):
        transform_file(f'{name}{suffix}{postfix}')
transform_file('empty.csv')
transform_file('lempty.csv')
