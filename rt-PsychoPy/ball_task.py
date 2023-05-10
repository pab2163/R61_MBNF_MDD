#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.81.03), Wed 04 Feb 2015 11:22:15 AM EST
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from helper_functions_ball_task import *

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

##################################################################################
## PARSE COMMAND LINE ARGUMENTS TO AUTOFILL DIALOGUE BOX AT STARTUP (for runs 2+) ##
num_cmd_line_arguments = len(sys.argv)
if num_cmd_line_arguments >= 2:
    input_participant = sys.argv[1]
else:
    input_participant = ''

# cmd line arg 3 will be run number
# if there is no command line argument 3 -- use empty string
# otherwise, use that as rum number
if num_cmd_line_arguments >= 3:
    input_run = sys.argv[2]
else:
    input_run = ''

# cmd line arg 4 will be feedback / no feedback 
if num_cmd_line_arguments >= 4:
    if sys.argv[3] == 'Feedback':
        input_feedback = ['Feedback', 'No Feedback']
    else:
        input_feedback = ['No Feedback', 'Feedback']
else:
    input_feedback = ['', 'Feedback', 'No Feedback']

# cmd line arg 5 will be 15min vs 30min
if num_cmd_line_arguments >= 4:
    if sys.argv[4] == '15min':
        input_feedback_condition = ['15min', '30min']
    else:
        input_feedback_condition = ['30min', '15min']
else:
    input_feedback_condition = ['', '15min', '30min']


# cmd line arg 6+ will be anchor
# if there is no command line argument -- use empty string
# otherwise, use that as rum number
if num_cmd_line_arguments >= 6:
    input_anchor = ' '.join(sys.argv[5:])
else:
    input_anchor = ''
#####################################################################################

# Store info about the experiment 
expName = 'DMN_BallTask'  # from the Builder filename that created thi s script
expInfo = {'participant':input_participant, 'run':input_run, 'anchor': input_anchor, 'feedback_on': input_feedback, 
           'feedback_condition': input_feedback_condition} 


murfi_FAKE=False

# Show dialogue box until all participant info has been entered
while expInfo['feedback_on'] not in ['Feedback', 'No Feedback']:
    expInfo['feedback_on'] =  input_feedback
    dlg = gui.DlgFromDict(dictionary=expInfo, title=expName, 
        labels = {'participant': 'Participant ID', 
                  'run': 'Run', 
                  'feedback_on': 'Display Feedback?',
                  'anchor': 'Participant Anchor',
                  'feedback_condition': 'Feedback Condition'},
        order = ['participant', 'run', 'feedback_on', 'anchor'])
    if dlg.OK == False: 
        core.quit()  # user pressed cancel



# Hard code other experiment info 
## Timestamp
expInfo['date'] = data.getDateStr()  
expInfo['expName'] = expName
expInfo['No_of_ROIs'] = 2
expInfo['Level_1_2_3'] = 1
expInfo['Run_Time'] = 120
expInfo['pda_outlier_threshold']=2
num_pda_outliers=0
# Baseline time before feedback (seconds)
BaseLineTime=30 

# TR (seconds)
expInfo['tr']=1.2


roi_number= str('%s') %(expInfo['No_of_ROIs'])
roi_number=int(roi_number)


# default scale factor (higher means ball moves up/down faster)
default_scale_factor = 25

# another interal scale factor to make sure scaling of feedback is appropriate (higher means ball moves up/down more SLOWLY)
internal_scaler=10

# Setup files for saving
if not os.path.isdir('data'):
    os.makedirs('data')  # if this fails (e.g. permissions) we will get error

# output file string (different depending on if feedback is being offered)
if expInfo['feedback_on']=='Feedback':
    filename = 'data' + os.path.sep + '%s_DMN_Feedback_%s' %(expInfo['participant'],expInfo['run'])
elif expInfo['feedback_on']=='No Feedback':
    filename = 'data' + os.path.sep + '%s_DMN_No_Feedback_%s' %(expInfo['participant'],expInfo['run'])


# if filepath already exists, stop run and check with user
while os.path.exists(filename + '_roi_outputs.csv'):
    warning_box = gui.Dlg(title = 'WARNING')
    warning_box.addText(f'Already have data for {expInfo["participant"]} run {expInfo["run"]}!\nClick OK to write to run  {int(expInfo["run"]) + 1} instead \
        Or, click Cancel to exit')
    warning_box.show()
    if not warning_box.OK:
        core.quit()
    else:
        expInfo['run'] = int(expInfo['run']) +1 
        filename = 'data' + os.path.sep + '%s_DMN_Feedback_%s' %(expInfo['participant'],expInfo['run'])

# If first run, use default scale factor
# Otherwise, adjust scale factor up/down if needed
if int(expInfo['run']) == 1:
    print('Run 1: starting with default scale scale factor')
    expInfo['scale_factor'] = default_scale_factor
else:
    try:
        last_run_filename = filename.replace(expInfo['run'], str(int(expInfo['run'])-1)) + '_roi_outputs.csv'
        last_run_info = pd.read_csv(last_run_filename)

        # Max values in cumulative hits columns give the total number of hits each in the last run
        last_run_cen_hits = last_run_info.cen_cumulative_hits.max()
        last_run_dmn_hits = last_run_info.dmn_cumulative_hits.max()

        print('Last run CEN hits: ', last_run_cen_hits, ' Last run DMN hits: ', last_run_dmn_hits)

        # last_run_scale_factor
        last_run_scale_factor = last_run_info.scale_factor[0]

        # if 5+ hits in either direction, decrease scale factor
        if last_run_dmn_hits >= 5 or last_run_cen_hits >= 5:
            expInfo['scale_factor'] = last_run_scale_factor * 0.75
        
        # if 0 or 1 total hits, increase scale factor
        elif last_run_cen_hits + last_run_dmn_hits <= 1:
            expInfo['scale_factor'] = last_run_scale_factor * 1.25

        # otherwise, keep scale factor the same
        else:
            expInfo['scale_factor'] = last_run_scale_factor 

        print('Last run scale factor: ', last_run_scale_factor, ' This run scale factor: ', expInfo['scale_factor'])
    except:
        print('WARNING: could not pull scale factor from previous run. Settting to default scale factor.')
        expInfo['scale_factor'] = default_scale_factor


RUN_TIME= str('%s') %(expInfo['Run_Time'])
RUN_TIME=int(RUN_TIME)
RUN_TIME=RUN_TIME

# Convert scale factor and position to pixel space
position_distance=expInfo['Level_1_2_3']
position_distance=int(position_distance)
scale_factor_z2pixels=expInfo['scale_factor']
scale_factor_z2pixels=int(scale_factor_z2pixels)
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

# Column headers for outfile
with open(filename+'_roi_outputs.csv', 'a') as csvfile:
    stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    stim_writer.writerow(['volume', 'scale_factor', 'time', 'time_plus_1.2', 'cen', 'dmn', 'stage', 'cen_cumulative_hits', 'dmn_cumulative_hits', 'pda_outlier', 'ball_y_position', 'top_circle_y_position', 'bottom_circle_y_position'])       

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=True,
    dataFileName=filename)
#save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file
endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation
# Setup the Window
win = visual.Window(size=(1080,1080), fullscr=True, screen=1, allowGUI=False, allowStencil=False,#1024, 1024
    monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    )

# store frame rate of monitor if we can measure it successfully
expInfo['frameRate']=win.getActualFrameRate()
if expInfo['frameRate']!=None:
    frameDur = 1.0/expInfo['frameRate']
else:
    print('FRAME RATE GUESSING')
    frameDur = 1.0/60.0 # couldn't get a reliable measure so guess

# Approximately how many frames does the monitor refresh per volume?
tr_to_frame_ratio = expInfo['tr']/frameDur

# Create csv output file for post-run slider questions
run_questions_file = filename + '_slider_questions.csv'
with open(run_questions_file, 'a') as csvfile:
    stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    stim_writer.writerow(["id", "run", 'feedback_on', "question_text", "reponse", "rt"])  


# Initialize components for Routine "instructions"
instructionsClock = core.Clock()
text = visual.TextStim(win=win, ori=0, name='text',
    text=u'Noting Practice\n\nIn this run you will see %s circles.\n\nThe upper yellow circle represents the brain process that corresponds to the Noting Practice.\
 \n\nTry to move the central dot into that circle!!\n\nTry to keep it there for 5 sec.\n\nIf you succeed, the circle will shrink and the dot will move back to the center.\
\n\nHow much can you shrink the circle?\n\nThis experiment will last 2 min.\n\n Press any button to start.' %int(roi_number),font=u'Arial',
    pos=[0, 0], height=0.06, wrapWidth=1.2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "trigger"
triggerClock = core.Clock()
text_3 = visual.TextStim(win=win, ori=0, name='text_3',
    text=u'waiting for scanner',    font=u'Arial',
    pos=[0, 0], height=0.1, wrapWidth=2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "baseline"
baselineClock = core.Clock()
text_2 = visual.TextStim(win=win, ori=0, name='text_2',
    text=u'+',    font=u'Arial',
    pos=[0, 0], height=0.3, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)


text_relax = visual.TextStim(win=win, ori=0, name='text_relax',
    text=u'Relax',    font=u'Arial',
    pos=[0, -.2], height=0.07, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "feedback"
feedbackClock = core.Clock()

text_4 = visual.TextStim(win=win, ori=0, name='text_4',
    text='default text',    font=u'Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-3.0)

#prepare the targets
colors=['yellow','blue','red','green','cyan','magenta','black','honeydew','indigo','maroon']
roi_names_list=['cen','dmn']
print (roi_names_list)
n_roi = roi_number
tau = 2 * np.pi
theta = np.zeros((n_roi))
for i in range(n_roi):
    theta[i] = (i * tau)/float(n_roi)

positions = np.exp((0-1j) * theta)
positions=positions*position_distance
positions = [1, -1]

# target_positions:
roi_pos = np.zeros((n_roi, 2))
for i in range(n_roi):
    roi_pos[i, :] = [(np.real(positions[i]))/3, (np.imag(positions[i]))/3]

# scale based on aspect ratio
scale=[win.size[1]/win.size[0], 1]

target_circles=[]
target_circles_id=[]
hit_counter=[]
home=[]
for i in range(n_roi):
    roi_circle_i = visual.Circle(win, pos=(roi_pos[i, 1],roi_pos[i, 0]), 
                                 radius=0.15,fillColor=None, 
                                 lineColor=colors[i], lineWidth=2)
    roi_circle_i.size *= scale
    target_circles.append(roi_circle_i)
    hit_counter.append(0)
    print (hit_counter)

starting_point = visual.Circle(win, pos=(0,0), radius=0.005,fillColor='white', lineColor='white')
home.append(starting_point)


ball = visual.Circle(win, 
                    pos=(0,0), 
                    radius=0.03,
                    fillColor='white',
                    lineColor='white',
                    lineWidth=3)

ball.size *= scale

text_5 = visual.TextStim(win=win, ori=0, name='text_5',
    text=u'thank you!',    font=u'Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

instruct_text = visual.TextStim(win=win, ori=0, name='instruct_text',
    text=u'replace me', font=u'Arial',
    pos=[0, 0], height=0.06, wrapWidth=1.2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "finish"
finishClock = core.Clock()

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

# Depending on whether feedback is offered/which run it is -- show different instruction slides
if expInfo['feedback_on'] == "No Feedback":
    if int(expInfo['run']) == 1: 
        instruction_slide_list = [no_feedback_run1_text, ready_text]
    else:
        instruction_slide_list = [no_feedback_later_runs_text, ready_text]
elif expInfo['feedback_on'] == 'Feedback':
    if int(expInfo['run']) == 1: 
        instruction_slide_list = [feedback_run1_text1, feedback_run1_text2, ready_text]
    else:
        instruction_slide_list = [feedback_later_runs_text, ready_text]

for instructions_slide in instruction_slide_list:
    instruct_text.setText(instructions_slide)
    run_instructions(instruct_text)


 #murfi communicator
from murfi_activation_communicator import MurfiActivationCommunicator
roi_names = ['cen', 'dmn']#, 'mpfc','wm']
# REPLACE THIS IP WITH THE MURFI COMPUTER'S IP 192.168.2.5
communicator = MurfiActivationCommunicator('192.168.2.5',
                                           15001, 210,
                                           roi_names,expInfo['tr'],murfi_FAKE)
print ("murfi communicator ok")

thisExp.addData('temporal_resolution', expInfo['tr'])


#------Prepare to start Routine "trigger"-------
t = 0
triggerClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
key_resp_3 = event.BuilderKeyResponse()  # create an object of type KeyResponse
key_resp_3.status = NOT_STARTED
# keep track of which components have finished
triggerComponents = []
triggerComponents.append(text_3)
triggerComponents.append(key_resp_3)
for thisComponent in triggerComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "trigger"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = triggerClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_3* updates
    if t >= 0.0 and text_3.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_3.tStart = t  # underestimates by a little under one frame
        text_3.frameNStart = frameN  # exact frame index
        text_3.setAutoDraw(True)
    
    # *key_resp_3* updates
    if t >= 0.0 and key_resp_3.status == NOT_STARTED:
        # keep track of start time/frame for later
        key_resp_3.tStart = t  # underestimates by a little under one frame
        key_resp_3.frameNStart = frameN  # exact frame index
        key_resp_3.status = STARTED
        # keyboard checking is just starting
        key_resp_3.clock.reset()  # now t=0
        event.clearEvents(eventType='keyboard')
    if key_resp_3.status == STARTED:
        theseKeys = event.getKeys(keyList=['num_add', 't','+','5'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            key_resp_3.keys = theseKeys[-1]  # just the last key pressed
            key_resp_3.rt = key_resp_3.clock.getTime()
            # a response ends the routine
            continueRoutine = False

            # reset trigger clock -- now it is keeping track of time relative to trigger!
            triggerClock.reset()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in triggerComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()
    else:  # this Routine was not non-slip safe so reset non-slip timer
        routineTimer.reset()

#-------Ending Routine "trigger"-------
for thisComponent in triggerComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# check responses
if key_resp_3.keys in ['', [], None]:  # No response was made
   key_resp_3.keys=None
# store data for thisExp (ExperimentHandler)
thisExp.addData('key_resp_3.keys',key_resp_3.keys)
if key_resp_3.keys != None:  # we had a response
    thisExp.addData('key_resp_3.rt', key_resp_3.rt)
thisExp.nextEntry()


# BASELINE: wait for 30s before delivering feedback
#------Prepare to start Routine "baseline"-------
t = 0
baselineClock.reset()  # clock 
frameN = -1
frame = 0
routineTimer.add(BaseLineTime)
# update component parameters for each repeat
# keep track of which components have finished
baselineComponents = []
baselineComponents.append(text_2)
for thisComponent in baselineComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "baseline"-------
continueRoutine = True
print("starting baseline")
while continueRoutine and routineTimer.getTime() > 0:
    # During baseline period, we still want to record MURFI outputs
    # get current time
    communicator.update()
    roi_raw_activations=[]

    # Where ROI activation first comes in
    # CEN, DMN
    try:
        for i in range(n_roi):
            roi_raw_i=communicator.get_roi_activation(roi_names_list[i], frame)
            roi_raw_activations.append(roi_raw_i)
    except:
        print (f"Did not get data for frame {frame}")
        roi_raw_activations = [np.nan, np.nan]

    # check for any missing values (nan) in the roi_raw_activatinp.isnan(roi_raw_activations[0])ons pulled for the current frame
    # If there is a nan value, this most likely indicates that data hasn't been acquired yet for the current volume. 
    # In this case, continue, and keep trying to acquire roi_raw_activations from MURFI (without advancing the frame)
    if np.isnan(roi_raw_activations[0]) or np.isnan(roi_raw_activations[1]):
        pass
    else:
        # If there is a new volume of output from MURFI, record it, and advance frame
        with open(filename+'_roi_outputs.csv', 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            print(([frame, triggerClock.getTime(), roi_raw_activations[0], roi_raw_activations[1]]))
            stim_writer.writerow([frame, expInfo['scale_factor'], triggerClock.getTime(), triggerClock.getTime() + 1.2, roi_raw_activations[0], roi_raw_activations[1], 'baseline', 0, 0, np.nan, np.nan, np.nan, np.nan])      
        frame +=1       


    t = baselineClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_2* updates
    if t >= 0.0 and text_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_2.tStart = t  # underestimates by a little under one frame
        text_2.frameNStart = frameN  # exact frame index
        text_2.setAutoDraw(True)
        text_relax.setAutoDraw(True)
    if text_2.status == STARTED and t >= (0.0 + (BaseLineTime-win.monitorFramePeriod*0.75)): #most of one frame period left
        pass
        
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in baselineComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "baseline"-------
text_2.setAutoDraw(False)
text_relax.setAutoDraw(False)
for thisComponent in baselineComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

#------Prepare to start Routine "feedback"-------
t = 0
feedbackClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
subject_key_target = event.BuilderKeyResponse()  # create an object of type KeyResponse
subject_key_target.status = NOT_STARTED
subject_key_reset = event.BuilderKeyResponse()  # create an object of type KeyResponse
subject_key_reset.status = NOT_STARTED
routineTimer.add(RUN_TIME)


# Initialize parameters before feedback
activity = 0
direction=0

# Draw initial stim positions
for i in range(n_roi):
    target_circles[i].draw()
ball.draw()
win.flip()

pda_outlier=False
#-------Start Routine "feedback"-------
continueRoutine = True
# Loop keeps going until RUN_TIME is up
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = feedbackClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *subject_key_target* updates
    if t >= 0.0 and subject_key_target.status == NOT_STARTED:
        # keep track of start time/frame for later
        subject_key_target.tStart = t  # underestimates by a little under one frame
        subject_key_target.frameNStart = frameN  # exact frame index
        subject_key_target.status = STARTED
        # keyboard checking is just starting
        subject_key_target.clock.reset()  # now t=0
        event.clearEvents(eventType='keyboard')
    if subject_key_target.status == STARTED:
        theseKeys = event.getKeys(keyList=['escape'])
        theseKeys_num=theseKeys

        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            subject_key_target.keys = theseKeys[-1]  # just the last key pressed
            subject_key_target.rt = subject_key_target.clock.getTime()
    
    # get updated data from MURFI    
    communicator.update()
    roi_raw_activations=[]

    # Where ROI activation first comes in
    # CEN, DMN
    for i in range(n_roi):
        roi_raw_i=communicator.get_roi_activation(roi_names_list[i], frame)
        roi_raw_activations.append(roi_raw_i)
       
    '''
    Check for any missing values (nan) from MURFI on the current frame. If there is a nan value, this most likely
    indicates that data hasn't been acquired yet for the current volume. In this case, continue, and keep trying to acquire
    roi_raw_activations from MURFI (without advancing the frame). This will happen several times for each volume before the data 
    for the next volume are available. 
    '''
    if np.isnan(roi_raw_activations[0]) or np.isnan(roi_raw_activations[1]):
        pass
    
    # a list of [CEN, DMN] for the current frame
    else:
        roi_activities=roi_raw_activations
        if np.nanmax(np.abs(roi_activities)) > expInfo['pda_outlier_threshold']:
            pda_outlier=True
            num_pda_outliers+=1
        else:
            pda_outlier=False

        print('time: ', routineTimer.getTime())
        print ("got feedback at frame : ",  frame, roi_raw_activations, roi_names_list)
        
        '''
        Loop through ROIs. Depending on which one has higher activity, change direction parameter 
        1 - upwards (when CEN higher)
        -1 = downwards (when DMN higher)
        '''
        for i in range(n_roi):
            target_circles[i].fillColor=None
            # for each ROI, look for the index -- see whether that ROI has the highest activity
            if roi_activities.index(np.nanmax(roi_activities))==i and np.nanmean(roi_activities)!=0:
                # Activity=absolute difference between ROI activations (always positive)
                activity=abs(np.nanmax(roi_activities)-(np.nanmin(roi_activities)))/10
                print ("activity",activity, " roi_activities",roi_activities)

                # activity will always be positive (PDA)
                # positions refers to either CEN position positions[0] or DMN position positions[1]
                print('Circle positions:', target_circles[0].pos[1], target_circles[1].pos[1])
                print ("direction -->", roi_names_list[i])
                print (roi_names_list[0],"hits: ",hit_counter[0], '   ', roi_names_list[1],"hits: ",hit_counter[1])
                direction = positions[i]

            # if the ball has passed the middle of either target circle, put position back to 0
            if further_than_circles(position=i, 
                circle_center=target_circles[i].pos[1], 
                ball_center=ball.pos[1]):

                # increment hig count
                hit_counter[i]=hit_counter[i]+1
                print('HIT', roi_names_list[i])
                ball.pos = (0,0)

                # for each hit, position of target circle moves away from the middle (up to a point)
                if np.abs(target_circles[i].pos[1]) + target_circles[i].radius + 0.1 < 1:
                    target_circles[i].pos=((target_circles[i].pos[0]*1.1), (target_circles[i].pos[1]*1.1))
                target_circles[i].fillColor='white'


        # Save info to outfile for each volume       
        with open(filename+'_roi_outputs.csv', 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            print(([frame, triggerClock.getTime(), roi_raw_activations[0], roi_raw_activations[1]]))
            stim_writer.writerow([frame, expInfo['scale_factor'], triggerClock.getTime(), triggerClock.getTime() + 1.2, roi_raw_activations[0], roi_raw_activations[1], 'feedback', hit_counter[0], hit_counter[1], pda_outlier, ball.pos[1], target_circles[0].pos[1], target_circles[1].pos[1]])   

        # Increment the frame
        frame += 1
    
    # calculate next ball position
    pause_ball_movement=False
    for i in range(n_roi):
        if further_than_circles(position=i, 
                    circle_center=target_circles[i].pos[1], 
                    ball_center=ball.pos[1]):
            pause_ball_movement=True

    if not pause_ball_movement:
        ball.pos = calculate_ball_position(circle_reference_position=direction, activation=activity, ball_x_position=ball.pos[0], ball_y_position=ball.pos[1], outlier=pda_outlier)             

    # Draw stimuli (if on feedback mode)
    if expInfo['feedback_on'] == 'Feedback':
        for i in range(n_roi):
            target_circles[i].draw()
        ball.draw()

        # flip window
        win.flip()

    # quit if escape pressed
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    

# END OF FEEDBACK LOOP
#########################################################
      
#------Prepare to start Routine "baseline"-------
t = 0
baselineClock.reset()  # clock 
frameN = -1
routineTimer.add(1.00000)
# update component parameters for each repeat
# keep track of which components have finished
baselineComponents = []
baselineComponents.append(text_2)
for thisComponent in baselineComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "baseline"-------
continueRoutine = True
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = baselineClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *text_2* updates
    if t >= 0.0 and text_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_2.tStart = t  # underestimates by a little under one frame
        text_2.frameNStart = frameN  # exact frame index
        text_2.setAutoDraw(True)
    if text_2.status == STARTED and t >= (0.0 + (1-win.monitorFramePeriod*0.75)): #most of one frame period left
        text_2.setAutoDraw(False)

# check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in baselineComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

# check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()

# refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "baseline"-------
for thisComponent in baselineComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
    
  
 
#------Prepare to start Routine "finish"-------
t = 0
finishClock.reset()  # clock 
frameN = -1
routineTimer.add(5.000000)
# update component parameters for each repeat
# keep track of which components have finished
finishComponents = []
finishComponents.append(text_5)
for thisComponent in finishComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# Ask slider questions
run_slider(question_text='How often were you using the mental noting practice?',
                left_label='Never', right_label='Always')
run_slider(question_text='How often did you check the position of the ball',
                left_label='Never', right_label='All the time')
run_slider(question_text='How difficult was it to apply mental noting?',
                left_label='Not at all', right_label='Very Difficult')
run_slider(question_text='How calm do you feel right now?',
                left_label='Not at all', right_label='Very calm')


#-------Start Routine "finish"-------
continueRoutine = True
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = finishClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_5* updates
    if t >= 0.0 and text_5.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_5.tStart = t  # underestimates by a little under one frame
        text_5.frameNStart = frameN  # exact frame index
        text_5.setAutoDraw(True)
    if text_5.status == STARTED and t >= (0.0 + (5-win.monitorFramePeriod*0.75)): #most of one frame period left
        text_5.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in finishComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "finish"-------
for thisComponent in finishComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

win.close()
start_next_run()



