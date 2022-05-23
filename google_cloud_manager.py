# Standard Lib. Imports
import multiprocessing
from threading import Thread
from multiprocessing import Process
from queue import Queue
import logging

# Local Imports
from config import GOOGLE_CLOUD_SPEECH_CREDENTIALS
from extraction import json_extract
from visualization import Visualizer

# 3rd Party Imports
import speech_recognition as sr
import matplotlib.pyplot as audio_plot

r = sr.Recognizer()
audio_queue = Queue()
prepare_queue = multiprocessing.Queue()
show_queue = multiprocessing.Queue()

def recognize_worker():
	"""Runs in a background thread via daemon
	"""
	while True:
		audio = audio_queue.get() # Retrieve the next audio processing job from the main thread.
		if audio is None: break # Process stops if the main thread completes

		# Audio data recieved, recognize it with GSR
		try:
			# For testing purposes, the default API key is being
			# used for Google Speech Recognition.
			result = r.recognize_google_cloud(audio, GOOGLE_CLOUD_SPEECH_CREDENTIALS, show_all=True)
			speech = json_extract(result, 'transcript')
			print(f'Google Cloud Speech Recognition Prediction: \n{speech}')

		except sr.UnknownValueError:
			logging.warning('Google Cloud Speech Recognition could not recognize audio')
		except sr.RequestError as e:
			logging.fatal(f'Could not request results from Google Cloud Speech Recognition service; {e}')

		audio_queue.task_done() # Mark audio processing job as complete in the queue

if __name__ == '__main__':
	# Start a new thread to recognize audio, while this thread focuses on listening
	recognize_thread = Thread(target=recognize_worker, daemon=True)
	recognize_thread.start()

	# The challenge here is that we need to pass the audio input recieved
	# from the microphone to properly instantiate the Visualizer class.
	# ...Unless we set all of the Visualizer class attributes equal to None.
	# But isn't this a horrible practice? I have a gut feeling it is.
	prepare_pc = Process(target=Visualizer.prepare_audio, args=())
	prepare_pc.start()
	show_pc = Process(target=Visualizer.show_audio, args=())
	show_pc.start()

	with sr.Microphone() as source:
		try:
			while True:
				# repeatedly listen for phrases and put the resulting audio on the audio processing job queue
				r.adjust_for_ambient_noise(source, duration=1)
				input = r.listen(source, timeout=30, phrase_time_limit=15)
				audio_queue.put(input)

				# Visualizing

		except KeyboardInterrupt: # Ctrl + C shuts program down.
			pass

	audio_queue.join() # Block until all current audio processing jobs are done
	audio_queue.put(None) # Tell the recognize_thread to stop
	recognize_thread.join() # Wait for the recognize_thread to actually stop

	prepare_queue.join()
	prepare_queue.put(None)
	prepare_pc.join()

	show_queue.join()
	show_queue.put(None)
	show_pc.join()
	



