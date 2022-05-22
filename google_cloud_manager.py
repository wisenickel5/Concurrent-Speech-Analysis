# Standard Lib. Imports
from threading import Thread
from queue import Queue
import logging
import json

# Local Imports
from config import GOOGLE_CLOUD_SPEECH_CREDENTIALS

# 3rd Party Imports
import speech_recognition as sr

r = sr.Recognizer()
audio_queue = Queue()

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
			formatted_result = json.dumps(result, indent=2)
			print(f'Google Cloud Speech Recognition Prediction: \n{formatted_result}')

		except sr.UnknownValueError:
			logging.warning('Google Cloud Speech Recognition could not recognize audio')
		except sr.RequestError as e:
			logging.fatal(f'Could not request results from Google Cloud Speech Recognition service; {e}')

		audio_queue.task_done() # Mark audio processing job as complete in the queue

recognize_thread = Thread(target=recognize_worker)
recognize_thread.daemon = True
recognize_thread.start()

with sr.Microphone() as source:
	try:
		while True:
			r.adjust_for_ambient_noise(source, duration=1)
			audio_queue.put(r.listen(source))
	except KeyboardInterrupt: # Ctrl + C shuts program down.
		pass

audio_queue.join()
audio_queue.put(None)
recognize_thread.join()
