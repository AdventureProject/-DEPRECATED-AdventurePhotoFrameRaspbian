from __future__ import print_function
from pygame.locals import *
import os
import time
import urllib, json
import pygame
from PIL import Image
from resizeimage import resizeimage


def download_photo():
	print('fetching data...')

	file_name = 'current.jpg'
	image_key = 'image'
	url = "http://wethinkadventure.rocks/photoframe"

	try:
		response = urllib.urlopen(url)
		response_code = response.getcode()

		if response_code is not None and response_code is 200:
			print('parsing data...')

			data = json.loads(response.read())
			if data is not None and image_key in data:
				image_url = data[image_key]

				print(image_url)
				print('downloading image ...')

				temp_file_name = file_name + '.tmp'

				f = open(temp_file_name, 'wb')
				f.write(urllib.urlopen(image_url).read())
				f.close()

				os.rename(temp_file_name, file_name)
			else:
				print('failed to parse data...')
		else:
			print('failed with status code: ' + str(response_code))
	except ValueError:
		print('Decoding JSON has failed')
	except urllib.error.URLError as e:
		print(e.reason)
	except IOError:
		print('Failed to open connection')

	return file_name


def get_photo():
	file_name = download_photo()

	print('loading image...')

	with open(file_name, 'r+b') as f:
		with Image.open(f) as image:
			cover = resizeimage.resize_cover(image, [w, h])
			cover.save(file_name, image.format)

	image = pygame.image.load(file_name)

	return image


def show_loading():
	loading_img = pygame.image.load('/app/loading.png')
	show_image(loading_img)


def text(txt, position):
	font = pygame.font.Font(None, 64)
	scoretext = font.render(txt, 1, (255, 255, 255))
	screen.blit(scoretext, position)


def show_image(image):
	screen.fill(black)
	if image is not None:
		screen.blit(image, (0, 0))

	pygame.display.flip()


class Timer:
	def __init__(self):
		pass

	startTime = 0
	interval = 0

	def start(self, interval):
		self.startTime = time.time()
		self.interval = interval

	def timer_is_up(self):
		return time.time() > (self.startTime + self.interval)

	def elapsed_time(self):
		return time.time() - self.startTime


# START EXECUTION

# sys.stdout = open("/home/pi/logs/adventure_app.log", "w")

print('Starting Adventure.Rocks!')

print('starting display')

black = (0, 0, 0)
w = 800
h = 480

pygame.init()
screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
screen.fill(black)
pygame.mouse.set_visible(0)
pygame.display.set_caption('Adventure.Rocks')

show_loading()

img = get_photo()

intervalSeconds = 5 * 60

timer = Timer()
timer.start(intervalSeconds)

running = True
while running:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.KEYUP:
			if event.type == pygame.QUIT:
				running = False
			if event.key == pygame.K_ESCAPE:
				running = False
		if event.type == pygame.MOUSEBUTTONUP:
			# pos = pygame.mouse.get_pos()
			print('User wants a new image')
			show_loading()
			img = get_photo()
			timer.start(intervalSeconds)

	if timer.timer_is_up():
		print('Rotating to new image')
		show_loading()
		img = get_photo()
		timer.start(intervalSeconds)

	show_image(img)

pygame.display.quit()

print('done.')
