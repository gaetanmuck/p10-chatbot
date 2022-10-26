from botbuilder.core import TurnContext, ActivityHandler, ConversationState, UserState
from botbuilder.schema import ActivityTypes, ChannelAccount
from dotenv import load_dotenv; load_dotenv()
from tools.clu import ask_clu
from model.usermodel import UserModel
from model.convstate import ConvState


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



    async def start_conv(self, turn_context: TurnContext):
        """Print out the welcoming messages."""

        await turn_context.send_activity('Hello, welcome to FlyMeBot,\r\nI am a here to understand where and when do you want to book a flight.')
        await turn_context.send_activity('Tell me informations about the flight you would like to book?')



    async def end_conv(self, turn_context: TurnContext):
        """Print out the ending messages."""

        answer = "All right, I will look for that, and send you an offer that most correspond to your wishes, directly in your email!"
        answer += "\r\nI hope the conversation went smoothly enough to satisfy you."
        answer += "\r\nThank you very much for using FlyMeBot to look for your flight."
        await turn_context.send_activity(answer)
        answer = '-- you may now close the conversation, or send another message about another flight --'
        await turn_context.send_activity(answer)


    async def look_for_missing(self, missing, turn_context: TurnContext):
        answer = 'I need additional information about your flight.\r\n'
        answer += 'Can you tell me more about the ' + missing.replace('_', ' ') + ' of your flight?'
        await turn_context.send_activity(answer)




    async def on_message_activity(self, turn_context: TurnContext):
        """Message handling"""

        incoming_text = turn_context.activity.text

        conv_state = await self.conv_prop.get(turn_context, ConvState)
        user_infos = await self.user_prop.get(turn_context, UserModel)


        # When the conversation just started or has been reset:
        if conv_state.step == 'init':
            found_entities = ask_clu(incoming_text)

            if len(found_entities) == 0:
                ######## Send error message to Insights: not related message ########
                answer = 'I found no information about a possible flight in your message, can you try again with different words?'
                await turn_context.send_activity(answer)
                conv_state.step = 'init' # We keep it at this step
            
            else:
                user_infos.parse_entities(found_entities, True)
                answer = user_infos.sum_up()
                await turn_context.send_activity(answer)
                conv_state.step = 'sum-up-confirm'


        # The user should have confirm (or not) the SUM UP:
        elif conv_state.step == 'sum-up-confirm':

            # If he answered YES (or alike):
            # Close the conversation
            if incoming_text in ['yes', 'y', 'yeah', 'yea', 'yep', 'ok', 'okey', 'okay', 'affirmative', 'amen', 'good', 'true', 'sure', 'aye']:
                ######## Send error message to Insights: good predictions ########
                missing = user_infos.get_missing()

                # The user provided every information needed: finish the conversation
                if missing == 'complete':
                    self.end_conv(turn_context)
                    conv_state.step = 'init'

                # There is some information missing:
                else:  
                    await turn_context.send_activity('Very good!')
                    await self.look_for_missing(missing, turn_context)
                    conv_state.step = 'look-for-missing'

            # If he answered NO (or alike):
            # Change what information needs to be changed
            elif incoming_text in ['no', 'n', 'nope', 'not', 'wrong', 'not really']:
                ######## Send error message to Insights: bad predictions ########
                answer = 'That is sad...\r\n'
                answer += 'What is wrong? The "destination", "origin", "go date", "back date" or "budget"?'
                await turn_context.send_activity(answer)
                conv_state.step = 'choose-correction'
            
            # If he answered something the bot did not get (not registered as a yes or a no)
            else: await turn_context.send_activity('Mmh, was that a yes or a no?')


        # The question about a specific information has been asked to the user, parse the user answer
        elif conv_state.step == 'look-for-missing':
            found_entities = ask_clu(incoming_text)
            missing = user_infos.get_missing() # To get the asked key
            found = user_infos.parse_entities_specific(found_entities, missing)

            if found:
                missing = user_infos.get_missing() # To see if there is still missing information:
                if missing == 'complete':
                    answer = user_infos.sum_up()
                    await turn_context.send_activity(answer)
                    conv_state.step = 'sum-up-confirm'
                else:  
                    await self.look_for_missing(missing, turn_context)
                    conv_state.step = 'look-for-missing'
            else:
                answer = 'Uh, that is not a valid value for a ' + missing.replace('_', ' ') + '\r\n'
                answer += 'Can you be more specific?'
                await turn_context.send_activity(answer)



        # First step of the correction, the property:
        elif conv_state.step == 'choose-correction':
            incoming_text = incoming_text.replace('the ', '')

            # If the user did say a righteous property name
            if incoming_text in ['destination', 'origin', 'go date', 'back date', 'budget']:
                answer = 'What is the new value for ' + incoming_text + '?'
                await turn_context.send_activity(answer)
                conv_state.step = 'choose-correction-' + incoming_text

            # If the user did not answer something like 'the destination'
            else:
                answer = 'Sorry, I did not understood your answer.\r\n'
                answer += 'What is wrong? The "destination", "origin", "go date", "back date" or "budget"?'
                await turn_context.send_activity(answer)
                conv_state.step = 'choose-correction'


        # Second step of the correction, the value:
        elif conv_state.step.find('choose-correction-') != -1:
            key = conv_state.step.replace('choose-correction-', '')
            found_entities = ask_clu(incoming_text)
            found = user_infos.parse_entities_specific(found_entities, key)

            if found:
                await turn_context.send_activity('All good, correction taken.')
                answer = user_infos.sum_up()
                await turn_context.send_activity(answer)
                conv_state.step = 'sum-up-confirm'
            else:
                answer = 'Uh, that is not a valid value for a ' + key + '\r\n'
                answer += 'Can you be more specific?'
                await turn_context.send_activity(answer)


        # This is an error case, it should never happen
        else: 
            print('############ ' + conv_state.step)
            await turn_context.send_activity('é_è \r\nI am sorry I had a malfunction...\r\nWe need to restart the conversation...')
            await self.start_conv(turn_context)