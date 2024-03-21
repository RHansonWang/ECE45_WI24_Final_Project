import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

def generate_random_sound(sample_rate=44100, duration=1.0):
    fundamental_frequency = 440.0
    num_harmonics = 3
    harmonic_variation = 30 
    frequencies = fundamental_frequency * np.arange(1, num_harmonics + 1, dtype=np.float64)
    frequencies += np.random.uniform(-harmonic_variation, harmonic_variation, size=num_harmonics)
    amplitude_range = (0.25, 1.0)
    amplitudes = np.random.uniform(amplitude_range[0], amplitude_range[1], size=num_harmonics)
    phases = np.random.uniform(0, 2 * np.pi, size=num_harmonics)
    n_samples = int(sample_rate * duration)
    t = np.arange(n_samples) / sample_rate
    signal = np.zeros(n_samples)
    for f, a, p in zip(frequencies, amplitudes, phases):
        signal += a * np.sin(2 * np.pi * f * t + p)
        
    signal = signal / np.max(np.abs(signal))
    return t, signal

def apply_fourier_transform_modification(signal, sample_rate, cutoff_frequency):
    fft_result = np.fft.fft(signal)
    frequency_bins = np.fft.fftfreq(len(signal), d=1/sample_rate)
    fft_result[np.abs(frequency_bins) > cutoff_frequency] = 0
    modified_signal = np.fft.ifft(fft_result)
    return np.real(modified_signal)  


sample_rate = 44100  
duration = 1.0  
t, signal = generate_random_sound(sample_rate, duration)


cutoff_frequency = 1000  
modified_signal = apply_fourier_transform_modification(signal, sample_rate, cutoff_frequency)


print("Playing original sound...")
sd.play(signal, sample_rate)
sd.wait()


print("Playing modified sound...")
sd.play(modified_signal, sample_rate)
sd.wait()


plt.figure(figsize=(10, 8))
plt.subplot(2, 1, 1)
plt.plot(t[:1000], signal[:1000])
plt.title('Original Sound Waveform')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(t[:1000], modified_signal[:1000])
plt.title('Modified Sound Waveform (After FFT Modification)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.grid(True)

plt.tight_layout()
plt.show()
