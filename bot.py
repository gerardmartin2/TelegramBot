import random
import igo
import osmnx as ox
import time
import os

from staticmap import StaticMap, CircleMarker

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Required parameters
PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 800
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

init_time = -1
users = {}  # Map with user's Telegram ID and its position.
graph = None
highways = {}
igraph = None
congestions = []

def start(update, context):
    """Welcome the user and provide a link to /help command."""

    name = update.effective_chat.first_name
    emo = "👋"
    message = """Hello, %s! %s
    \n\nI'm the GuideBot and I'm going to help you get to your destination
    \n\nUse /help to know all available commands""" % (name, emo)
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, text=message)
    users[chat_id] = []


def help(update, context):
    """Give information about the available commands as well as linking
     to them."""

    emo = "👉"
    message = """%s /start : Start a conversation with GuideBot
              \n%s /help : Available commands
              \n%s /author : Information about who has implemented the bot
              \n%s /where : User's current location
              \n%s /pos : Fix a fake location. Indicate the place name or its coordinates.
              \n%s /go : Picture with the best route from user's location to the chosen destination. Indicate the name of the destination.
              """ % (emo, emo, emo, emo, emo, emo)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def author(update, context):
    """Provide information about the authors of the bot."""

    message = "This bot has been implemented by Adrià Diéguez Moscardó and Gerard Martin Pey"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def coordinates(update, context):
    """Get user coordinates from Telegram's location and update the dictionary
    to store them."""

    users[update.effective_chat.id] = [update.message.location.latitude, update.message.location.longitude]


def where(update, context):
    """Plot a map with the current user location."""

    try:
        file = "%d.png" % random.randint(1000000, 9999999)
        # Creates the map
        map = StaticMap(840, 840)
        # Get latitude and longitude from the user
        lat = users[update.effective_chat.id][0]
        lon = users[update.effective_chat.id][1]
        # Mark user's location
        map.add_marker(CircleMarker((lon, lat), 'red', 14))
        picture = map.render()
        picture.save(file)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(file, 'rb'))
        os.remove(file)
    except Exception as e:
        print(e)
        context.bot.send_message(
          chat_id=update.effective_chat.id,
          text="ERROR. Ensure you share your location or use /pos to fix a position.")


def go(update, context):
    """Plot a map with the shortest path according to the itime concept from
    user's position to the chosen destination point."""

    global init_time, graph, highways, igraph, congestions
    # If the graph has not been created yet
    if graph is None:
        print("Starting the creation of the graph.")
        graph = igo.download_graph(PLACE)
        print("Graph created properly. Starting highways download.")
        highways = igo.download_highways(HIGHWAYS_URL)
        print("Highways downloaded properly. Starting congestions download.")
        # Set the time when congestions are downloaded
        init_time = time.time()
        print("Init time set to: ", init_time)
        congestions = igo.download_congestions(CONGESTIONS_URL)
        print("Congestions downloaded properly. Starting igraph creation.")
        igraph = igo.build_igraph(graph, highways, congestions)
        print("igraph properly created.")
    else:
        # Get the current time
        current_time = time.time()
        print("The current time is: ", current_time)
        # If the difference between the last congestions update time and
        # the current time is greater than 15, update the congestions
        time_delta = current_time - init_time
        time_delta = time_delta/60
        print("It have been ", time_delta, " minutes since the last update.")
        if time_delta >= 15:
            congestions = igo.download_congestions(CONGESTIONS_URL)
            print("Congestions downloaded properly. Starting igraph creation.")
            igraph = igo.build_igraph(graph, highways, congestions)
            print("igraph properly created.")
        else:
            print("Congestions are on date. ", time_delta, " have passed.")

    # Read the destination
    destination = update.message.text[4:]
    try:
        # If latitud and longitud are set
        lat, lon = users[update.effective_chat.id]
        print("Searching the shortest path.")
        # Find shortest path and plot it
        ipath = igo.get_shortest_path_with_itimes(igraph, lat, lon, destination)
        print("Shortest path found. Ploting it.")
        picture = igo.plot_path(igraph, ipath, SIZE)
        file = "%d.png" % random.randint(1000000, 9999999)
        picture.save(file)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(file, 'rb'))
        os.remove(file)
    except Exception as e:
        # If neither latitud or longitud are set
        print(e)
        context.bot.send_message(
          chat_id=update.effective_chat.id,
          text="ERROR. Ensure you share your location or use /pos to fix a position.")


def pos(update, context):
    """Set a false user's location to the given place. False position can
    be set with coordinates or with its name. """

    location = update.message.text[4:]
    try:
        # If location's coordinates are given
        cc = []
        # Separate them
        for coordinate in location.split():
            l.append(float(coordinate))
        lat_pos, lon_pos = cc[0], cc[1]
    except:
        # If location's name is given
        location = location + ",Barcelona,Catalonia"
        lat_pos, lon_pos = ox.geocode(location)
    users[update.effective_chat.id] = [lat_pos, lon_pos]


# Access token from token.txt.
TOKEN = open('token.txt').read().strip()


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


# Indicates the relationship between the Telegram commands
# and the functions of bot.py
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('where', where))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('pos', pos))
dispatcher.add_handler(MessageHandler(Filters.location, coordinates))

# Start the bot.
updater.start_polling()
