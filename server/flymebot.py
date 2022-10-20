from botbuilder.core import TurnContext, ActivityHandler
from botbuilder.schema import ActivityTypes, ChannelAccount

class FlyMeBot(ActivityHandler):

    async def on_message_activity(self, turn_context: TurnContext):
        incoming_text = turn_context.activity.text
        await turn_context.send_activity(incoming_text)


    async def on_members_added_activity(self, member_added: ChannelAccount, turn_context: TurnContext):
        await turn_context.send_activity('Hello, welcome to FlyMeBot,\r\nWhere do you want to go?')