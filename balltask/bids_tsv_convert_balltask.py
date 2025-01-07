'''
Paul Alexander Bloom
July 17 2023

Runs upon exit of balltask to convert the csv output to a BIDS-compatible tsv file

'''

import pandas as pd
import numpy as np

def convert_balltask_csv_to_bids(infile):
    # block_duration=28
    # response_duration=1
    # presentation_duration=2.5
    # block_type_instruction_duration=2
    slider_outputs = pd.read_csv(infile.replace('roi_outputs', 'slider_questions'))
    slider_outputs = slider_outputs[-slider_outputs.run.isna()]
    slider_outputs.reset_index(inplace=True)
    df = pd.read_csv(infile)
    df.rename(columns = {
                    'time':'onset',
                    'stage':'trial_type',
                    'cen':'cen_signal',
                    'dmn':'dmn_signal',
                    'volume':'feedback_source_volume'}, 
              inplace=True)
    df['duration']=0
    df['pda']=df.cen_signal-df.dmn_signal
    df['cen_hit']=np.where(df.cen_cumulative_hits.diff(periods=-1) == -1, 1, 0)
    df['dmn_hit']=np.where(df.dmn_cumulative_hits.diff(periods=-1) == -1, 1, 0)
    df['participant']=str(slider_outputs['id'][0])
    df.participant = "sub-" + df.participant
    df['run'] = slider_outputs['run'][0]
    df['feedback_on'] = slider_outputs['feedback_on'][0]
    df['slider_noting'] = (slider_outputs.loc[slider_outputs.question_text=='How often were you using the mental noting practice?', 'response'])
    df['slider_ballcheck'] = (slider_outputs.loc[slider_outputs.question_text=='How often did you check the position of the ball?', 'response'])
    df['slider_difficulty'] = (slider_outputs.loc[slider_outputs.question_text=='How difficult was it to apply mental noting?', 'response'])
    df['slider_calm'] = (slider_outputs.loc[slider_outputs.question_text=='How calm do you feel right now?', 'response'])
    df.fillna('n/a', inplace=True)
    out_df = df[['onset', 'duration', 'trial_type', 'feedback_source_volume',
                 'cen_signal', 'dmn_signal', 'pda', 
                 'ball_y_position','cen_hit', 'dmn_hit', 
                'scale_factor', 'participant', 'run', 'feedback_on',
                'slider_noting', 'slider_ballcheck', 'slider_difficulty', 'slider_calm']]

    outfile_stems = infile.split('_')
    path = outfile_stems[0].split('/')
    run_num = int(slider_outputs['run'][0])
    if str(slider_outputs['feedback_on'][0]) == 'Feedback':
        run_type = 'feedback'
    else:
        if run_num == 1:
            run_type='transferpre'
        elif run_num == 2:
            run_type='transferpost'
            run_num = 1
        elif run_num ==3:
            run_type='transferpost'
            run_num=2
            
    # put together bids tsv filename
    outfile = 'data/' + str(slider_outputs['id'][0]) +  '/sub-' + str(slider_outputs['id'][0]) + '_ses-nf_task-' + run_type + '_run-' + "{:02d}".format(run_num) + '.tsv'
    out_df.to_csv(outfile, sep ='\t', index=False)
    return(out_df)
