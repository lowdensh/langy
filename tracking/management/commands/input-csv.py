from django.core.management.base import BaseCommand, CommandError
from tracking.management.commands._slutil import tprint
from tracking.management.commands._vocabulary import get_word_to_ix
import numpy as np
import pandas as pd
import torch
import torch.nn as nn


csv_directory = 'model_data/'

EMBEDDING_DIM = 5     # 5 dimensional embeddings
torch.manual_seed(1)  # reproducible results

# Dictionary mapping unique foreign words to indices
word_to_ix = get_word_to_ix()

# Stores embeddings for all words
# Indices from word_to_ix are used to find the embed Tensor for a particular word
embeddings = nn.Embedding(len(word_to_ix), EMBEDDING_DIM)


# Returns a Tensor
#   for a foreign word embedding.
#   An embedding is a numerical representation/encoding of a string.
#   Each Tensor has EMBEDDING_DIM dimensions, where each item is a float.
#   e.g. 'lernen' : tensor([[ 0.9712,  0.3932, -2.1187, -2.1191, -2.0247]])
def get_embed(word):
    lookup_tensor = torch.tensor([word_to_ix[word]], dtype=torch.long)
    return embeddings(lookup_tensor)


class Command(BaseCommand):
    help = ('Create a csv of transformed learning traces to use as input to a model. '
            'Foreign words are transformed into embed features')

    def add_arguments(self, parser):
        parser.add_argument(
            'input_csv',
            type=str,
            help='Filename (without extension) for the input csv e.g. \'learning_traces_duolingo\'')
        parser.add_argument(
            'output_csv',
            type=str,
            help='Filename (without extension) for the output csv e.g. \'model_input_duolingo\'')

    def handle(self, *args, **kwargs):
        input_csv = f'{csv_directory}{kwargs["input_csv"]}.csv'
        output_csv = f'{csv_directory}{kwargs["output_csv"]}.csv'

        # Read csv and create dataframe
        tprint(f'reading {input_csv} and creating dataframe')
        df = None
        try:
            df = pd.read_csv(input_csv)
        except:
            raise CommandError(f'could not read {input_csv}')

        # Display data
        tprint(f'{df.shape[0]} datapoints:')
        print(df.head())
        
        # Prepare to transform foreign words into embed features
        # Get embeds for all foreign words
        tprint('getting embeds for foreign words')
        df['embed'] = df['frn'].apply(get_embed)

        # Get ith item from Tensor in embed column
        def get_embed_item(row, i):
            return row['embed'][0][i].item()

        # Create new feature per embed dimension
        tprint('creating features for word embeds')
        for i in range(EMBEDDING_DIM):
            tprint(f'embed feature {i+1}/{EMBEDDING_DIM}')
            df[f'frn_{i}'] = df.apply(get_embed_item, i=i, axis=1)

        # Drop columns now that foreign words are represented numerically
        tprint('dropping columns')
        df.drop(['frn', 'embed'], axis=1, inplace=True)

        # Display data
        tprint(f'{df.shape[0]} datapoints:')
        print(df.head())

        # Create csv
        tprint(f'creating {output_csv}')
        try:
            df.to_csv(output_csv, index=False)
        except:
            raise CommandError(f'could not create {output_csv}')

        tprint('done.')
