from email.mime import audio
# Std. Lib. Imports
import logging
import sys

# External
import speech_recognition as sr

def recognize_speech_from_file(file_location: str):
	harvard_sentences = sr.AudioFile(file_location)
	if not harvard_sentences:
		logging.error('Unable to load Audio File')
		sys.exit()

	r = sr.Recognizer()
	with harvard_sentences as source:
		audio = r.record(source, duration=32)

	if not audio:
		logging.error('Cannot read audio')
		sys.exit()

	r.recognize_google(audio)

if __name__ == '__main__':
	sentences = './audio_samples/Harvard_Sentences.wav'