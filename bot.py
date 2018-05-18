import discord
import asyncio
import config
import urllib.request
import pathlib
import os
import re
from glob import glob

###########################
# config.py file\t\t  #
###########################
print("Loading configuration...")

token = config.token
app_id = config.app_id

# create a new discord client
print("Loading client...")
client = discord.Client()

# parse input function
def parseinput(s):
	args = splitmessage(s)
	# remove the first
	# the last element is the url
	url = args[len(args)-1]
	# the first is the username
	user = args[1].lower()
	# the rest is the image title
	title = '_'.join(args[2:len(args)-1]).lower()
	# remove unwanted characters
	pattern = re.compile('\W')
	user = re.sub(pattern, '', user)
	title = re.sub(pattern, '', title)
	return[user, title, url]

# function to split strings into lists of single words
def splitmessage(s):
	words = []
	inword = 0
	for c in s:
		if c in " \r\n\t": #whitepsace
			inword = 0
		elif not inword:
			words = words + [c]
			inword = 1
		else:
			words[-1] = words[-1] + c
	return words

def downloader(args):
	user_folder = args[0]
	file_name = args[1]
	image_url = args[2]
	print(image_url)
	if not image_url.startswith(('http://', 'https://')):
		print('Invalid URL')
		return('Invalid URL')
	maintype = ''
	subtype = ''
	ensure_dir(user_folder)
	opener=urllib.request.build_opener()
	opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
	urllib.request.install_opener(opener)
	# we should check for valid url before running this
	with urllib.request.urlopen(image_url) as response:
		info = response.info()
		maintype = info.get_content_type()  # -> text
		subtype = info.get_content_subtype()  # -> html)
	if maintype not in ('image/png', 'image/jpeg', 'image/gif'):
		print("Invalid file type!")
		return("Invalid file type!")
	else:
		fullfilename = os.path.join("./data/" + user_folder, file_name + "." + subtype)
		urllib.request.urlretrieve(image_url,fullfilename)
		return("Success")


def ensure_dir(file_path):
	safe_name = './' + file_path.replace('/', '_')
	pathlib.Path('./data/' + safe_name).mkdir(exist_ok=True) 

# runs when the client first connects
@client.event
async def on_ready():
	# print info to terminal
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	print('Connected servers:')
	for server in client.servers:
		print(server.name)
	print('------')

# runs when a message is recieved
@client.event
async def on_message(message):
	if message.content.startswith('!greet'):
		await client.send_message(message.channel, "Greetings! I work")
	if message.content.startswith('!add'):
		args = parseinput(message.content)
		print(args)
		# current version of downloader assumes the file name is only 1 word
		# should convert to lowercase and remove spaces, etc
		result = downloader(args)
		if result == "Success":
                        await client.send_message(message.channel, "Added " + args[2].replace('_', ' ') + " for user **" + args[1] + "**")
		else:
			await client.send_message(message.channel, result)
	elif message.content.startswith('!help'):
		await client.send_message(message.channel, "This command isn't finished yet")
	elif message.content.startswith('!search'):
		# check the rest of the message for correct formatting
		# check that the user folder exists
		# check that the file exists
		# else, spit out error messages
		await client.send_message(message.channel, "This command isn't finished yet")
	elif message.content.startswith('!delete'):
		args = splitmessage(message.content)
		for name in os.listdir('./data/' + args[1].lower()):
			if '_'.join(args[2:len(args)-1]).replace(' ', '_').lower() in name:
				print("./data/" + args[1].lower() + "/" + name)
				os.remove("./data/" + args[1].lower() + "/" + name)
 
	elif message.content.startswith('!show'):
		args = splitmessage(message.content)
		if len(args)==1:
			# check if there are any users added, if not then tell to use !add
			if len(glob("./data/*/")) == 0:
				await client.send_message(message.channel, "There are currently no saved images.\r\nPlease use the !add command")
			else:
				embed = discord.Embed(title="**__Saved Images__**")
				for item in glob("./data/*/"):
					print(os.path.basename(item[:-1]))
					titles = ""
					for title in glob(item + "/*"): titles = titles + os.path.basename(title) + "\r\n"
					if titles == "":
						titles = "empty"
					embed.add_field(name=os.path.basename(item[:-1]), value=titles, inline=True)
				await client.send_message(message.channel, embed=embed)
		# for now, assume that it'll be !show username
		if len(args)==2:
			if len(glob("./data/" + args[1].lower() + "/*")) == 0:
				await client.send_message(message.channel, "This user currently has no images added.\r\nPlease use the !add command")
			else:
				titles = ""
				for title in glob("./data/" + args[1] + "/*"):
					titles = titles + "\r\n" + os.path.basename(title).split('.', 1)[0].replace('_', ' ') + ","
				if not len(titles) == 0:
					titles = titles[:-1]
				embed = discord.Embed(title="**__" + args[1].capitalize() + "'s Images__**", description=titles)
				await client.send_message(message.channel, embed=embed)
		# make sure user folder and file exist, then send
		if len(args)>=3:
			searchName = args[2:len(args)-1]
			for name in os.listdir('./data/' + args[1].lower()):
				if args[2].replace(' ', '_').lower() in name:
					await client.send_file(message.channel, "./data/" + args[1] + "/" + name)
		# if just !show (no extra arguments) print an overview
		# this needs to work with multiple filetypes (png, jpeg, jpg, etc)
		# also, spaces, underscores, capitalization, etc



# start the bot
client.run(token)
