from youtubesearchpython import VideosSearch, CustomSearch, PlaylistsSearch, PlaylistsSearch, Playlist
from utiles import time_formatting



class PlaylistResult:
	def __init__(self, url):
		self.url = url
		self.playlist = Playlist(url)
		self.videos = []
		self.count = 0
		self.parse()

	def parse(self):
		for vid in self.playlist.videos[self.count:]:
			video = {
				"title": vid["title"],
				"url": f"https://youtube.com/watch?v={vid['id']}",
				"duration": time_formatting(vid["duration"]),
				"channel": {
					"name": vid["channel"]["name"], 
					"url": f"https://www.youtube.com/channel/{vid['channel']['id']}"},

			}
			self.videos.append(video)
			self.count = len(self.videos)

	def next(self):
		if not self.playlist.hasMoreVideos:
			return
		self.playlist.getNextVideos()
		current = self.count
		self.parse()
		self.new_videos = self.count-current

		return True
	def get_new_titles(self):
		titles = self.get_display_titles()
		return titles[len(titles)-self.new_videos:len(titles)]

	def get_title(self, n):
		return self.videos[n]["title"]
	def get_display_titles(self):
		titles = []
		for vid in self.videos:
			title = [vid['title'], _("المدة: {}").format(vid['duration']), f"{_('بواسطة')} {vid['channel']['name']}"]
			titles.append(", ".join(title))
		return titles
	def get_url(self, n):
		return self.videos[n]["url"]





class Search:
	def __init__(self, query, filter=0):
		self.query = query
		self.filter = filter
		self.results = {}
		self.count = 1
		filters = {
			1: "EgJAAQ",
			2: "CAISAhAB",
			3: "CAMSAhAB", 
			4: "EgIQA"
		}
		if self.filter == 0:
			self.search = VideosSearch(self.query)
		elif self.filter == 4:
				self.search = PlaylistsSearch(self.query)
		else:
			self.search = CustomSearch(self.query, filters[self.filter])
		self.parse_results()

	def parse_results(self):
		results = self.search.result()["result"]
		for result in results:
			self.results[self.count] = {
				"type": result["type"],
				"title": result["title"],
				"url": result["link"], 
				"duration": result.get("duration"),
				"elements": result.get("videoCount"),
				"channel": {
					"name": result["channel"]["name"], 
					"url": f"https://www.youtube.com/channel/{result['channel']['id']}"}
			}
			if result["type"] == "video":
				self.results[self.count]["views"] = self.parse_views(result["viewCount"]["text"])
			else:
				self.results[self.count]["views"] = None
			self.count += 1
	def get_titles(self):
		titles = []
		for result, data  in self.results.items():
			title = [data['title']]
			if data["type"] == "video":
				title += [self.get_duration(data['duration']),
					f"{_('بواسطة')} {data['channel']['name']}",
					self.views_part(data['views'])]
			elif data["type"] == "playlist":
				title += [_("قائمة تشغيل"),
			f"{_('بواسطة')} {data['channel']['name']}", 
					_("تحتوي على {} من الفيديوهات").format(data["elements"])]
			titles.append(", ".join([element for element in title if element != ""]))
		return titles

	def get_last_titles(self):
		titles = self.get_titles()
		return titles[len(titles)-self.new_videos:len(titles)]
	def get_title(self, number):
		return self.results[number+1]["title"]
	def get_url(self, number):
		return self.results[number+1]["url"]
	def get_type(self, number):
		return self.results[number+1]["type"]
	def get_channel(self, number):
		return self.results[number+1]["channel"]

	def load_more(self):
		try:
			self.search.next()
		except:
			return
		current = self.count
		self.parse_results()
		self.new_videos = self.count-current
		return True
	def parse_views(self, string):
		try:
			string = string.replace(",", "")
		except AttributeError:
			return
		return string.replace("views", "")
	def get_views(self, number):

		return self.results[number+1]['views']
	def views_part(self, data):
		if data is not None:
			return _("عدد المشاهدات {}").format(data)
		else:
			return _("بث مباشر")

	def get_duration(self, data): # get the duration of the video
		if data is not None:
			return _("المدة: {}").format(time_formatting(data))
		else:
			return ""