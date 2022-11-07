from flask import Flask, request, Response, render_template
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

conversation_id = 0
history = []


@app.route('/test', methods=['GET'])
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


@app.route('/new-conversation', methods=['GET'])
def new_conversation():
    global conversation_id

    # Create a new id for this conversation
    conversation_id += 1 
    
    # Prepare the history object
    history.append({
        'understood': True,
        'messages': []
    })

    return {'conv_id': conversation_id - 1}


@app.route('/new-message', methods=['GET'])
def new_message():
    conv_id = int(request.args.get('conversation_id'))
    text = request.args.get('text')
    writer = request.args.get('writer')
    understood = request.args.get('understood')
    if understood == 'False': history[conv_id]['understood'] = False
    history[conv_id]['messages'].append({'conv_id': conv_id, 'text': text, 'writer': writer})
    return ''


@app.route('/history', methods=['GET'])
def history_fct():
    return render_template('history.html', conversations=history)


@app.route('/conv-detail', methods=['GET'])
def conv_detail():
    conv_id = int(request.args.get('conversation_id'))
    return render_template('conv_detail.html', conversation=history[conv_id])


if __name__ == '__main__':
    app.run('localhost', 5000)