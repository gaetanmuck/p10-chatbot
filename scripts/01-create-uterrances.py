import os, json
import pandas as pd
import dotenv; dotenv.load_dotenv()


# Get environment variables
print('[CREATE-UTTERANCES]: Load variables...')

frame_path = os.environ.get('PATH_FRAMES')
utterances_path = os.environ.get('PATH_UTTERANCES')
# train_rate = float(os.environ.get('CLU_TRAIN_RATE'))
language_code = os.environ.get('CLU_LANGUAGE_CODE')

if not frame_path: raise SystemExit('> Environment variable [PATH_FRAMES] is missing')
if not utterances_path: raise SystemExit('> Environment variable [PATH_UTTERANCES] is missing')
# if not train_rate: raise SystemExit('> Environment variable [CLU_TRAIN_RATE] is missing')
if not language_code: raise SystemExit('> Environment variable [CLU_LANGUAGE_CODE] is missing')


# Read the initial raw data
print('[CREATE-UTTERANCES]: Read raw data...')
frames = pd.read_json(frame_path)


# Extract only turns from raw data
print('[CREATE-UTTERANCES]: Extract turns from raw data...')
turns = []
for i, row in frames.iterrows():
    for turn in row['turns']:
        if turn['author'] == 'user':
            turns.append(turn)


# Create utterances
print('[CREATE-UTTERANCES]: Create utterances...')
utterances = []
for turn in turns:

    # Get wanted properties
    properties = []
    all_acts = turn['labels']['acts']
    for act in all_acts:
        for arg in act['args']:
            if 'val' not in arg: continue
            if arg['key'] == 'intent' and arg['val'] == 'book': properties.append({'val': 'BookFlight', 'key': 'intent'})
            elif arg['key'] == 'dst_city': properties.append({'val': arg['val'].lower(), 'key': 'destination'})
            elif arg['key'] == 'or_city': properties.append({'val': arg['val'].lower(), 'key': 'origin'})
            elif arg['key'] == 'str_date': properties.append({'val': arg['val'].lower(), 'key': 'go_date'})
            elif arg['key'] == 'end_date': properties.append({'val': arg['val'].lower(), 'key': 'back_date'})
            elif arg['key'] == 'budget': properties.append({'val': arg['val'].lower(), 'key': 'budget'})
            else: pass

    # Prepare the variables
    intent = 'BookFlight'
    text = turn['text'].lower()
    entities = []

    # Find indexes of properties in string
    for prop in properties:
        if prop['key'] == 'intent': continue

        index = text.find(prop['val'])
        entities.append({
            'category': prop['key'],
            'offset': index,
            'length': len(prop['val'])
        })


    # Create utterance
    utterances.append({
        'intent': intent, 
        'language': language_code,
        'text': text,
        'entities': entities
    })

print('[CREATE-UTTERANCES]: All utterances number:', len(utterances))


# Filter utterances
print('[CREATE-UTTERANCES]: Filter utterances...')
utterances_filtered = []
for ut in utterances:
    
    # We do not take ones with no entities
    if len(ut['entities']) == 0: continue    

    # We filter out the ones which have a problem (index of entity == -1)
    else: 
        pb = False
        for ent in ut['entities']:
            if ent['offset'] == -1: 
                pb = True
                break
        if pb: continue
        else: utterances_filtered.append(ut)


# Have unicity on texts
utterances_filtered = pd.DataFrame(utterances_filtered).drop_duplicates('text')
print('[CREATE-UTTERANCES]: Filtered utterances number:', len(utterances))


# Shuffle utterances
utterances_filtered = utterances_filtered.sample(frac=1).reset_index(drop=True)


### The next part is not needed anymore: when training, the option is directly put there
### We let the code if the future, we want to use this instead of the default options

# print('[CREATE-UTTERANCES]: Train test split...')

# # Flag a dataset column with 'Test' or 'Train according to environment variable
# utterances_filtered['dataset'] = 'Test'
# # Because we just shuffled utterances, we can make the test train split by taking first X rows are train, and ones after are test
# max_index = int(train_rate * len(utterances_filtered))
# for i, row in utterances_filtered.iterrows():
#     if i > max_index: break
#     utterances_filtered.at[i, 'dataset'] = 'Train'


# # Shuffle again utterances because of test train split
# utterances_filtered = utterances_filtered.sample(frac=1)


# Save dataset as json at the right place
print('[CREATE-UTTERANCES]: Write utterances... ')
# utterances_filtered.to_json(utterances_path, orient='records')
utterances_filtered[0:3].to_json(utterances_path, orient='records') # Temp for test