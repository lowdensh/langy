from tracking.management.commands._slutil import tprint
import numpy as np
import pandas as pd


csv_directory = 'model_data/'
duolingo_csv = f'{csv_directory}learning_traces_duolingo_13m.csv'
langy_csv = f'{csv_directory}learning_traces_langy.csv'


# Returns a list
#   of unique foreign words from Duolingo and Langy learning traces, sorted alphabetically.
#   Built from Duolingo and Langy learning trace csvs.
def get_vocabulary():
    duolingo_df = None
    langy_df = None

    try:
        duolingo_df = pd.read_csv(duolingo_csv)
    except Exception:
        tprint(f'could not read {duolingo_csv}')
        return None

    try:
        langy_df = pd.read_csv(langy_csv)
    except Exception:
        tprint(f'could not read {langy_csv}')
        return None

    duolingo_words = duolingo_df['frn'].unique().tolist()
    langy_words = langy_df['frn'].unique().tolist()

    return sorted(np.unique(duolingo_words + langy_words))

# Returns a dictionary
#   mapping unique foreign words to indices.
#   Built from Duolingo and Langy learning trace csvs.
def get_word_to_ix():
    vocabulary = get_vocabulary()
    if vocabulary:
        return {word: index for index, word in enumerate(vocabulary)}
    else:
        tprint(f'vocabulary is empty')
        return None