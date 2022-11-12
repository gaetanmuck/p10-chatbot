from botbuilder.core import TurnContext, ActivityHandler, ConversationState, UserState
from botbuilder.schema import ActivityTypes, ChannelAccount
from dotenv import load_dotenv; load_dotenv()
from tools.clu import ask_clu
from model.usermodel import UserModel
from model.convstate import ConvState
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
import requests, os


###########################################
# About Azure insights and metrics there: #
###########################################


# Global vars
stats = stats_module.stats
view_manager = stats.view_manager
stats_recorder = stats.stats_recorder

# Number of conversation
conversation_count = measure_module.MeasureInt('Conversation', 'Number of conversation since last deployment', 'conversations')
conversation_view = view_module.View('Conversation view', 'Number of conversation since last deployment', [], conversation_count, aggregation_module.CountAggregation())
view_manager.register_view(conversation_view)

# Number of Ended conversation
conversation_ended_count = measure_module.MeasureInt('Ended conversation', 'Number of ended conversation since last deployment', 'ended conversations')
conversation_ended_view = view_module.View('Ended conversation view', 'Number of ended conversation since last deployment', [], conversation_ended_count, aggregation_module.CountAggregation())
view_manager.register_view(conversation_ended_view)

# Number of messages
message_count = measure_module.MeasureInt('Message', 'Number of messages since last deployment', 'messages')
message_view = view_module.View('Message view', 'Number of messages since last deployment', [], message_count, aggregation_module.CountAggregation())
view_manager.register_view(message_view)

# Number of correctly interpretated sentences
right_interpretation_count = measure_module.MeasureInt('Understood', 'Number of sentences correctly understood since last deployment', 'right interpretations')
message_view = view_module.View('Understood view', 'Number of sentences correctly understood since last deployment', [], right_interpretation_count, aggregation_module.CountAggregation())
view_manager.register_view(message_view)

# Number of wrongly interpretated sentences
wrong_interpretation_count = measure_module.MeasureInt('Misunderstood', 'Number of sentences misunderstood since last deployment', 'wrong interpretations')
wrong_interpretation_view = view_module.View('Misunderstood view', 'Number of sentences misunderstood since last deployment', [], wrong_interpretation_count, aggregation_module.CountAggregation())
view_manager.register_view(wrong_interpretation_view)

# Total interpretations
total_interpretation_count = measure_module.MeasureInt('Interpretations', 'Number of sentences interpretated since last deployment', 'interpretations')
total_interpretation_view = view_module.View('Understood view', 'Number of sentences interpretated since last deployment', [], total_interpretation_count, aggregation_module.CountAggregation())
view_manager.register_view(total_interpretation_view)

# Rates of correct interpretations
right_rate_count = measure_module.MeasureFloat('Right rate', '% of sentences correctly interpretated since last deployment', '%')
right_rate_interpretation_view = view_module.View('Right rate view', 'Number of sentences interpretated since last deployment', [], right_rate_count, aggregation_module.LastValueAggregation())
view_manager.register_view(right_rate_interpretation_view)

# Again, globals:
mmap1 = stats_recorder.new_measurement_map()
tmap1 = tag_map_module.TagMap()
mmap2 = stats_recorder.new_measurement_map()
tmap2 = tag_map_module.TagMap()

exporter = metrics_exporter.new_metrics_exporter(
    instrumentation_key=os.environ.get('INSTRUMENTATION_KEY')
)
view_manager.register_exporter(exporter)

###########################################

class FlyMeBot(ActivityHandler):
    
    def __init__(self, conv_state: ConversationState, user_state: UserState):
        """Initialize Bot with 'global' variables"""

        self.right_interpretation = 0
        self.wrong_interpretation = 0

        self.conv_state = conv_state
        self.user_state = user_state

        self.conv_prop = self.conv_state.create_property("conv_state")
        self.user_prop = self.user_state.create_property("user_state")


    def create_conv_history(self):
        """Connect to the history handled and get a conversation id."""
        print('WEB_APP_PATH:', os.environ.get('WEB_APP_PATH'))
        return requests.get(os.environ.get('WEB_APP_PATH') + '/new-conversation').json()['conv_id']


    def send_message_to_history(self, conv_id, writer, text, understood):
        """Save a message into the history (make the API call)."""
        print('WEB_APP_PATH:', os.environ.get('WEB_APP_PATH'))
        requests.get(os.environ.get('WEB_APP_PATH') + '/new-message?conversation_id=' + str(conv_id) + '&text=' + str(text) + '&writer=' + str(writer) + '&understood=' + str(understood))



    async def bot_answers(self, turn_context: TurnContext, conv_id, text, understood=True):
        """Function to handle response from the Bot (history + send message to the chat)"""
        self.send_message_to_history(conv_id, 'Bot', text, understood)
        await turn_context.send_activity(text)



    async def on_turn(self, turn_context: TurnContext):
        """Way to store the state from a turn to another."""

        await super().on_turn(turn_context)

        await self.conv_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)



    async def on_members_added_activity(self, member_added: ChannelAccount, turn_context: TurnContext):
        """Begining of conversation"""

        # Adding 1 conversation to azure insights
        mmap1.measure_int_put(conversation_count, 1)
        mmap1.record(tmap1)
        print('-- INSIGHTS: New conversation --')

        user_infos = await self.user_prop.get(turn_context, UserModel)
        user_infos.conv_id = self.create_conv_history()
        await self.start_conv(turn_context, user_infos.conv_id)



    async def start_conv(self, turn_context: TurnContext, conv_id):
        """Print out the welcoming messages."""

        await self.bot_answers(turn_context, conv_id, 'Hello, welcome to FlyMeBot,\r\nI am a here to understand where and when do you want to book a flight.')
        await self.bot_answers(turn_context, conv_id, 'Tell me informations about the flight you would like to book?')



    async def end_conv(self, turn_context: TurnContext, conv_id):
        """Print out the ending messages."""

        mmap1.measure_int_put(conversation_ended_count, 1)
        mmap1.record(tmap1)
        print('-- INSIGHTS: Conversation ended -- ')

        answer = "All right, I will look for that, and send you an offer that most correspond to your wishes, directly in your email!"
        answer += "\r\nI hope the conversation went smoothly enough to satisfy you."
        answer += "\r\nThank you very much for using FlyMeBot to look for your flight."
        await self.bot_answers(turn_context, conv_id, answer)
        answer = '-- you may now close the conversation, or send another message about another flight --'
        await self.bot_answers(turn_context, conv_id, answer)


    async def look_for_missing(self, missing, turn_context: TurnContext, conv_id):
        """Asks the user about missing information."""
        answer = 'I need additional information about your flight.\r\n'
        answer += 'Can you tell me more about the ' + missing.replace('_', ' ') + ' of your flight?'
        await self.bot_answers(turn_context, conv_id, answer)




    async def on_message_activity(self, turn_context: TurnContext):
        """Message handling"""
        
        # Adding 1 message to azure insights
        mmap1.measure_int_put(message_count, 1)
        mmap1.record(tmap1)
        print('-- INSIGHTS: New message -- ')

        incoming_text = turn_context.activity.text

        conv_state = await self.conv_prop.get(turn_context, ConvState)
        user_infos = await self.user_prop.get(turn_context, UserModel)

        self.send_message_to_history(user_infos.conv_id, 'User', incoming_text, True)

        # When the conversation just started or has been reset:
        if conv_state.step == 'init':
            found_entities = ask_clu(incoming_text)

            if len(found_entities) == 0:
                answer = 'I found no information about a possible flight in your message, can you try again with different words?'
                await self.bot_answers(turn_context, user_infos.conv_id, answer)
                
                conv_state.step = 'init' # We keep it at this step
            
            else:
                user_infos.parse_entities(found_entities, True)
                answer = user_infos.sum_up()
                await self.bot_answers(turn_context, user_infos.conv_id, answer)
                conv_state.step = 'sum-up-confirm'


        # The user should have confirm (or not) the SUM UP:
        elif conv_state.step == 'sum-up-confirm':

            # If he answered YES (or alike):
            # Close the conversation
            if incoming_text.lower() in ['yes', 'y', 'yeah', 'yea', 'yep', 'ok', 'okey', 'okay', 'affirmative', 'amen', 'good', 'true', 'sure', 'aye']:
                missing = user_infos.get_missing()

                # Adding 1 correct interpretation to azure insights
                mmap2.measure_int_put(right_interpretation_count, 1)
                mmap2.record(tmap2)
                self.right_interpretation += 1
                print('-- INSIGHTS: Right interpretation -- ')
                await self.bot_answers(turn_context, user_infos.conv_id, "Very good!")

                # The user provided every information needed: finish the conversation
                if missing == 'complete':
                    await self.end_conv(turn_context, user_infos.conv_id)
                    user_infos = UserModel()
                    conv_state.step = 'init'

                # There is some information missing:
                else:  
                    await self.look_for_missing(missing, turn_context, user_infos.conv_id)
                    conv_state.step = 'look-for-missing'


            # If he answered NO (or alike):
            # Change what information needs to be changed
            elif incoming_text.lower() in ['no', 'n', 'nope', 'not', 'wrong', 'not really']:

                # Adding 1 wrong interpretation to azure insights
                mmap2.measure_int_put(wrong_interpretation_count, 1)
                mmap2.record(tmap2)
                self.wrong_interpretation += 1
                print('-- INSIGHTS: Wrong interpretation -- ')

                # Send response to user
                answer = 'That is sad...\r\n'
                answer += 'What is wrong? The "destination", "origin", "go date", "back date" or "budget"?'
                await self.bot_answers(turn_context, user_infos.conv_id, answer, False)
                conv_state.step = 'choose-correction'
            
            # If he answered something the bot did not get (not registered as a yes or a no)
            else: await turn_context.send_activity('Mmh, was that a yes or a no?')
        
            mmap2.measure_float_put(right_rate_count, self.right_interpretation / (self.right_interpretation + self.wrong_interpretation))
            mmap2.record(tmap2)
            print('-- INSIGHTS: Interpretation rate: -- ', self.right_interpretation / (self.right_interpretation + self.wrong_interpretation))


        # The question about a specific information has been asked to the user, parse the user answer
        elif conv_state.step == 'look-for-missing':
            found_entities = ask_clu(incoming_text)
            missing = user_infos.get_missing() # To get the asked key
            found = user_infos.parse_entities_specific(found_entities, missing)

            if found:
                missing = user_infos.get_missing() # To see if there is still missing information:
                if missing == 'complete':
                    answer = user_infos.sum_up()
                    await self.bot_answers(turn_context, user_infos.conv_id, answer)
                    conv_state.step = 'sum-up-confirm'
                else:  
                    await self.look_for_missing(missing, turn_context, user_infos.conv_id)
                    conv_state.step = 'look-for-missing'
            else:
                answer = 'Uh, that is not a valid value for a ' + missing.replace('_', ' ') + '\r\n'
                answer += 'Can you be more specific?'
                await self.bot_answers(turn_context, user_infos.conv_id, answer)



        # First step of the correction, the property:
        elif conv_state.step == 'choose-correction':
            incoming_text = incoming_text.replace('the ', '')

            # If the user did say a righteous property name
            if incoming_text in ['destination', 'origin', 'go date', 'back date', 'budget']:
                answer = 'What is the new value for ' + incoming_text + '?'
                await self.bot_answers(turn_context, user_infos.conv_id, answer)
                conv_state.step = 'choose-correction-' + incoming_text

            # If the user did not answer something like 'the destination'
            else:
                answer = 'Sorry, I did not understood your answer.\r\n'
                answer += 'What is wrong? The "destination", "origin", "go date", "back date" or "budget"?'
                await self.bot_answers(turn_context, user_infos.conv_id, answer)
                conv_state.step = 'choose-correction'


        # Second step of the correction, the value:
        elif conv_state.step.find('choose-correction-') != -1:
            key = conv_state.step.replace('choose-correction-', '')
            found_entities = ask_clu(incoming_text)
            found = user_infos.parse_entities_specific(found_entities, key)

            if found:
                await turn_context.send_activity('All good, correction taken.')
                answer = user_infos.sum_up()
                await self.bot_answers(turn_context, user_infos.conv_id, answer)
                conv_state.step = 'sum-up-confirm'
            else:
                answer = 'Uh, that is not a valid value for a ' + key + '\r\n'
                answer += 'Can you be more specific?'
                await self.bot_answers(turn_context, user_infos.conv_id, answer)


        # This is an error case, it should never happen
        else: 
            print('############ ' + conv_state.step)
            await turn_context.send_activity('é_è \r\nI am sorry I had a malfunction...\r\nWe need to restart the conversation...')
            await self.start_conv(turn_context, user_infos.conv_id)