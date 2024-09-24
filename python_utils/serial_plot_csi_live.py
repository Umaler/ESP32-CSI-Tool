import sys
import signal
import matplotlib.pyplot as plt
import matplotlib
import math
import time
import numpy as np
import collections
from wait_timer import WaitTimer

from socket import *

signal.signal(signal.SIGINT, signal. SIG_DFL)

mac_whitelist = "D0:EF:76:58:30:08"

# Set subcarrier to plot
subcarrier = 44

# Wait Timers. Change these values to increase or decrease the rate of `print_stats` and `render_plot`.
print_stats_wait_timer = WaitTimer(1.0)
render_plot_wait_timer = WaitTimer(0.2)

# Deque definition
perm_amp = collections.deque(maxlen=100)
perm_phase = collections.deque(maxlen=100)

# Variables to store CSI statistics
packet_count = 0
total_packet_counts = 0

# Create figure for plotting
plt.ion()
fig = plt.figure()
plt.pause(0.1)
ax = fig.add_subplot(111)
fig.canvas.draw()

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
serverSocket.bind(('', 5000))


def carrier_plot(amp):
    plt.clf()
    df = np.asarray(amp, dtype=np.int32)
    # Can be changed to df[x] to plot sub-carrier x only (set color='r' also)
    plt.plot(range(100 - len(amp), 100), df[:, subcarrier], color='r')
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.xlim(0, 100)
    plt.title(f"Amplitude plot of Subcarrier {subcarrier}")
    # TODO use blit instead of flush_events for more fastness
    # to flush the GUI events
    plt.draw()
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.1)


def process(res):
    # Parser
    all_data = res.split(',')
    if all_data[2] != mac_whitelist:
        return

    csi_data = []
    amplitudes = []
    phases = []
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
            case "p":
                phases = data
            case _:
                print(f'Unknown id during processing line: {ident}')

    imaginary = []
    real = []

    if (not amplitudes or not phases) and csi_data:
        for i, val in enumerate(csi_data):
            if i % 2 == 0:
                imaginary.append(val)
            else:
                real.append(val)

    if not amplitudes and not phases:
        csi_size = len(csi_data)
        if len(imaginary) > 0 and len(real) > 0:
            for j in range(int(csi_size / 2)):
                if not amplitudes:
                    amplitude_calc = math.sqrt(imaginary[j] ** 2 + real[j] ** 2)
                    amplitudes.append(amplitude_calc)
                if not phases:
                    phase_calc = math.atan2(imaginary[j], real[j])
                    phases.append(phase_calc)

    if phases:
        perm_phase.append(phases)
    if amplitudes:
        perm_amp.append(amplitudes)

while True:
    message, _ = serverSocket.recvfrom(1024)

    line = message.decode()

    if "CSI_DATA" in line:
        process(line)
        packet_count += 1
        total_packet_counts += 1

        if print_stats_wait_timer.check():
            print_stats_wait_timer.update()
            print("Packet Count:", packet_count, "per second.", "Total Count:", total_packet_counts)
            packet_count = 0

        if render_plot_wait_timer.check() and len(perm_amp) > 2:
            render_plot_wait_timer.update()
            carrier_plot(perm_amp)
