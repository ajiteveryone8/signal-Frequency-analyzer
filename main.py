import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from matplotlib.widgets import Slider

# Open a file dialog to select the CSV file
root = Tk()
root.withdraw()  # Hide the root Tkinter window

# Open the file dialog
file_path = askopenfilename(filetypes=[("CSV files", "*.csv")], title="Select a CSV file")

# Destroy the root window after the file dialog is closed
root.destroy()

if not file_path:
    print("No file selected. Exiting...")
    exit()

# Load the data from the selected CSV file
data = pd.read_csv(file_path)

# Extract columns
time = data['time']
x = data['X']
y = data['Y']

# Plot the time-domain data
plt.figure(figsize=(10, 5))
plt.plot(time, x, label='X')
plt.plot(time, y, label='Y')
plt.title('Time-Domain Signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid()
plt.show()


# Plot the time-domain data
plt.figure(figsize=(10, 5))
plt.plot(x, y, label='Y')
plt.title('X-Y Signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid()
plt.show()

# Compute FFT
sampling_interval = time.diff().mean()  # Calculate sampling interval
sampling_rate = 1 / sampling_interval  # Sampling rate
n = len(time)  # Number of samples

# FFT for X
fft_x = np.fft.fft(x)
frequencies = np.fft.fftfreq(n, d=sampling_interval)

# Filter frequencies and amplitudes for X and Y up to 10 Hz
max_frequency = 10  # Limit to 10 Hz
valid_indices = frequencies[:n // 2] <= max_frequency

# FFT for Y
fft_y = np.fft.fft(y)






# Normalize FFT amplitudes
normalized_fft_x = np.abs(fft_x[:n // 2]) / max(np.abs(fft_x[:n // 2]))
normalized_fft_y = np.abs(fft_y[:n // 2]) / max(np.abs(fft_y[:n // 2]))

filtered_frequencies_x = frequencies[:n // 2][valid_indices]
filtered_normalized_fft_x = normalized_fft_x[valid_indices]

filtered_frequencies_y = frequencies[:n // 2][valid_indices]
filtered_normalized_fft_y = normalized_fft_y[valid_indices]

# Plot normalized FFT for X and Y
plt.figure(figsize=(10, 5))
plt.plot(filtered_frequencies_x, filtered_normalized_fft_x, label='Normalized FFT of X', color='blue')
plt.plot(filtered_frequencies_y, filtered_normalized_fft_y, label='Normalized FFT of Y', color='orange')
plt.title('Normalized Frequency-Domain Signal (FFT of X and Y)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Normalized Amplitude')
plt.legend()
plt.grid()
plt.show()


# Define a threshold for normalized amplitude
threshold_normalized = 0.1  # Example: 30% of the maximum normalized amplitude

# Filter frequencies and amplitudes for X
high_amp_indices_x = normalized_fft_x > threshold_normalized
filtered_frequencies_x = frequencies[:n // 2][high_amp_indices_x]
filtered_amplitudes_x = normalized_fft_x[high_amp_indices_x]

# Filter frequencies and amplitudes for Y
high_amp_indices_y = normalized_fft_y > threshold_normalized
filtered_frequencies_y = frequencies[:n // 2][high_amp_indices_y]
filtered_amplitudes_y = normalized_fft_y[high_amp_indices_y]



# Remove zero frequency (DC component) for X
non_zero_indices_x = filtered_frequencies_x != 0
filtered_frequencies_x = filtered_frequencies_x[non_zero_indices_x]
filtered_amplitudes_x = filtered_amplitudes_x[non_zero_indices_x]

# Remove zero frequency (DC component) for Y
non_zero_indices_y = filtered_frequencies_y != 0
filtered_frequencies_y = filtered_frequencies_y[non_zero_indices_y]
filtered_amplitudes_y = filtered_amplitudes_y[non_zero_indices_y]

# Plot filtered normalized FFT points for X and Y without zero frequency
plt.figure(figsize=(10, 5))
plt.scatter(filtered_frequencies_x, filtered_amplitudes_x, label='High Amplitude FFT of X', color='blue')
plt.scatter(filtered_frequencies_y, filtered_amplitudes_y, label='High Amplitude FFT of Y', color='orange')
plt.title('High Amplitude Frequency Points (Normalized FFT of X and Y, No DC Component)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Normalized Amplitude')
plt.legend()
plt.grid()
plt.show()


# Ensure all arrays have the same length by padding with NaN if necessary
max_length = max(len(filtered_frequencies_x), len(filtered_frequencies_y))

# Pad filtered frequencies and amplitudes for X
filtered_frequencies_x = np.pad(filtered_frequencies_x, (0, max_length - len(filtered_frequencies_x)), constant_values=np.nan)
filtered_amplitudes_x = np.pad(filtered_amplitudes_x, (0, max_length - len(filtered_amplitudes_x)), constant_values=np.nan)

# Pad filtered frequencies and amplitudes for Y
filtered_frequencies_y = np.pad(filtered_frequencies_y, (0, max_length - len(filtered_frequencies_y)), constant_values=np.nan)
filtered_amplitudes_y = np.pad(filtered_amplitudes_y, (0, max_length - len(filtered_amplitudes_y)), constant_values=np.nan)

# Save filtered frequency and amplitude data for X and Y to a CSV file
filtered_data = pd.DataFrame({
    'Frequency_X': filtered_frequencies_x,
    'Amplitude_X': filtered_amplitudes_x,
    'Frequency_Y': filtered_frequencies_y,
    'Amplitude_Y': filtered_amplitudes_y
})

# Get the base name of the selected file and append '_output' to it
base_name = os.path.basename(file_path)  # Extract the file name with extension
file_name, file_ext = os.path.splitext(base_name)  # Split into name and extension
output_file_name = f"{file_name}_output{file_ext}"  # Add '_output' before the extension

# Create the output folder if it doesn't exist
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Construct the full path for the output file
output_file_path = os.path.join(output_folder, output_file_name)

# Save to the constructed file path
filtered_data.to_csv(output_file_path, index=False)

print("Filtered frequency and amplitude data saved to 'filtered_fft_data.csv'")



# Generate a sine wave using filtered frequencies and amplitudes
generated_time = np.linspace(0, max(time), len(time))  # Create a time array matching the original time
generated_signal = np.zeros_like(generated_time)  # Initialize the generated signal

# Compute the phase of the FFT for X
phases_x = np.angle(fft_x[:n // 2])  # Extract the phase information for X

# Filter the phases corresponding to the filtered frequencies
filtered_phases_x = phases_x[high_amp_indices_x]

# Remove zero frequency (DC component) for phases
filtered_phases_x = filtered_phases_x[non_zero_indices_x]

# Generate a sine wave using filtered frequencies, amplitudes, and phases
generated_signal = np.zeros_like(generated_time)  # Initialize the generated signal

# Add sine waves for each frequency, amplitude, and phase
for freq, amp, phase in zip(filtered_frequencies_x, filtered_amplitudes_x, filtered_phases_x):
    if not np.isnan(freq):  # Skip NaN values
        generated_signal += amp * np.sin(2 * np.pi * freq * generated_time + phase)


# Initialize the figure and axes
fig, ax = plt.subplots(figsize=(10, 5))
plt.subplots_adjust(left=0.1, bottom=0.25)  # Adjust space for sliders

# Plot the original signal
original_line, = ax.plot(time, x, label='Actual X Signal', color='blue')

# Generate the initial sine wave
generated_signal = np.zeros_like(generated_time)
for freq, amp, phase in zip(filtered_frequencies_x, filtered_amplitudes_x, filtered_phases_x):
    if not np.isnan(freq):  # Skip NaN values
        generated_signal += amp * np.sin(2 * np.pi * freq * generated_time + phase)

# Plot the generated sine wave
generated_line, = ax.plot(generated_time, generated_signal, label='Generated Signal Using FFT', color='orange', linestyle='dashed')

# Add legend explicitly with the top-right corner location
ax.legend(loc='upper right')  # Move the legend to the top-right corner

# Add sliders for amplitude and phase
ax_amp = plt.axes([0.1, 0.1, 0.65, 0.03])  # Position for amplitude slider
ax_phase = plt.axes([0.1, 0.15, 0.65, 0.03])  # Position for phase slider

slider_amp = Slider(ax_amp, 'Amplitude', 0.1, 5.0, valinit=1.0)  # Amplitude slider
slider_phase = Slider(ax_phase, 'Phase', -np.pi, np.pi, valinit=0.0)  # Phase slider

# Update function for sliders
def update(val):
    amp_factor = slider_amp.val
    phase_shift = slider_phase.val

    # Regenerate the sine wave with updated amplitude and phase
    updated_signal = np.zeros_like(generated_time)
    for freq, amp, phase in zip(filtered_frequencies_x, filtered_amplitudes_x, filtered_phases_x):
        if not np.isnan(freq):  # Skip NaN values
            updated_signal += amp_factor * amp * np.sin(2 * np.pi * freq * generated_time + phase + phase_shift)

    # Update the generated line
    generated_line.set_ydata(updated_signal)
    fig.canvas.draw_idle()

# Connect sliders to the update function
slider_amp.on_changed(update)
slider_phase.on_changed(update)

# Show the interactive plot
plt.show()