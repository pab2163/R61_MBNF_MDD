#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
from pull_timings import *
import pandas as pd
import random
import os  # handy system and path functions
import csv
import time
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

block_order = pd.DataFrame({'block': np.arange(10), 
    'block_type': ['positive', 'self', 'other',  'other', 'self',  'other', 'self',  'self', 'other','positive']})

# Store info about the experiment session
expName = 'task-selfref_run-01'  # from the Builder filename that created this script
expInfo = {'participant':'', 'session':1, 'run':1}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False: core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

if not os.path.exists(f'{_thisDir}/reMIND/'):
    os.mkdir(f'{_thisDir}/reMIND/')

if not os.path.exists(f"{_thisDir}/reMIND/{expInfo['participant']}"):
    os.mkdir(f"{_thisDir}/reMIND/{expInfo['participant']}")

# pull word order for the participant
participant_number = int(expInfo['participant'].replace('remind-', ''))
word_order_file = f"word_list_splits/word_order_{participant_number}.csv"
word_order = pd.read_csv(word_order_file)
word_list = word_order[word_order.run == expInfo['run']]
#print(word_list)

negative_words = list(word_list.word[word_list.valence_condition == 'negative'])
positive_words = list(word_list.word[word_list.valence_condition == 'positive']) 
random.shuffle(positive_words)
random.shuffle(negative_words)


print(negative_words)
print(positive_words)

# output file setm
filename = f"{_thisDir}/reMIND/{expInfo['participant']}/reMIND_ses{expInfo['session']}_task-selfref_run_{expInfo['run']}"

def write_to_tsv(row_info:list):
    with open(filename+'_events.csv', 'a') as csvfile:
        stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        stim_writer.writerow(row_info)
 
write_to_tsv(['participant','session', 'date', 'exp_name', 'frame_rate', 'absolute_time', 'trigger_time', 'trial_type', 'trial_num', 'word', 'response_time','reponse_key'])

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)
trial_duration = 2.5

# Setup the Window
win = visual.Window(size=(1920, 1080), fullscr=True, screen=1, allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    )

# Initialize components for Routine "instruct"
instructClock = core.Clock()
instruct_text = visual.TextStim(win=win, ori=0, name='instruct_text',
    text=u'Next you will see a set of adjectives.\n\nPlease make judgments about the presented words\ndepending on the current TASK:\n\n1) Self-condition: judge whether the word describes you. \n\n2) Other-condition: judge whether the word describes Abraham Lincoln.\n\n3) Positive-condition: judge if the word is positive.\n\nAnd then answer "YES -index or "NO" -middle finger. \n\n                            Press any button to start!',    font='Arial',
    pos=[0.0, 0], height=0.08, wrapWidth=1.5,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "trigger"
triggerClock = core.Clock()
trial_clock = core.Clock()
text_3 = visual.TextStim(win=win, ori=0, name='text_3',
    text=u'waiting for trigger',    font=u'Arial',
    pos=[0, 0], height=0.1, wrapWidth=2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "fixation"
fixationClock = core.Clock()

fix_stim = visual.TextStim(win=win, ori=0, name='fix_stim',
    text=u'+',    font=u'Arial',
    pos=[0, 0], height=0.2, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)


controlClock = core.Clock()
prefix = visual.TextStim(win=win, ori=0, name='prefix',
    text=u'+',    font=u'Arial',
    pos=[0, 0], height=0.2, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)


word = visual.TextStim(win=win, ori=0, name='word',
    text='default text',    font=u'Arial',
    pos=[0, 0], height=0.2, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-1.0)

yes = visual.TextStim(win=win, ori=0, name='word',
    text='yes',    font=u'Arial',
    pos=[0.7, 0.5], height=0.2, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-1.0)

no = visual.TextStim(win=win, ori=0, name='word',
    text='no',    font=u'Arial',
    pos=[-0.7, 0.5], height=0.2, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-1.0)
    

block_type_text = visual.TextStim(win=win, ori=0, name='word',
    text='block_text',    font=u'Arial',
    pos=[0.0, -0.7], height=0.2, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-1.0)

postfix = visual.TextStim(win=win, ori=0, name='postfix',
    text=u'+',    font=u'Arial',
    pos=[0, 0], height=0.2, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-2.0)


# store frame rate of monitor if we can measure it successfully
expInfo['frameRate']=win.getActualFrameRate()
if expInfo['frameRate']!=None:
    frameDur = 1.0/round(expInfo['frameRate'])
else:
    frameDur = 1.0/60.0 # couldn't get a reliable measure so guess

def run_instructions():
    instruct_text.draw()
    win.flip()
    continueRoutine = True
    while continueRoutine:
        theseKeys = event.getKeys(keyList=['b'])
        if len(theseKeys) > 0:  # at least one key was pressed
                # a response ends the routine
                continueRoutine = False
    write_to_tsv([expInfo['participant'],expInfo['session'], expInfo['date'], 
                    expName, expInfo['frameRate'], time.time(), '', 'instructions', '', '', '',''])

'''
Get trigger
'''
def get_trigger():
    #trigger_resp = event.BuilderKeyResponse()
    #trigger_resp = NOT_STARTED
    event.clearEvents(eventType='keyboard')
    text_3.draw()
    win.flip()
    triggerClock.reset()
    continueRoutine = True
    while continueRoutine:
        theseKeys = event.getKeys(keyList=['t'])
        if len(theseKeys) > 0:  # at least one key was pressed
                trigger_rt = triggerClock.getTime()
                triggerClock.reset()
                print(trigger_rt)
                # a response ends the routine
                continueRoutine = False
                write_to_tsv([expInfo['participant'],expInfo['session'], expInfo['date'], 
                    expName, expInfo['frameRate'], time.time(), 0, 'trigger', '', '', '',''])

'''
Run a block of trials
'''
def run_block(n_trials, block_type, block_number):
    if block_type == 'positive':
        block_type_text.setText(f'Is the word positive?')
    elif block_type == 'self':
        block_type_text.setText(f'Does this word describe you?')
    elif block_type == 'other':
        block_type_text.setText(f'Does this word describe your friend?')

    block_type_text.draw()
    win.flip()
    core.wait(1)
    # get timings just for the current block
    block_timing_frame = all_block_timings[all_block_timings.block == block_number]
    block_timing_frame.reset_index(inplace = True)

    # run each trial in the block, pulling the word type (positive vs. negative) and fixation duration (ISI) from the block_timing_frame
    for trial_num in range(n_trials):
        run_trial(trial_type = block_timing_frame.stim_type[trial_num], fixation_duration= block_timing_frame.fix_duration[trial_num])

'''
Show a fixation cross 
'''
def run_fixation(duration):
    # present fixation
    fix_stim.draw()
    win.flip()
    fix_time = core.StaticPeriod(screenHz=expInfo['frameRate'])
    fix_time.start(duration) 
    fix_time.complete() 
    write_to_tsv([expInfo['participant'],expInfo['session'], expInfo['date'], 
                    expName, expInfo['frameRate'], time.time(), triggerClock.getTime(), 'fixation', 1, '', '',''])
    event.clearEvents(eventType='keyboard')

'''
Run a single trial
'''
def run_trial(trial_type, fixation_duration):
    # fixation at beginning of trial
    run_fixation(duration=fixation_duration)
    
    # present word 
    trial_clock.reset()
    if trial_type == 'negative':
        trial_word = negative_words.pop(0)
    elif trial_type == 'positive':
        trial_word = positive_words.pop(0)
    word.setText(trial_word)
    endExpNow = False
    no.bold = False
    yes.bold = False
    word.draw()
    yes.draw()
    no.draw()
    block_type_text.draw()
    win.flip()
    write_to_tsv([expInfo['participant'],expInfo['session'], expInfo['date'], 
                    expName, expInfo['frameRate'], time.time(), triggerClock.getTime(), 'word_presentation', 1, trial_word, '', ''])
    
    # get participant button press response for word
    continueRoutine = True
    while continueRoutine:            
        trial_time = trial_clock.getTime()
        if trial_time > 0 and trial_time < trial_duration:
            theseKeys = event.getKeys(keyList=['1', '2', 'escape'])
            if "escape" in theseKeys:
                endExpNow = True

            # if participant has pressed a button    
            if len(theseKeys) > 0:
                print(theseKeys)   
                write_to_tsv([expInfo['participant'],expInfo['session'], expInfo['date'], 
                                expName, expInfo['frameRate'], time.time(), triggerClock.getTime(), 'response', 1, 
                                trial_word, trial_clock.getTime(), theseKeys[0]])
                # change color of selected word
                if '1' in theseKeys:
                    no.bold = True
                elif '2' in theseKeys:
                    yes.bold = True
                word.draw()
                yes.draw()
                no.draw()
                block_type_text.draw()
                win.flip()
            if endExpNow:
                win.close()
                core.quit()
        else:
            continueRoutine = False 
            if endExpNow:
                core.quit()
                core.quit()      


run_instructions()
get_trigger()

for block_num in range(block_order.shape[0]):
    run_fixation(8)
    run_block(n_trials = 6, block_type = block_order.block_type[block_num], block_number = block_num)


win.close()
core.quit()
