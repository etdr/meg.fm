#!/usr/bin/env python3

import os
import signal
from uuid import uuid4
from datetime import datetime
from argparse import ArgumentParser
from time import sleep
from dotenv import dotenv_values
# from pynput import keyboard
from ruamel.yaml import YAML

from utils import banner, printline
from descriptions import get_descriptions, MODEL as DESC_MODEL
from music import generate_music
from metadata import get_metadata, MODEL as METADATA_MODEL
	# SYSPROMPT_VERSION as META_SYSP_VER
	# MODEL as METADATA_MODEL
from artwork import get_artwork, ARTSOURCE as ART_MODEL

PIDFILE = "/tmp/meg.fm-generator.pid"

config = dotenv_values()
CONTENT_DIR = config['CONTENT_DIR']

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

def filter_data_incompleteness(selections):
	def selection_is_ok(s):
		if 'description' not in s or not s['description'] \
		  or 'metadata' not in s or not s['metadata'] \
		  or 'artist' not in s['metadata'] or 'title' not in s['metadata'] \
		  or 'year' not in s['metadata']:
			return False
		return True
	
	filtered = [s for s in selections if selection_is_ok(s)]
	num_filtered = len(selections) - len(filtered)
	if num_filtered:
		print(f"filtered {num_filtered} selections with incomplete text data")
	return filtered
			

def generate_tracks(n, batch_num=0):
	time_start = datetime.now()
	print(f"starting generation of {n} objects at {time_start.isoformat()}")

	descs_list = get_descriptions(n)

	selections = [
		{
			'uuid': str(uuid4()),
			'description': d,
			'created': time_start,
			'sources': {
				'description': DESC_MODEL,
				'metadata': METADATA_MODEL,
				'artwork': ART_MODEL,
				'music': 'audiocraft'
			}
		}
		for d
		in descs_list
	]

	get_metadata(selections)
	selections = filter_data_incompleteness(selections)

	get_artwork(selections)
	generate_music(selections)

	for s in selections:
		with open(f"{CONTENT_DIR}/info/{s['uuid']}.yaml", 'wt') as f:
			yaml.dump(s, f)

	time_end = datetime.now()
	runtime_mins = (time_end - time_start).seconds / 60
	print(f"{f'BATCH {batch_num}: ' if batch_num != 0 else ''}generated {len(selections)} tracks in {runtime_mins:<4.4} minutes")
	print(f"roughly {len(selections) / runtime_mins:<3.3} tracks per minute")
	return len(selections)


def batch_generate_tracks(batches, batch_size):
	num_generated = 0
	for i in range(batches):
		banner(f"COMMENCING WITH BATCH {i + 1} OF {batches}", 1)
		num_generated += generate_tracks(batch_size, i + 1)
	return num_generated


if __name__ == "__main__":
	pid = str(os.getpid())
	with open(PIDFILE, 'w') as pidf:
		pidf.write(pid)

	parser = ArgumentParser(description="generates batches of hypothetical music and associated data")
	parser.add_argument("n", type=int, help="number of tracks to generate per batch")
	parser.add_argument("-b", "--batches", type=int, help="number of batches", default=1)
	parser.add_argument("-u", "--until", type=str, help="time to generate until", default='')
	parser.add_argument("-i", "--indefinite", action="store_true", help="keep generating until manual exit")
	# add arguments (when applicable) for:
	#   - description model selection
	#   - metadata model selection
	#   - artwork model selection
	args = parser.parse_args()

	if args.until:
		time_until = datetime.fromisoformat(args.until)
	else:
		time_until = datetime.max
	time_start = datetime.now()

	exit_generation = False
	def handle_sigusr1(signum, frame):
		global exit_generation
		print("Exiting after this batch...")
		exit_generation = True
	signal.signal(signal.SIGUSR1, handle_sigusr1)

	# def stop_after_this(k):
	# 	global exit_generation
	# 	if k == keyboard.Key.esc:
	# 		exit_generation = True
	# 		print("exiting after current batch")
	# key_listener = keyboard.Listener(on_press=stop_after_this)
	# key_listener.start()

	if args.indefinite:
		num_generated = 0
		banner("GENERATING INDEFINITELY", 0)
		while not exit_generation:
			banner("ANOTHER ONE")
			num_generated += generate_tracks(args.n)
	elif args.until:
		num_generated = 0
		banner("STARTING UNTIL RUN", 0)
		while not exit_generation and datetime.now() < time_until:
			banner("EXIT TIME NOT REACHED, COMMENCING SINGLE BATCH")
			num_generated += generate_tracks(args.n)
	else:
		while not exit_generation:
			if args.batches == 1:
				banner("COMMENCING WITH SINGLE BATCH", 0)
				num_generated = generate_tracks(args.n)
				break
			else:
				banner(f"STARTING RUN OF {args.batches} BATCHES", 0)
				num_generated = batch_generate_tracks(args.batches, args.n)
				break
	
	# key_listener.stop()
	time_end = datetime.now()
	runtime_mins = (time_end - time_start).seconds / 60
	printline(1)
	if exit_generation:
		print("Exiting on request")
	print(f"TOTAL RUN: generated {num_generated} tracks in {runtime_mins:<4.4} minutes")
	print(f"roughly {num_generated / runtime_mins:<3.3} tracks per minute")
	banner("GENERATION COMPLETE! 💯", 0)

	os.unlink(PIDFILE)


