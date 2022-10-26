from botbuilder.core import TurnContext, ActivityHandler, ConversationState, UserState
from botbuilder.schema import ActivityTypes, ChannelAccount
from dotenv import load_dotenv; load_dotenv()
from clu import ask_clu
from data_model import ConvState, UserModel


class FlyMeBot(ActivityHandler):
    
    def __init__(self, conv_state: ConversationState, user_state: UserState):
        """Initialize Bot with 'global' variables"""

        self.conv_state = conv_state
        self.user_state = user_state

        self.conv_prop = self.conv_state.create_property("conv_state")
        self.user_prop = self.user_state.create_property("user_state")



    async def on_turn(self, turn_context: TurnContext):
        """Way to store the state from a turn to another."""

        await super().on_turn(turn_context)

        await self.conv_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)



    async def on_members_added_activity(self, member_added: ChannelAccount, turn_context: TurnContext):
        """Begining of conversation"""
        await self.start_conv(turn_context)



    async def on_message_activity(self, turn_context: TurnContext):
        """Message handling"""

        incoming_text = turn_context.activity.text

        conv_state = await self.conv_prop.get(turn_context, ConvState)
        user_infos = await self.user_prop.get(turn_context, UserModel)


        # The user should had given the DESTINATION:
        if conv_state.step == 'destination':

            # Parse response and save it
            found_entities = ask_clu(incoming_text)
            user_infos.destination = self.find_key_in_entities(found_entities, 'destination')

            # Advance in the conversation: ask about the origin:
            await turn_context.send_activity('Ok, now tell me from where do you want to go there?')
            conv_state.step = 'origin'


        # The user should had given the ORIGIN:
        elif conv_state.step == 'origin':

            # Parse response and save it
            found_entities = ask_clu(incoming_text)
            user_infos.origin = self.find_key_in_entities(found_entities, 'origin')

            # Advance in the conversation: ask about the go date:
            await turn_context.send_activity('Very nice, when do you want to go?')
            conv_state.step = 'go_date'


        # The user should had given the GO DATE:
        elif conv_state.step == 'go_date':

            # Parse response and save it
            found_entities = ask_clu(incoming_text)
            user_infos.go_date = self.find_key_in_entities(found_entities, 'go_date')

            # Advance in the conversation: ask about the back date:
            await turn_context.send_activity('And when do you want to come back?')
            conv_state.step = 'back_date'


        # The user should had given the BACK DATE:
        elif conv_state.step == 'back_date':

            # Parse response and save it
            found_entities = ask_clu(incoming_text)
            user_infos.back_date = self.find_key_in_entities(found_entities, 'back_date')

            # Advance in the conversation: ask about the back date:
            await turn_context.send_activity('And last but not least, what is your budget?')
            conv_state.step = 'budget'

        # The user should had given the BUDGET:
        elif conv_state.step == 'budget':

            # Parse response and save it
            found_entities = ask_clu(incoming_text)
            user_infos.budget = self.find_key_in_entities(found_entities, 'budget')

            # Finish the conversation, sum up and asks about understood conversation
            conv_state.step = await self.sum_up(turn_context, user_infos)


        # The user should have confirm (or not) the SUM UP:
        elif conv_state.step == 'sum-up-confirm':

            # If he answered YES (or alike):
            # Close the conversation
            if incoming_text in ['yes', 'y', 'yeah', 'yea', 'yep', 'ok', 'okey', 'okay', 'affirmative', 'amen', 'good', 'true', 'sure', 'aye']:
                str = "All right, I will look for that, and send you an offer that most correspond to your wishes, directly in your email!"
                str += "\r\nI hope the conversation went smoothly enough to satisfy you."
                str += "\r\nThank you very much for using FlyMeBot to look for your flight."
                await turn_context.send_activity(str)
                await turn_context.send_activity('-- you may now close the conversation --')
                conv_state.step = 'finished'

            # If he answered NO (or alike):
            # Change what information needs to be changed
            elif incoming_text in ['no', 'n', 'nope', 'not', 'wrong', 'not really']:
                await turn_context.send_activity("Ok, let's correct the information!\r\nDo you want to change the 'destination', 'origin', 'go date', 'back date' or 'budget'?")
                conv_state.step = 'choose-correction'
            
            # If he answered something the bot did not get (not registered as a yes or a no)
            else: await turn_context.send_activity('Mmh, I did not get if that was a yes or a no?')


        # The user should have said WHAT TO CHANGE:
        elif conv_state.step == 'choose-correction':

            # Here we make the user answer character rightly one of the answer.
            if incoming_text.lower() in ['destination', 'origin', 'go date', 'back date', 'budget']:
                # When errors has been detected, we ask for the new value:
                await turn_context.send_activity("Ok, what is the correct " + incoming_text + "?")
                # Since the spelling is mandatory right, we can use it in the conversation state:
                conv_state.step = 'correction-' + incoming_text

            # If it is not in the list of the five possibilities, we simply ask him again until it is.
            else: await turn_context.send_activity("I am sorry, I did not understand what you said.\r\nDo you want to change the 'destination', the 'origin', the 'go date', 'back date' or the 'budget'?")


        # Ask for the new DESTINATION, then sum up again and ask for confirmation
        elif conv_state.step == 'correction-destination':
            found_entities = ask_clu(incoming_text)
            user_infos.destination = self.find_key_in_entities(found_entities, 'destination')
            conv_state.step = await self.sum_up(turn_context, user_infos)

        # Ask for the new ORIGIN, then sum up again and ask for confirmation
        elif conv_state.step == 'correction-origin':
            found_entities = ask_clu(incoming_text)
            user_infos.origin = self.find_key_in_entities(found_entities, 'origin')
            conv_state.step = await self.sum_up(turn_context, user_infos)

        # Ask for the new GO DATE, then sum up again and ask for confirmation
        elif conv_state.step == 'correction-go date':
            found_entities = ask_clu(incoming_text)
            user_infos.go_date = self.find_key_in_entities(found_entities, 'go_date')
            conv_state.step = await self.sum_up(turn_context, user_infos)

        # Ask for the new BACK DATE, then sum up again and ask for confirmation
        elif conv_state.step == 'correction-back date':
            found_entities = ask_clu(incoming_text)
            user_infos.back_date = self.find_key_in_entities(found_entities, 'back_date')
            conv_state.step = await self.sum_up(turn_context, user_infos)

        # Ask for the new BUDGET, then sum up again and ask for confirmation
        elif conv_state.step == 'correction-budget':
            found_entities = ask_clu(incoming_text)
            user_infos.budget = self.find_key_in_entities(found_entities, 'budget')
            conv_state.step = await self.sum_up(turn_context, user_infos)

        # After the final message, if the user write again in the conversation, we restart from the begining
        elif conv_state.step == 'finished':
            await turn_context.send_activity('So you want do look for another flight, let\'s go!\r\nAgain, start with telling me what your destination is?')
            conv_state.step = 'destination'

        # This is an error case, it should never happen
        else: 
            await turn_context.send_activity('é_è \r\nI am sorry I had a malfunction...\r\nWe need to restart the conversation...')
            self.start_conv(turn_context)



    def find_key_in_entities(self, entities, key):
        """Parse the CLU response in order to find a particular key. If the key is not found, returns an empty string."""
        for ent in entities:
            if ent['key'] == key: 
                return ent['value']
        return ''



    async def sum_up(self, turn_context, user_infos):
        """Print out to the user all the information in memory of the Bot. Returns the next conversation step."""

        str = "So, if I understood correctly, you are looking for the following flight \r\n"
        str += "  - <" + user_infos.origin + "> => <" + user_infos.destination + ">\r\n"
        str += "  - From <" + user_infos.go_date + "> to <" + user_infos.back_date + ">\r\n"
        str += "  - With a budget of <" + user_infos.budget + ">\r\n"
        str += "\r\nIs that all correct?"
        await turn_context.send_activity(str)

        return 'sum-up-confirm'



    async def start_conv(self, turn_context: TurnContext):
        """Print out the welcoming messages."""

        await turn_context.send_activity('Hello, welcome to FlyMeBot,\r\nI am a here to understand where and when do you want to book a flight.')
        await turn_context.send_activity('First, start with telling me what is your destination?')

