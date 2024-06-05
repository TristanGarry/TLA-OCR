import pandas as pd
from thefuzz import process

df = pd.read_csv('test.csv')

df.dropna(inplace=True)

def find_closest_match_fuzz(input_str, options, threshold=75):
    match, score = process.extractOne(input_str, options)
    return match if score >= threshold else pd.NA

# Valid character options
character_options = ["Onion", "Garlic", "Beef", "Pork", "Rice", "Noodle"]

df['player_1_character'] = df['player_1_character'].apply(lambda x: find_closest_match_fuzz(x, character_options))
df['player_2_character'] = df['player_2_character'].apply(lambda x: find_closest_match_fuzz(x, character_options))

df.dropna(inplace=True)

with open('unique_players.csv', 'r') as fil:
    unique_players = fil.read().split('\n')

# Alternate player names that are quite different in unique_players.csv
unique_players.append('Hitaka')
unique_players.append('Savory Buns')

df['player_1_name'] = df['player_1_name'].apply(lambda x: find_closest_match_fuzz(x, unique_players))
df['player_2_name'] = df['player_2_name'].apply(lambda x: find_closest_match_fuzz(x, unique_players))

df = df[['player_1_name', 'player_1_character', 'player_2_name', 'player_2_character']]

df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

print(df)
