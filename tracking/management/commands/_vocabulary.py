from language.models import Translation
from tracking.management.commands._slutil import tprint
import numpy as np
import pandas as pd


csv_directory = 'model_data/'
duolingo_csv = f'{csv_directory}learning_traces_duolingo_subset.csv'


# Returns a list
#   of unique foreign words from Duolingo learning traces and all Langy Translations. 
#   Sorted alphabetically.
def get_vocabulary():
    duolingo_df = None

    try:
        duolingo_df = pd.read_csv(duolingo_csv)
    except Exception:
        tprint(f'could not read {duolingo_csv}')
        return None
    duolingo_words = duolingo_df['frn'].unique().tolist()

    langy_words = [t.readable_word for t in Translation.objects.all()]
    langy_words = sorted(list(set(langy_words)))  # unique and ordered

    return sorted(np.unique(duolingo_words + langy_words))

# Returns a dictionary
#   mapping unique foreign words to indices.
def get_word_to_ix():
    vocabulary = get_vocabulary()
    if vocabulary:
        return {word: index for index, word in enumerate(vocabulary)}
    else:
        tprint(f'vocabulary is empty')
        return None
