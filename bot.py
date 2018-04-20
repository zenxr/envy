import discord
import asyncio
import config
import urllib.request
import pathlib
import os

###########################
# config.py file\t\t  #
###########################
print("Loading configuration...")

token = config.token
app_id = config.app_id

# create a new discord client
print("Loading client...")
client = discord.Client()

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

def downloader(user_folder, file_name, image_url):
	maintype = ''
	subtype = ''
	ensure_dir(user_folder)
	with urllib.request.urlopen(image_url) as response:
		info = response.info()
		maintype = info.get_content_type()  # -> text
		subtype = info.get_content_subtype()  # -> html
	if maintype not in ('image/png', 'image/jpeg', 'image/gif'):
		print("Invalid file type!")
		return("Invalid file type!")
	else:
		fullfilename = os.path.join(user_folder, file_name + "." + subtype)
		urllib.request.urlretrieve(image_url,fullfilename)

def ensure_dir(file_path):
	safe_name = './' + file_path.replace('/', '_')
	pathlib.Path('./' + safe_name).mkdir(exist_ok=True) 

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
		args = splitmessage(message.content)
		downloader(args[1], args[2], args[3])


# start the bot
client.run(token)