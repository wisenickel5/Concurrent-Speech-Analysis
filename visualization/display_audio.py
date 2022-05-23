# Standard Library
import time
from multiprocessing import Process, Value

# Local

# 3rd Party
import numpy as np
import matplotlib.pyplot as plt

class Visualizer(Process):
	"""The goal here is to to extend the multiprocessing.Process class and add 
	attributes that need to be accessed from multiple processes. In specific, 
	data must be shared between two processes that will be running the
	prepare_audio() & show_audio_functions.
	Ref: https://superfastpython.com/share-process-attributes/

	Args:
		Process (_type_): _description_
	"""
	def __init__(self, plot: plt, audio=None):
		Process.__init__(self)
		self.audio = audio
		self.frame_data = Value('i', 0) # Buffer String
		self.sample_rate = Value('i', 0)
		self.sample_width = Value('i', 0)
		self.audio_arrays = Value('i', 0)
		self.plot = plot
		self.time_axis = Value('i', 0) # n-dimentsional array
		self.sound_axis = Value('i', 0) # Array

	def prepare_audio(self) -> None:
		if self.audio: # If audio is detected, set the class attributes
			self.frame_data = self.audio['frame_data']
			self.sample_rate = self.audio['sample_rate']
			self.sample_width = self.audio['sample_width']
			
			self.audio_arrays = len(self.frame_data)
			# Assumes sample width is 2
			ch1 = np.array([self.frame_data[i][0] for i in range(self.audio_arrays)]) # Channel 1
			ch2 = np.array([self.frame_data[i][1] for i in range(self.audio_arrays)]) # Channel 2

			self.time_axis = np.linspace(0, self.audio_arrays/self.sample_rate, self.audio_arrays, endpoint=False)
			self.sound_axis = ch1

	def show_audio(self) -> None:
		if self.audio: # If audio is detected, begin displaying the plot
			previous_time = time.time()
			self.plot.ion()

			spent_time = 0
			update_periodicity = 2 # Expressed in seconds

			for i in range(self.audio_arrays):
				# For every second, increase spent_time by one
				if i // self.sample_rate != (i-1) // self.sample_rate:
					spent_time += 1
				if spent_time == update_periodicity:
					# Plotting commands
					self.plot.clf() # Clear previous plot
					self.plot.plot(self.time_axis, self.sound_axis)
					self.plot.xlabel('Time (s)')
					self.plot.ylabel('Audio')
					self.plot.axvline(x= i/self.sample_rate, color='r') # Plot a red line to keep track of the progession
					self.plot.show()
					self.plot.pause(update_periodicity - (time.time() - previous_time))

					# Implementing a forced pause to synchronize the audio 
					# being played with the audio track being displayed
					previous_time = time.time()
					spent_time = 0



