import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

#Define the dungeon map########################################
MAP_WIDTH = 80
MAP_HEIGHT = 45
#Rooms
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
#Colors
color_dark_wall = libtcod.Color(70,70,70)
color_dark_ground = libtcod.Color(120,120,120)

#Define classes################################################
class Tile:
	#a tile of the map
	def __init__(self,blocked,block_sight = None):
		self.blocked = blocked
		
		#by default, if a tile is blocked, it also blocks sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight

class Object:
	#this is a generic object: the player, a monster, an item, the stairs...
	#it's always represented by a character on screen.
	def __init__(self, x, y, char, color):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		
	def move(self, dx, dy):
		#move by given amount
		if not map[self.x + dx][self.y + dy].blocked:
			self.x += dx
			self.y += dy
		
	def draw(self):
		#set the color and then draw the character that represents this object at its position
		libtcod.console_set_default_foreground(con, self.color)
		libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
	
	def clear(self):
		#erase character
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

class Rect:
	#a rectangle on the map, used to characterize a room
	def __init__(self, x, y, w, h):
		#define rectangle by top left and bottom right points
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
		
	def center(self):
		center_x = (self.x1 + self.x2) / 2 #average of leftmost and rightmost
		center_y = (self.y1 + self.y2) / 2
		return (center_x, center_y)
		
	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)
		
#Define functions###############################################
def make_map():
	global map, player
	
	#fill map with "blocked" tiles
	map = [[ Tile(True)
		for y in range(MAP_HEIGHT) ]
			for x in range(MAP_WIDTH) ]
	
	#Make rooms
	rooms = []
	num_rooms = 0
	
	for r in range(MAX_ROOMS):
		#random width and height
		w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		#random position within map boundry
		x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
		y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
		
		#make rectangle rooms
		new_room = Rect(x, y, w, h)
		
		#check if any rooms intersect with this one
		failed = False
		for other_room in rooms:
			if new_room.intersect(other_room):
				failed = True
				break
	
		if not failed:
			#this means no intersections. room is valid
			
			#paint it to the map tiles
			create_room(new_room)
			
			#get center coordinates
			(new_x, new_y) = new_room.center()
			
			if num_rooms == 0:
				#if this is the first room put the player there
				player.x = new_x
				player.y = new_y
				
			else:
				#all rooms after the first.
				#connect to previous with tunnel.
				
				#center coordinates of previous
				(prev_x, prev_y) = rooms[num_rooms - 1].center()
				
				#flip a coin (random number 0 or 1)
				if libtcod.random_get_int(0, 0, 1) == 1:
					#first horizontal then vertical
					create_h_tunnel(prev_x, new_x, prev_y)
					create_v_tunnel(prev_y, new_y, prev_x)
				else:
					#vertical then horizontal
					create_v_tunnel(prev_y, new_y, prev_x)
					create_h_tunnel(prev_x, new_x, prev_y)
				
			#add new room to list
			rooms.append(new_room)
			num_rooms += 1
	#make npc
	npc.x = player.x
	npc.y = player.y - 5
	
def create_room(room):
	global map
	#dig out the room from the rectangle, leave 1 block for walls
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			#go through the tiles in a rectangle and make them passable
			map[x][y].blocked = False
			map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):#horizontal tunnel
	global map
	
	for x in range(min(x1, x2), max(x1, x2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
	global map
	#vertical tunnel
	for y in range(min(y1, y2), max(y1, y2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False
		
def render_all():
	global color_dark_wall, color_light_wall
	global color_dark_ground, color_light_ground
	
	
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			wall = map[x][y].block_sight
			if wall:
				libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET )
			else:
				libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET )
				
	#draw all objects in list
	for object in objects:
		object.draw()
	
	#blit the contents of the new console the root console...whatever that means
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)			
			
def handle_keys():
	global playerX, playerY
	
	#fullscreen and exit keys
	key = libtcod.console_wait_for_keypress(True)
	
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		return True #exit game
		
	#movement keys
	if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		player.move(0, -1)
	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
		player.move(0, 1)
	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
		player.move(-1, 0)
	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
		player.move(1, 0)

#set up fonts
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
#initialize window (size, title, fulscreen)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
#make another console so not messing with root all the time
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

#create object representing the player
player = Object(0, 0, '@', libtcod.white)#position doesn't matter. It will be set in make_map()
#create an NPC
npc = Object(0, 0, '@', libtcod.yellow)
#create list of objects
objects = [npc, player]

#make the map			
make_map()
#now the main loop
while not libtcod.console_is_window_closed():
	
	#draw all objects
	render_all()
	
	#At the end of the main loop you'll always need to present the changes to the screen. 
	libtcod.console_flush()
	
	#erase object old location
	for object in objects:
		object.clear()
	
	#handle keys and exit if needed
	exit = handle_keys()
	if exit:
		break
	