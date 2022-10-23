from botbuilder.core import TurnContext, ActivityHandler, ConversationState, UserState
from botbuilder.schema import ActivityTypes, ChannelAccount
from dotenv import load_dotenv; load_dotenv()
from clu import ask_clu
from data_model import ConvState, UserModel


class FlyMeBot(ActivityHandler):
    
    def __init__(self, conv_state: ConversationState, user_state: UserState):
        self.conv_state = conv_state
        self.user_state = user_state

        self.conv_prop = self.conv_state.create_property("conv_state")
        self.user_prop = self.user_state.create_property("user_state")


    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        await self.conv_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)


    async def on_members_added_activity(self, member_added: ChannelAccount, turn_context: TurnContext):
        await turn_context.send_activity('Hello, welcome to FlyMeBot,\r\nI am a here to understand where and when do you want to book a flight.')
        await turn_context.send_activity('First, start with telling me what is your destination?')


    async def on_message_activity(self, turn_context: TurnContext):
        incoming_text = turn_context.activity.text

        conv_state = await self.conv_prop.get(turn_context, ConvState)
        user_infos = await self.user_prop.get(turn_context, UserModel)

        if conv_state.step == 'destination':
            found_entities = ask_clu(incoming_text)
            user_infos.destination = self.find_key_in_entities(found_entities, 'destination')
            await turn_context.send_activity('Ok, now tell me from where do you want to go there?')
            conv_state.step = 'origin'

        elif conv_state.step == 'origin':
            found_entities = ask_clu(incoming_text)
            user_infos.origin = self.find_key_in_entities(found_entities, 'origin')
            await turn_context.send_activity('Very nice, when do you want to go?')
            conv_state.step = 'go_date'

        elif conv_state.step == 'go_date':
            found_entities = ask_clu(incoming_text)
            user_infos.go_date = self.find_key_in_entities(found_entities, 'go_date')
            await turn_context.send_activity('And when do you want to come back?')
            conv_state.step = 'back_date'

        elif conv_state.step == 'back_date':
            found_entities = ask_clu(incoming_text)
            user_infos.back_date = self.find_key_in_entities(found_entities, 'back_date')
            await turn_context.send_activity('And last but not least, what is your budget?')
            conv_state.step = 'budget'

        elif conv_state.step == 'budget':
            found_entities = ask_clu(incoming_text)
            user_infos.budget = self.find_key_in_entities(found_entities, 'budget')

            await self.sum_up(turn_context, user_infos)
            conv_state.step = 'sum-up-confirm'

        elif conv_state.step == 'sum-up-confirm':
            if incoming_text in ['yes', 'y', 'yeah', 'yea', 'yep', 'ok', 'okey', 'okay', 'affirmative', 'amen', 'good', 'true', 'sure', 'aye']:
                str = "All right, I will look for that, and send you an offer that most correspond to your wishes, directly in your email!"
                str += "\r\nI hope the conversation went smoothly enough to satisfy you."
                str += "\r\nThank you very much for using FlyMeBot to look for your flight."
                await turn_context.send_activity(str)
                await turn_context.send_activity('-- you may now close the conversation --')
                conv_state.step = 'finished'

            elif incoming_text in ['no', 'n', 'nope', 'not', 'wrong', 'not really']:
                await turn_context.send_activity("Ok, let's correct the information!\r\nDo you want to change the 'destination', 'origin', 'go date', 'back date' or 'budget'?")
                conv_state.step = 'choose-correction'

            else: 
                await turn_context.send_activity('Mmh, I did not get if that was a yes or a no?')

        elif conv_state.step == 'choose-correction':
            if incoming_text.lower() in ['destination', 'origin', 'go date', 'back date', 'budget']:
                await turn_context.send_activity("Ok, what is the correct " + incoming_text + "?")
                conv_state.step = 'correction-' + incoming_text
            else: 
                await turn_context.send_activity("I am sorry, I did not understand what you said.\r\nDo you want to change the 'destination', the 'origin', the 'go date', 'back date' or the 'budget'?")

        elif conv_state.step == 'correction-destination':
            found_entities = ask_clu(incoming_text)
            user_infos.destination = self.find_key_in_entities(found_entities, 'destination')
            await self.sum_up(turn_context, user_infos)
            conv_state.step = 'sum-up-confirm'

        elif conv_state.step == 'correction-origin':
            found_entities = ask_clu(incoming_text)
            user_infos.origin = self.find_key_in_entities(found_entities, 'origin')
            await self.sum_up(turn_context, user_infos)
            conv_state.step = 'sum-up-confirm'

        elif conv_state.step == 'correction-go date':
            found_entities = ask_clu(incoming_text)
            user_infos.go_date = self.find_key_in_entities(found_entities, 'go_date')
            await self.sum_up(turn_context, user_infos)
            conv_state.step = 'sum-up-confirm'

        elif conv_state.step == 'correction-back date':
            found_entities = ask_clu(incoming_text)
            user_infos.back_date = self.find_key_in_entities(found_entities, 'back_date')
            await self.sum_up(turn_context, user_infos)
            conv_state.step = 'sum-up-confirm'

        elif conv_state.step == 'correction-budget':
            found_entities = ask_clu(incoming_text)
            user_infos.budget = self.find_key_in_entities(found_entities, 'budget')
            await self.sum_up(turn_context, user_infos)
            conv_state.step = 'sum-up-confirm'

        elif conv_state.step == 'finished':
            await turn_context.send_activity('So you want do look for another flight, let\'s go!\r\nAgain, start with telling me what your destination is?')
            conv_state.step = 'destination'



        else: 
            await turn_context.send_activity('é_è \r\nI am sorry I had a malfunction...\r\nWe need to restart the conversation...')
            # Restart conv





    def find_key_in_entities(self, entities, key):
        print('===========================')
        print(entities)
        print(key)
        print('===========================')
        for ent in entities:
            if ent['key'] == key: 
                return ent['value']
        return ''

    async def sum_up(self, turn_context, user_infos):
        str = "So, if I understood correctly, you are looking for the following flight \r\n"
        str += "  - <" + user_infos.origin + "> => <" + user_infos.destination + ">\r\n"
        str += "  - From <" + user_infos.go_date + "> to <" + user_infos.back_date + ">\r\n"
        str += "  - With a budget of <" + user_infos.budget + ">\r\n"
        str += "\r\nIs that all correct?"
        await turn_context.send_activity(str)



