import numpy as np
import sounddevice as sd
from tkinter import Tk, Scale, HORIZONTAL, OptionMenu, StringVar, Button, Label

# Global synthesizer parameters
frequency = 440.0  # Starting frequency in Hz
volume = 0.5       # Starting volume (0.0 to 1.0)
sample_rate = 44100  # Audio sample rate
duration = 1.0  # Duration of tone in seconds
waveform_type = 'sine'  # Type of waveform
reverb_enabled = False  # Reverb effect toggle
pulse_width = 0.5  # Pulse width (only for pulse waveform)

def generate_waveform(wave_type, frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    if wave_type == 'sine':
        return np.sin(2 * np.pi * frequency * t)
    elif wave_type == 'square':
        return np.sign(np.sin(2 * np.pi * frequency * t))
    elif wave_type == 'sawtooth':
        return 2 * (t * frequency - np.floor(1/2 + t * frequency))
    elif wave_type == 'triangle':
        return 2 * np.abs(2 * (t * frequency - np.floor(1/2 + t * frequency))) - 1
    elif wave_type == 'pulse':
        return np.where((t % (1/frequency)) < (1/frequency) * pulse_width, 1, -1)
    elif wave_type == 'noise':
        return np.random.uniform(low=-1.0, high=1.0, size=int(sample_rate * duration))
    else:
        return np.zeros_like(t)

def apply_reverb(signal, decay=0.6, delay_ms=50):
    delay_samples = int(delay_ms * sample_rate / 1000)
    output = np.copy(signal)
    for i in range(delay_samples, len(signal)):
        output[i] += decay * output[i - delay_samples]
    return output

def audio_callback(outdata, frames, time, status):
    global frequency, volume, waveform_type, reverb_enabled
    tone = generate_waveform(waveform_type, frequency, frames / sample_rate, sample_rate)
    if reverb_enabled:
        tone = apply_reverb(tone)
    outdata[:, 0] = volume * tone

def update_frequency(val):
    global frequency
    frequency = float(val)

def update_volume(val):
    global volume
    volume = float(val) / 100

def toggle_reverb():
    global reverb_enabled
    reverb_enabled = not reverb_enabled

def change_waveform(wave_type):
    global waveform_type
    waveform_type = wave_type
    pulse_width_label.pack_forget()
    pulse_width_slider.pack_forget()
    if wave_type == 'pulse':
        pulse_width_label.pack()
        pulse_width_slider.pack()

def update_pulse_width(val):
    global pulse_width
    pulse_width = float(val) / 100


root = Tk()
root.title("Synthesizer")

frequency_slider = Scale(root, from_=20, to=2000, orient=HORIZONTAL, label="Frequency", command=update_frequency)
frequency_slider.set(frequency)
frequency_slider.pack()

volume_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Volume", command=update_volume)
volume_slider.set(volume * 100)
volume_slider.pack()

waveform_var = StringVar(root)
waveform_var.set(waveform_type)  
waveform_menu = OptionMenu(root, waveform_var, "sine", "square", "sawtooth", "triangle", "pulse", "noise", command=change_waveform)
waveform_menu.pack()

reverb_button = Button(root, text="Toggle Reverb", command=toggle_reverb)
reverb_button.pack()

pulse_width_label = Label(root, text="Pulse Width")
pulse_width_slider = Scale(root, from_=1, to=99, orient=HORIZONTAL, label="Pulse Width (%)", command=update_pulse_width)
pulse_width_slider.set(pulse_width * 100)

stream = sd.OutputStream(callback=audio_callback, samplerate=sample_rate, channels=1)
stream.start()
root.mainloop()
stream.stop()
