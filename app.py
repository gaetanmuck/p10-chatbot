from flask import Flask, request, Response
from botbuilder.schema import Activity
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, ConversationState, UserState, MemoryStorage
from model.flymebot import FlyMeBot
import asyncio

botadaptersettings = BotFrameworkAdapterSettings('', '') 
botadapter =BotFrameworkAdapter(botadaptersettings)

mem_storage = MemoryStorage()
conv_state = ConversationState(mem_storage)
user_state = UserState(mem_storage)


app = Flask(__name__)
loop = asyncio.get_event_loop()
flymebot = FlyMeBot(conv_state, user_state)

@app.route('/test', methots=['GET'])
def test():
    return 'Hello world!'

@app.route('/api/messages', methods=['POST'])
def api_messages():

    # Checkings
    if not 'application/json' in request.headers['content-type']: return Response(status=415)

    # Processing
    jsonmessage = request.json # Parse message
    activity = Activity().deserialize(jsonmessage) # Transforom into an activity
    task = loop.create_task(botadapter.process_activity(activity, '', flymebot.on_turn)) # Process the activity (call the bot)
    loop.run_until_complete(task) # Wait for the task

    return ''



if __name__ == '__main__':
    app.run('localhost', 5000)