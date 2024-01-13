import matplotlib.pyplot as plt
import numpy as np
import guwlib

# define the signal
my_signal = guwlib.Burst(n_cycles=4, center_frequency=1, delta_t=2, window='hanning')


# time domain ----------------------------------------------------------------------------------------------------------
t = np.linspace(0, 100, 10000)
s = np.array([my_signal.get_value_at(i_t) for i_t in t])


# frequency domain -----------------------------------------------------------------------------------------------------
fft = np.fft.fft(s)

# compute the frequencies corresponding to the FFT values
dt = t[1] - t[0]  # sample rate
n_samples = s.size
f = np.linspace(0, 1 / dt, n_samples)

# Consider only the first half of the frequencies (single-sided spectrum)
fft = fft[0:n_samples // 2]
f = f[0:n_samples // 2]

# Compute the amplitude spectrum
amp_spectrum = 2.0 / n_samples * np.abs(fft)

# Create a figure and a set of subplots --------------------------------------------------------------------------------
fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))

ax1 = axs[0]
ax1.plot(t, s)
ax1.set_title('Time domain')
ax1.set_xlabel('t')
ax1.set_ylabel('s(t)')
ax1.set_xlim([0, 10])
ax1.set_ylim([-1.5, 1.5])
ax1.grid(color='lightgray', which='both')
ax1.set_xticklabels([])
ax1.set_yticklabels([])

# fill_between



# Access the second subplot
ax2 = axs[1]
ax2.set_title('Frequency domain')
ax2.plot(f, amp_spectrum)
ax2.set_ylabel('|s|')
ax2.set_xlabel('f')
ax2.set_xlim([0, 4])
ax2.set_ylim([0, 0.025])
ax2.grid(color='lightgray', which='both')
ax2.set_xticklabels([])
ax2.set_yticklabels([])


# Show the figure with the subplots
fig.tight_layout(pad=1)
plt.show()
