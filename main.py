from __future__ import print_function
from pygame.locals import *
import sys
import time
import urllib, json
import pygame


def downloadPhoto():
	print('fetching data...')
	url = "http://wethinkadventure.rocks/random"
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	imageUrl = data['image']

	print(imageUrl)
	print('downloading image ...')

	fileName = 'current.jpg'
	f = open(fileName, 'wb')
	f.write(urllib.urlopen(imageUrl).read())
	f.close()

	return fileName


def getPhoto():
	fileName = downloadPhoto()

	print('loading image...')

	img = pygame.image.load(fileName)
	img = pygame.transform.scale(img, (w, h))

	return img


def showLoading():
	loadingImg = pygame.image.load('/app/loading.png')
	showImage(loadingImg)


def showImage(image):
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
		self.startTime = time.clock()
		self.interval = interval

	def timerIsUp(self):
		return time.clock() > (self.startTime + self.interval)


### START EXECUTION

sys.stdout = open("/home/pi/logs/adventure_app.log", "w")

print('Starting Adventure.Rocks!')

print('starting display')

black = (0, 0, 0)
w = 800
h = 480

screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
screen.fill(black)
pygame.mouse.set_visible(0)
pygame.display.set_caption('Adventure.Rocks')

showLoading()

img = getPhoto()

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
			showLoading()
			img = getPhoto()
			timer.start(intervalSeconds)

	if timer.timerIsUp():
		print('Rotating to new image')
		showLoading()
		img = getPhoto()
		timer.start(intervalSeconds)

	showImage(img)

pygame.display.quit()

print('done.')
