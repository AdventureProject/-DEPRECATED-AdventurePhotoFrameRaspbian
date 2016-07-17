from pygame.locals import *
import os
import os.path
import time
import urllib2
import json
import pygame
from subprocess import call
from PIL import Image
from resizeimage import resizeimage
from datetime import datetime

DATA_DIR = 'data/'

def log(msg):
	print msg
	
	with open('logs/app.log', 'a') as f:
		now = str(datetime.now())
		f.write(now + ' - \t' + msg + '\n')


def download_image( url, filename ):
	temp_file_name = filename + ".tmp"

	# Write out bitmap to disk
	with open(temp_file_name, 'wb') as f:
		f.write(urllib2.urlopen(url).read())
		if os.path.getsize(temp_file_name) > 0:
			log('File download complete, move to complete')
			os.rename(temp_file_name, filename)
		else:
			log('File download FAILED, delete temp')
			os.remove(temp_file_name)


def download_photo( photo_frame_id ):
	log('fetching data...')

	info_file_name = DATA_DIR+'current.info'

	bitmap_file_name = DATA_DIR+'current.jpg'
	image_key = 'image'
	url = "http://wethinkadventure.rocks/photoframe/" + photo_frame_id

	# Init with all the current info
	curent_photo = PhotoInfo()
	curent_photo.file_name = bitmap_file_name
	if os.path.isfile(info_file_name):
		with open(info_file_name,'r') as f:
			data = f.read()
			if data:
				curent_photo.info = json.loads(data)

	try:
		response = urllib2.urlopen(url)
		response_code = response.getcode()

		if response_code is not None and response_code is 200:
			log('parsing data...')

			data_str = response.read()
			data = json.loads(data_str)
			if data is not None and image_key in data:
				image_url = data[image_key]

				log(image_url)
				log('downloading image ...')

				# Write out bitmap to disk
				download_image(image_url, bitmap_file_name)

				log('writing info to file ...')
				# Write all our info data to disk
				with open(info_file_name, "w") as f:
					f.write(data_str)
				curent_photo.info = data
			else:
				log('failed to parse data...')
		else:
			log('failed with status code: ' + str(response_code))
	except ValueError:
		log('Decoding JSON has failed')
	except urllib2.URLError as e:
		log('URLError: ' + str(e.reason))
	except IOError:
		log('Failed to open connection')

	return curent_photo


def get_photo( photo_frame_id ):
	curent_photo = download_photo( photo_frame_id )

	log('loading image...')

	with open(curent_photo.file_name, 'r+b') as f:
		log('file opened')
		with Image.open(f) as image:
			log('image opened')
			cover = resizeimage.resize_cover(image, [w, h])
			log('file resize complete')
			cover.save(curent_photo.file_name, image.format)
			log('image saved to disk')

	curent_photo.bitmap = pygame.image.load(curent_photo.file_name)
	if curent_photo.bitmap is None:
		log('failed to decode image!')

	return curent_photo


FILE_NAME_MAP_ZOOM_IN = DATA_DIR+"map_zoomed_in.png"
FILE_NAME_MAP_ZOOM_OUT = DATA_DIR+"map_zoomed_out.png"
def download_map_images(photo_info):
	photo_info.location_images = MapImages()
	
	location = photo_info.info['location']
	if location:
		try:
			download_image(get_google_maps_small_view_url(location),FILE_NAME_MAP_ZOOM_IN)
			photo_info.location_images.zoomed_in = pygame.image.load(FILE_NAME_MAP_ZOOM_IN)
		except urllib2.URLError as e:
			log('URLError: ' + str(e.reason))
		except IOError:
			log('Failed to open connection')

		try:
			download_image(get_google_maps_large_view_url(photo_info.info['location']), FILE_NAME_MAP_ZOOM_OUT)
			photo_info.location_images.zoomed_out = pygame.image.load(FILE_NAME_MAP_ZOOM_OUT)
		except urllib2.URLError as e:
			log('URLError: ' + str(e.reason))
		except IOError:
			log('Failed to open connection')

	return photo_info.location_images


# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def draw_text(surface, text, color, rect, font, aa=False, bkg=None):
	rect = Rect(rect)
	y = rect.top
	line_spacing = -2

	# get the height of the font
	font_height = font.size("Tg")[1]

	while text:
		i = 1

		# determine if the row of text will be outside our area
		if y + font_height > rect.bottom:
			break

		# determine maximum width of line
		while font.size(text[:i])[0] < rect.width and i < len(text):
			i += 1

		# if we've wrapped the text, then adjust the wrap to the last word
		if i < len(text):
			i = text.rfind(" ", 0, i) + 1

		# render the line and blit it to the surface
		if bkg:
			image = font.render(text[:i], 1, color, bkg)
			image.set_colorkey(bkg)
		else:
			image = font.render(text[:i], aa, color)

		surface.blit(image, (rect.left, y))
		y += font_height + line_spacing

		# remove the text we just blitted
		text = text[i:]

	return text


def draw_text_in_box(surface, text_string, rect, font):
	rendered_text = font.render(text_string, True, BLACK)
	text_rect = rendered_text.get_rect()
	halfWidth = rect.width/2
	halfHeight = rect.height/2

	surface.blit(rendered_text, [rect.left + halfWidth - (text_rect.width/2), rect.top + halfHeight - (text_rect.height/2)])


def draw_text_simple(txt, position, color, font, surface):
	log('Show text: ' + txt)
	rendered_text = font.render(txt, 1, color)
	surface.blit(rendered_text, position)


def show_loading():
	log('Show loading screen.')
	loading_img = pygame.image.load('/app/loading.png')

	screen.fill(BLACK)
	if loading_img is not None:
		screen.blit(loading_img, (0, 0))
	pygame.display.flip()


def render(cur_photo, show_info = False, show_tutorial = False, show_about = False):
	screen.fill(BLACK)
	if cur_photo.bitmap is not None:
		screen.blit(cur_photo.bitmap, (0, 0))

	#debug drawing
	#pygame.draw.rect(screen, RED, NextRect)

	PADDING = 15
	DOUBLE_PADDING = PADDING * 2

	if show_info:
		if cur_photo.location_images is not None:
			if cur_photo.location_images.zoomed_in is not None:
				screen.blit(cur_photo.location_images.zoomed_in, (400, 0))

			if cur_photo.location_images.zoomed_out is not None:
				screen.blit(cur_photo.location_images.zoomed_out, (0, 0))

		if cur_photo.info.get('title'):
			# Display line wrapped text
			title_rect = Rect((PADDING,PADDING),(w-DOUBLE_PADDING,h/2))
			draw_text(screen, cur_photo.info['title'], BLACK, title_rect, basicFont, True)

		if cur_photo.info.get('date'):
			# Display single line text
			text = basicFont.render(cur_photo.info['date'], True, BLACK)
			text_rect = text.get_rect()
			screen.blit(text, [PADDING, h - text_rect.height - PADDING])
	elif show_tutorial:
		pygame.draw.rect(screen, WHITE, ScreenRect)
		pygame.draw.rect(screen, GREEN, TutorialRect)
		pygame.draw.rect(screen, ORANGE, AboutRect)
		pygame.draw.rect(screen, BLUE, BacklightRect)
		pygame.draw.rect(screen, RED, NextRect)

		draw_text_in_box(screen, "Show Tutorial", TutorialRect, basicFont)
		draw_text_in_box(screen, "Brightness", BacklightRect, basicFont)
		draw_text_in_box(screen, "Next Photo", NextRect, basicFont)
		draw_text_in_box(screen, "About", AboutRect, basicFont)

		draw_text_in_box(screen, "Photo Info", ScreenRect, largeFont)
	elif show_about:
		pygame.draw.rect(screen, WHITE, ScreenRect)

		basic_font_height = basicFont.size("Tg")[1]
		large_font_height = largeFont.size("Tg")[1]

		draw_text_simple("We Think Adventure.Rocks", [PADDING,PADDING], BLACK, largeFont, screen)
		draw_text_simple("www.wethinkadventure.rocks", [PADDING, PADDING + large_font_height + basic_font_height], BLACK, basicFont, screen)
		draw_text_simple("Created By:", [PADDING, PADDING + large_font_height + (basic_font_height * 3)], BLACK, basicFont, screen)
		draw_text_simple("    Adam & Stacy Brown", [PADDING, PADDING + large_font_height + (basic_font_height * 4)], BLACK, basicFont, screen)


	pygame.display.flip()


TutorialRect = Rect((0, 0), (280, 170))
BacklightRect = Rect((0, 310), (280, 170))
NextRect = Rect((520, 310), (280, 170))
AboutRect = Rect((520, 0), (280, 170))

ScreenRect = Rect((0, 0), (800, 480))

def check_hit(check_pos, rect):
	return rect.collidepoint(check_pos)

def get_google_maps_large_view_url( location ):
	base_url = "http://maps.googleapis.com/maps/api/staticmap?center={1}&zoom=6&scale=1&size=400x480&maptype=terrain&key={0}&format=png&visual_refresh=true&markers=size:mid%7Ccolor:0xff0000%7Clabel:%7C{1}"
	return base_url.format(GOOGLE_MAPS_API_KEY, location)

def get_google_maps_small_view_url( location ):
	base_url = "http://maps.googleapis.com/maps/api/staticmap?center={1}&zoom=15&scale=1&size=400x480&maptype=terrain&key={0}&format=png&visual_refresh=true&markers=size:mid%7Ccolor:0xff0000%7Clabel:%7C{1}"
	return base_url.format(GOOGLE_MAPS_API_KEY, location)


class MapImages:
	def __init__(self):
		pass

	zoomed_in = None
	zoomed_out = None


class PhotoInfo:
	def __init__(self):
		pass

	file_name = None
	info = None
	bitmap = None

	location_images = None


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

def get_file_contents(file_path):
		contents = None
		with open(file_path, 'r') as file:
			contents = file.read()
		return contents

def get_next_brightness( cur_brightness ):
	BRIGHTNESS_INCREMENT = 64

	if cur_brightness >= 255:
		new_brightness = 0
	else:
		new_brightness = cur_brightness + BRIGHTNESS_INCREMENT
		if new_brightness > 255:
			new_brightness = 255

	return new_brightness

# START EXECUTION
log('==========================')
log('Starting Adventure.Rocks!')
log('==========================')

log('starting display')

PHOTO_FRAME_ID = get_file_contents( '/app/config/PHOTO_FRAME_ID' )
if PHOTO_FRAME_ID is None:
	log('WARNING: PhotoFrame ID is missing!')

GOOGLE_MAPS_API_KEY = get_file_contents( '/app/config/GOOGLE_MAPS_API_KEY' )
if GOOGLE_MAPS_API_KEY is None:
	log('WARNING: Google Maps API Key is missing!')

# set up some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 128, 0)

w = 800
h = 480

displaying_info = False

pygame.init()
screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
screen.fill(BLACK)
pygame.mouse.set_visible(0)
pygame.display.set_caption('Adventure.Rocks')

basicFont = pygame.font.SysFont(None, 48)
largeFont = pygame.font.SysFont(None, 64)

show_loading()

photo = get_photo( PHOTO_FRAME_ID )

intervalSeconds = 5 * 60

timer = Timer()
timer.start(intervalSeconds)

displaying_tutorial = False
displaying_about = False

current_brightness = 255

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
			pos = pygame.mouse.get_pos()

			dismissing_tutorial = False
			if displaying_tutorial:
				log('Hiding tutorial')
				displaying_tutorial = False
				dismissing_tutorial = True

			log('x:' + str(pos[0]) + ' y:' + str(pos[1]))
			if displaying_info:
				log('Hiding image details')
				displaying_info = False
			elif displaying_about:
				log('Hiding about')
				displaying_about = False
			else:
				# Detect click for Next Photo
				if check_hit(pos, NextRect):
					log('User wants a new image')
					show_loading()
					photo = get_photo( PHOTO_FRAME_ID )
					timer.start(intervalSeconds)
				elif check_hit(pos, TutorialRect):
					if not dismissing_tutorial:
						log('User wants tutorial')
						displaying_tutorial = True
				elif check_hit(pos, BacklightRect):
					log('User wants to change brightness')
					current_brightness = get_next_brightness(current_brightness)
					log('New Brightness: ' + str(current_brightness))
					call(["/app/backlight.sh", str(current_brightness)])
				elif check_hit(pos, AboutRect):
					log('User wants to view About')
					displaying_about = True
				else:
					log('User wants image details')
					# If we don't have images loaded and we DO have a location, download them
					if photo.location_images is None and photo.info['location']:
						show_loading()
						download_map_images(photo)
					displaying_info = True


	if timer.timer_is_up():
		displaying_info = False
		log('Rotating to new image')
		show_loading()
		photo = get_photo( PHOTO_FRAME_ID )
		timer.start(intervalSeconds)
		log('Rotation complete.')

	render(photo, displaying_info, displaying_tutorial, displaying_about)

pygame.display.quit()

log('done.')
