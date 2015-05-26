#! /usr/bin/env python2

import os, sys, requests, pygame
from gps import *
from pygame.locals import *

class WeatherClient:
	apikey = "7232a1f6857090f33b9d1c7a74721"

	@staticmethod
	def latlon():
		gpsd = gps(mode = WATCH_ENABLE)

		try:
			while True:
				report = gpsd.next()
				if report['class'] == 'TPV':
					gpsd.close()
					return report['lat'], report['lon']

		except:
			return None, None

	@staticmethod
	def usefuldata(j):
		d = j['data']['current_condition'][0]
		out = "Now - Temp: {0}C, Feels like: {1}C, Description: {2}\n"\
					.format(d['temp_C'],
									d['FeelsLikeC'],
									d['weatherDesc'][0]['value'])

		hourly = j['data']['weather'][0]['hourly']
		hour_count = 1

		for h in hourly:
			out += ("+{0}hr - Temp: {1}C, Feels like: {1}C, Chance of Rain:"
							" {3}%, Description: {4}\n")\
							.format(hour_count,
											h['tempC'],
											h['FeelsLikeC'],
											h['chanceofrain'],
											h['weatherDesc'][0]['value'])

			hour_count += 1

			return out.rstrip()

		@staticmethod
		def update():
			errstr = "Error getting weather data"

			lat, lon = WeatherClient.latlon()

			if lat == None or lon == None:
				return errstr

			api_req = ("http://api.worldweatheronline.com/free/v2/weather.ashx"
			"?q={0}%2C{1}&format=json&key={2}").format(lat, lon, WeatherClient.apikey)
			r = None

			try:
				r = requests.get(api_req)
			except requests.exceptions.RequestExceptions as e:
				return errstr

			return WeatherClient.usefuldata(r.json())

class CarLauncher:
	def __init__(self):
		pygame.init()
		pygame.mixer.quit()

		screen_info = pygame.display.Info()
		self.screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h))

		pygame.display.set_caption('Car Launcher')

		self.titlefont = pygame.font.Font(None, 100)
		self.wfont = pygame.font.Font(None, 30)
		self.w_text = None # Weather text

	def clean_background(self):
		background = pygame.Surface(self.screen.get_size())
		self.backgorund = background.convert()
		self.background.fill((0, 0, 0))

		# Render title centered
		text = self.titlefont.render("CarPi Launcher", 1, (255, 255, 255))
		textpos = text.get_rect()
		textpos.centerx = self.background.get_rect().centerx

		self.background.blit(text, textpost)
		self.screen.blit(self.background, (0,0))

		pygame.display.flip()

	def main_menu(self):
		self.btns = {'Music': None, 'Nav': None, 'Weather': None}

		item_num = 1

		for key in self.btns:
			text = self.titlefont.render(key, , 1, (255, 255, 255))
			textpos = text.get_rect()
			max_width = self.background.get_rect().width / len(self.btns)
			center_offset =  max_width * 0.5

			textpos.centery = self.background.get_rect().centery / 2
			textpost.centerx = (max_width * item_num) - center_offset

			self.btns[key] = textpos
			self.screen.blit(text, textpos)

			item_num += 1

		pygame.display.flip()

	def select_rect(self, rect, text):
		surface = pygame.Surface((rect.w, rect.h))
		surface.fill((0, 255, 0))

		t = self.titlefont.render(text, 1 , (255, 255, 255))
		surface.blit(t, (0,0))
		self.screen.blit(surface, rect)

		pygame.display.flip()

	def reset(self):
		self.clean_background()
		self.main_menu()
#		self.render_weather()

	def execute(self, path):
		os.system(path)
		self.reset()

	def render_weather(self):
		if self.w_text == None
			return

		margin = 10
		y = self.btns['Nav'].bottomleft[1] + margin

		for t in self.w_text.split("\n"):
			line = self.wfont.render(t.rstrip(), 1, (255, 255, 255))
			line_rect = line.get_rect()
			line_rect.centerx = self.background.get_rect().centerx
			line.rect.y = y
			self.screen.blit(line, line_rect)
			y += margin + line_rect.height

		pygame.display.flip()

	def handle_events(self, events):
		for e in events:
			if e.type == QUIT:
				sys.exit()
			elif e.type == MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()

				for btn_text, rect in self.btns.iteritems():
					if rect.collidepoint(pos):
						self.select_rect(rect, btn_text)

						if btn_text == 'Nav':
							self.execute("/usr/bin/navit")
						elif btn_text == "Music":
							self.execute("/usr/local/bin/pympdtouchgui")
						elif btn_text == "Weather":
							self.w_text = WeatherClient.update()

							self.reset()

	def loop(self):
		clock = pygame.time.Clock()
		self.reset()

		while 1:
			self.handle_events(pygame.event.get())
			clock.tick(5)

if __name__ == "__main__":
	cl = CarLauncher()
	cl.loop()

