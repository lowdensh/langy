"""Create a csv of learning traces from Duolingo or Langy."""

from django.core.management.base import BaseCommand, CommandError
from tracking.management.commands._slutil import tprint
from tracking.models import LearningTrace
import numpy as np
import pandas as pd


csv_directory = 'model_data/'


class Command(BaseCommand):
    help = 'Create a csv of learning traces from Duolingo or Langy.'


    def add_arguments(self, parser):
        parser.add_argument(
            'target',
            type=str,
            help='The target application data to create the new csv from, either \'duolingo\' or \'langy\'')


    def handle(self, *args, **kwargs):
        if kwargs['target'] == 'duolingo': self.create_duolingo_csv()
        if kwargs['target'] == 'langy': self.create_langy_csv()


    # Create a csv for Duolingo learning traces from a csv of existing data
    # Adapts the format to match with Langy
    def create_duolingo_csv(self):
        # input_csv = f'{csv_directory}learning_traces.13m.csv'  # 1.21GB, 13m datapoints
        input_csv = f'{csv_directory}learning_traces.13m_subset.csv'  # 100MB, 1m datapoints
        output_csv = f'{csv_directory}learning_traces_duolingo_subset.csv'

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

        # Remove columns
        df.drop([
            'timestamp',
            'user_id',
            'learning_language',
            'ui_language',
            'lexeme_id',
            'session_seen',
            'session_correct'
            ], axis=1, inplace=True)


        #################
        # lexeme_string #
        #################

        # Transform lexeme_string from lexeme tags to single words
        # Remove <tag components>
        # Extract word after first slash /
        tprint('transforming lexeme_strings to words')
        df['lexeme_string'].replace(r'<[^>]*>', '', regex=True, inplace=True)
        df['lexeme_string'] = df['lexeme_string'].str.extract('([^\/]*$)')
        
        # Remove datapoints for lemexe_strings with unexpected characters ' and +
        tprint('removing lemexe_string words with unexpected characters')
        df = df[~df['lexeme_string'].str.contains(r"['\+]")]


        ##################
        # Manage columns #
        ##################

        # Add new columns for additional interaction statistics
        # Duolingo combines (seen, interacted, tested) in practice sessions
        # Langy recognises these statistics distinctly
        tprint('adding new columns for Langy interaction statistics')
        df['interacted'] = df['history_seen']
        df['tested'] = df['history_seen']

        # Rename columns
        df.rename(columns={
            'p_recall': 'p_trans',
            'lexeme_string': 'frn',
            'history_seen': 'seen',
            'history_correct': 'correct',
            }, inplace=True)

        # Reorder columns
        df = df[['frn', 'delta', 'seen', 'interacted', 'tested', 'correct', 'p_trans']]


        ###########
        # p_trans #
        ###########
        
        # Recalculate p_trans for each datapoint
        # Duolingo p_recall is calculated for each particular session, rather than for user's full history
        tprint('recalculating p_trans')
        df['p_trans'] = df['correct'] / df['tested']

        # Display data
        tprint(f'{df.shape[0]} datapoints:')
        print(df.head())


        #######
        # CSV #
        #######

        # Create csv
        tprint(f'creating {output_csv}')
        try:
            df.to_csv(output_csv, index=False)
        except:
            raise CommandError(f'could not create {output_csv}')

        tprint('done.')


    # Create a csv for Langy LearningTrace objects from the database
    def create_langy_csv(self):
        output_csv = f'{csv_directory}learning_traces_langy.csv'

        # Get data and create dataframe
        tprint(f'getting traces and creating dataframe')
        traces_list = []
        for t in LearningTrace.objects.all():
            traces_list.append({
                'frn': t.frn,
                'delta': t.delta,
                'seen': t.seen,
                'interacted': t.interacted,
                'tested': t.tested,
                'correct': t.correct,
                'p_trans': t.p_trans
            })
        df = pd.DataFrame(traces_list)

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
