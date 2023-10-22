#!/usr/bin/env python3

from os import chdir, listdir, remove
from os.path import splitext
from argparse import ArgumentParser
from dotenv import dotenv_values

CONTENT_DIR = dotenv_values()['CONTENT_DIR']
chdir(CONTENT_DIR)

parser = ArgumentParser()
parser.add_argument("-d", "--dry-run", action="store_true")
args = parser.parse_args()

info_ids = {splitext(f)[0] for f in listdir("info") if f.endswith('.yaml')}
music_ids = {splitext(f)[0] for f in listdir("music") if f.endswith('.opus')}
png_ids = {splitext(f)[0] for f in listdir("artwork/png") if f.endswith('.png')}
webp_ids = {splitext(f)[0] for f in listdir("artwork/webp") if f.endswith('.webp')}

# no info but we have artwork/music
for i in music_ids - info_ids:
	print(i + ".opus")
	if not args.dry_run:
		remove(f"music/{i}.opus")
for i in png_ids - info_ids:
	print(i + ".png")
	if not args.dry_run:
		remove(f"artwork/png/{i}.png")
for i in webp_ids - info_ids:
	print(i + ".webp")
	if not args.dry_run:
		remove(f"artwork/webp/{i}.webp")

# no music but we have info/artwork
for i in info_ids - music_ids:
	print(i + ".yaml")
	if not args.dry_run:
		remove(f"info/{i}.yaml")
for i in png_ids - music_ids:
	print(i + ".png")
	if not args.dry_run:
		remove(f"artwork/png/{i}.png")
for i in webp_ids - music_ids:
	print(i + ".webp")
	if not args.dry_run:
		remove(f"artwork/webp/{i}.webp")

# no artwork (png) but we have info/music
for i in info_ids - png_ids:
	print(i + ".yaml")
	if not args.dry_run:
		remove(f"info/{i}.yaml")
for i in music_ids - png_ids:
	print(i + ".png")
	if not args.dry_run:
		remove(f"artwork/png/{i}.png")
