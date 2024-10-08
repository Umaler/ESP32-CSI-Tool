
line = input()

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
