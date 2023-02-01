#! /bin/bash
# Clemens Bauer
# Modified by Paul Bloom December 2022


## 4 ARGS: [subid] [ses] [run] [step]

#Step 1: disable wireless internet, set MURFI_SUBJECTS_DIR, and NAMEcd
#Step 2: receive 2 volume scan
#Step 3: create masks
#Step 4: run murfi for realtime

subj=$1
step=$2
ses='ses-lo1'
run='run-01'

# Set initial paths
subj_dir=../subjects/$subj
cwd=$(pwd)
absolute_path=$(dirname $cwd)
subj_dir_absolute="${absolute_path}/subjects/$subj"
fsl_scripts=../scripts/fsl_scripts


# Set template files
template_dmn='DMNax_brainmaskero2_lps.nii.gz'
template_cen='CENa_brainmaskero2_lps.nii.gz'

# Set paths & check that computers are properly connected with scanner via Ethernet
if [ ${step} = setup ]
then
    #clear
    echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    echo "+ Wellcome to MURFI real-time Neurofeedback"
    echo "+ running " ${step}
    export MURFI_SUBJECTS_DIR="${absolute_path}/subjects/"
    export MURFI_SUBJECT_NAME=$subj
    echo "+ subject ID: "$MURFI_SUBJECT_NAME
    echo "+ working dir: $MURFI_SUBJECTS_DIR"
    #echo "disabling wireless internet"
    #ifdown wlan0
    echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    echo "checking the presence of scanner and stim computer"
    ping -c 3 192.168.2.1
    ping -c 3 192.168.2.6
    echo "make sure Wi-Fi is off"
    echo "make sure you are Wired Connected to rt-fMRI"
    echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
fi  

# run MURFI for 2vol scan (to be used for registering masks to native space)  
if [ ${step} = 2vol ]
then
    clear
    echo "ready to receive 2 volume scan"
    singularity exec murfi2.sif murfi -f $subj_dir/xml/2vol.xml
fi

# For registering masks in MNI space to native space (based on 2vol scan)
if [ ${step} = register ]
then
    clear
    echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    echo "Registering masks to study_ref"
    echo "Ignore Flipping WARNINGS we need LPS/NEUROLOGICAL orientation for murfi feedback!!"
    latest_ref=$(ls -t $subj_dir/xfm/*.nii | head -n1)
    latest_ref="${latest_ref::-4}"
    echo ${latest_ref}
    bet ${latest_ref} ${latest_ref}_brain -R -f 0.4 -g 0 -m # changed from -f 0.6
    slices ${latest_ref}_brain ${latest_ref} -o $subj_dir/xfm/2vol_skullstrip_check.gif

    # CCCB version (direct flirt from subject functional to MNI structural: step 1)
    # because the images that we get from Prisma through Vsend are in LPS orientation we need to change both our MNI mean image and our mni masks accordingly: 
    #fslswapdim MNI152_T1_2mm.nii.gz x -y z MNI152_T1_2mm_LPS.nii.gz
    #fslorient -forceneurological MNI152_T1_2mm_LPS.nii.gz
    # once the images are in the same orientation we can do registration
    rm -r $subj_dir/xfm/epi2reg
    mkdir $subj_dir/xfm/epi2reg
    mkdir $subj_dir/mask/lps

    # warp MNI templates into native space
    flirt -in MNI152_T1_2mm_LPS.nii.gz -ref ${latest_ref} -out $subj_dir/xfm/epi2reg/mnilps2studyref -omat $subj_dir/xfm/epi2reg/mnilps2studyref.mat
    flirt -in MNI152_T1_2mm_LPS_brain.nii.gz -ref ${latest_ref}_brain -out $subj_dir/xfm/epi2reg/mnilps2studyref_brain -omat $subj_dir/xfm/epi2reg/mnilps2studyref.mat

    # make registration image for inspection, and open it
    slices $subj_dir/xfm/epi2reg/mnilps2studyref_brain ${latest_ref}_brain -o $subj_dir/xfm/MNI2_warp_to_2vol_native_check.gif

    # If paths to personalized masks exist, then run MURFI. Otherwise, prompt user about whether to use template masks instead
    dmn_mni_thresh="../subjects/${subj}/mask/mni/dmn_mni.nii.gz"
    cen_mni_thresh="../subjects/${subj}/mask/mni/cen_mni.nii.gz"   
    if [ -f "${dmn_mni_thresh}" ] && [ -f "${cen_mni_thresh}" ];
    then
        echo 'Found DMN & CEN MNI masks'
    else 
        # If the user wants, use standard DMN & CEN templates for feedback
        if zenity --question --text="Continue using standard DMN &amp; CEN templates instead?" \
            --width=800 --title="Warning, no masks found for ${subj}!"
        then
            cp $template_dmn $dmn_mni_thresh
            cp $template_cen $cen_mni_thresh
        else
            exit 0
        fi
    fi

    # For each mask (MNI), swap dimension & register to 2vol native space
    for mask_name in {dmn,cen};
    do 
        echo "+ REGISTERING ${mask_name} TO study_ref" 
        #fslswapdim $subj_dir/mask/mni/${mask_name}_mni x -y z $subj_dir/mask/lps/${mask_name}_mni_lps
        #fslorient -forceneurological $subj_dir/mask/lps/${mask_name}_mni_lps
        
        #start registration
        flirt -in $subj_dir/mask/lps/${mask_name}_mni_lps -ref ${latest_ref} -out $subj_dir/mask/${mask_name} -init $subj_dir/xfm/epi2reg/mnilps2studyref.mat -applyxfm -interp nearestneighbour -datatype short
        fslmaths $subj_dir/mask/${mask_name}.nii.gz -mul ${latest_ref}_brain_mask $subj_dir/mask/${mask_name}.nii.gz -odt short

        # erode each mask one voxel
        #fslmaths $subj_dir/mask/${mask_name}.nii.gz -ero $subj_dir/mask/${mask_name}.nii.gz 
        gunzip -f $subj_dir/mask/${mask_name}.nii.gz
    done

    echo "+ INSPECT"
    echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    xdg-open $subj_dir/xfm/MNI2_warp_to_2vol_native_check.gif
    fsleyes ${latest_ref}_brain  $subj_dir/mask/cen.nii -cm red $subj_dir/mask/dmn.nii -cm blue  #$subj_dir/mask/smc.nii -cm yellow $subj_dir/mask/stg.nii -cm green
fi

if  [ ${step} = feedback ]
then
clear
    echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    echo "ready to receive rtdmn feedback scan"
    export MURFI_SUBJECTS_DIR="${absolute_path}/subjects/"
    export MURFI_SUBJECT_NAME=$subj 

    singularity exec murfi2.sif murfi -f $subj_dir_absolute/xml/rtdmn.xml
fi


if  [ ${step} = resting_state ]
then
clear
    echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    echo "ready to receive resting state scan"
    export MURFI_SUBJECTS_DIR="${absolute_path}/subjects/"
    export MURFI_SUBJECT_NAME=$subj
    singularity exec murfi2.sif murfi -f $subj_dir/xml/rest.xml

fi



if  [ ${step} = extract_rs_networks ]
then
clear
    echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    echo "+ compiling resting state run into analysis folder"

    expected_volumes=249
    # # get all volumes of resting data (no matter how many) merged into 1 .nii.gz file
    # run_0_volumes=$(find ../subjects/${subj}/img/ -name "img-00000*" | wc -l)
    # run_1_volumes=$(find ../subjects/${subj}/img/ -name "img-00001*" | wc -l)

    # if [ ${run_0_volumes} -eq 250 ] && [ ${run_1_volumes} -eq 250 ];
    # then
    #     rest_runA_num=0
    #     rest_runB_num=1
    #else
    runstring="Resting state runs should have ${expected_volumes} volumes\n"
    for i in {0..10};
    do
        # Because of MURFI file-naming conventions, do not use the first volume!
        run_volumes=$(find ${subj_dir_absolute}/img/ -type f \( -iname "img-0000${i}*" ! -iname "*00001.nii" \) | wc -l)
        if [ ${run_volumes} -ne 0 ]
        then
            runstring="${runstring}\nRun ${i}: ${run_volumes} volumes"
        fi
    done

    # use zenity to allow user to choose which resting volume to use (and how many runs to use)
    input_string=$(zenity --forms --title="Which resting state runs to use for ICA?" \
        --separator=" " --width 600 --height 600 \
        --add-entry="First Input Run #" \
        --add-entry="Second Input Run #" --text="`printf "${runstring}"`"\
        --add-combo="How many resting runs to use for ICA?\nOnly use runs that have 200+ volumes for ICA?" --combo-values "2 (default) |1 (only to be used if there aren't 2 viable runs to use)")

    # check that exit button hasn't been clicked
    if [[ $? == 1 ]];
    then
        exit 0
    fi

    # parse zenity output using space as delimiter
    read -a input_array <<< $input_string
    rest_runA_num=${input_array[0]}
    rest_runB_num=${input_array[1]}

    # Use 2 resting runs for ICA
    echo ${input_array[2]}
    if [[ ${input_array[2]} == '2' ]] ;
    then
        template_fsf_file=fsl_scripts/rest_template.fsf
        echo "Using run ${rest_runA_num} and run ${rest_runB_num}"

        # merge individual volumes to make 1 file for each resting state run
        rest_runA_filename=$subj_dir_absolute/rest/$subj'_'$ses'_task-rest_run-01_bold'.nii.gz
        rest_runB_filename=$subj_dir_absolute/rest/$subj'_'$ses'_task-rest_run-02_bold'.nii.gz 


        #fslmerge -tr $rest_runA_filename $subj_dir_absolute/img/img-0000${rest_runA_num}* 1.2
        #fslmerge -tr $rest_runB_filename $subj_dir_absolute/img/img-0000${rest_runB_num}* 1.2

        volsA=$(find ${subj_dir_absolute}/img/ -type f \( -iname "img-0000${rest_runA_num}*" ! -iname "*00001.nii" \))
        volsB=$(find ${subj_dir_absolute}/img/ -type f \( -iname "img-0000${rest_runB_num}*" ! -iname "*00001.nii" \)) 
        fslmerge -tr $rest_runA_filename $volsA 1.2
        fslmerge -tr $rest_runB_filename $volsB 1.2

        # Re-orient to neurological (will be LPS from VSend)
        #fslswapdim $rest_runA_filename x -y z $rest_runA_filename
        #fslswapdim $rest_runB_filename x -y z $rest_runB_filename
        #fslorient -forceneurological $rest_runA_filename
        #fslorient -forceneurological $rest_runB_filename

        # figure out how many volumes of resting state data there were to be used in ICA
        rest_runA_volumes=$(fslnvols $rest_runA_filename)
        rest_runB_volumes=$(fslnvols $rest_runB_filename)
        if [ ${rest_runA_volumes} -ne ${expected_volumes} ] || [ ${rest_runB_volumes} -ne ${expected_volumes} ]; 
        then
            echo "WARNING! ${rest_runA_volumes} volumes of resting-state data found for run 1."
            echo "${rest_runB_volumes} volumes of resting-state data found for run 2. ${expected_volumes} expected?"

            # calculate minimum volumes (which run has fewer, then use fslroi to cut both runs to this minimum)
            minvols=$(( rest_runA_volumes < rest_runB_volumes ? rest_runA_volumes : rest_runB_volumes ))
            fslroi $rest_runA_filename $rest_runA_filename 0 $minvols
            fslroi $rest_runB_filename $rest_runB_filename 0 $minvols
            echo "Clipping runs so that both have ${minvols} volumes"
        else
            minvols=$expected_volumes
        fi

        echo "+ computing resting state networks this will take about 25 minutes"
        echo "+ started at: $(date)"
        
        # update FEAT template with paths and # of volumes of resting state run
        cp $fsl_scripts/rest_template.fsf $subj_dir_absolute/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf
        #DATA_path=$subj_dir/rest/$subj'_'$ses'_task-rest_'$run'_bold'.nii.gz
        OUTPUT_dir=$subj_dir_absolute/rest/rs_network
        sed -i "s#DATA1#$rest_runA_filename#g" $subj_dir_absolute/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf
        sed -i "s#DATA2#$rest_runB_filename#g" $subj_dir_absolute/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf
        sed -i "s#OUTPUT#$OUTPUT_dir#g" $subj_dir/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf

        # update fsf to match number of rest volumes
        sed -i "s/set fmri(npts) 250/set fmri(npts) ${minvols}/g" $subj_dir_absolute/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf
        feat $subj_dir/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf        
    else
        # Use just a single run for ICA (only to be used when 2 isn't viable)
        template_fsf_file=fsl_scripts/rest_template_single_run.fsf
        echo "Using run ${rest_runA_num} for single-run ICA"

        # merge individual volumes to make 1 file for each resting state run
        rest_runA_filename=$subj_dir_absolute/rest/$subj'_'$ses'_task-rest_run-01_bold'.nii.gz
        fslmerge -tr $rest_runA_filename $subj_dir_absolute/img/img-0000${rest_runA_num}* 1.2
        # Re-orient to neurological (will be LPS from VSend)
        #fslswapdim $rest_runA_filename x -y z $rest_runA_filename
        #fslorient -forceneurological $rest_runA_filename

        # figure out how many volumes of resting state data there were to be used in ICA
        rest_runA_volumes=$(fslnvols $rest_runA_filename)
        echo "${rest_runA_volumes} volumes of resting-state data found for run 1."
        echo "+ computing resting state networks this will take about 25 minutes"
        echo "+ started at: $(date)"
        
        # update FEAT template with paths and # of volumes of resting state run
        cp $template_fsf_file $subj_dir_absolute/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf
        #DATA_path=$subj_dir/rest/$subj'_'$ses'_task-rest_'$run'_bold'.nii.gz
        OUTPUT_dir=$subj_dir_absolute/rest/rs_network
        sed -i "s#DATA#$rest_runA_filename#g" $subj_dir_absolute/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf
        sed -i "s#OUTPUT#$OUTPUT_dir#g" $subj_dir/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf

        # update fsf to match number of rest volumes
        sed -i "s/set fmri(npts) 250/set fmri(npts) ${rest_runA_volumes}/g" $subj_dir_absolute/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf
        feat $subj_dir/rest/$subj'_'$ses'_task-rest_'$run'_bold'.fsf   
    fi                        
fi



if [ ${step} = process_roi_masks ]
then
clear
    echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    echo "+ Generating DMN & CEN Masks "
    echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    

# Set up file paths needed for mask creation

## File to contain spatial correlations between ICs & template networks

# first look for ICA feat directory based on multiple runs (.gica directory)
ica_directory=$subj_dir/rest/rs_network.gica/groupmelodic.ica/

if [ -d $ica_directory ]
then
    ica_version='multi_run'

# if ICA feat dir for multi-run ICA isn't present, look for single-run version
elif [ -d "${subj_dir}/rest/rs_network.ica/filtered_func_data.ica/" ] 
then
    ica_directory="${subj_dir}/rest/rs_network.ica/" 
    ica_version='single_run'
else
    echo "Error: no ICA directory found for ${subj}. Exiting now..."
    exit 0
fi
correlfile=$ica_directory/template_rsn_correlations_with_ICs.txt
touch ${correlfile}

template_networks='template_networks.nii.gz'

# Merge template files to 1 image
fslmerge -tr ${template_networks} ${template_dmn} ${template_cen} 1

echo $ica_version



# If single-session, then ICA was done in native space, and registration is needed
if [ $ica_version == 'single_run' ]
then
    # ICs in native space
    infile=$ica_directory/filtered_func_data.ica/melodic_IC.nii.gz 
    # ICA file, template, and transform matrices needed for registration
    examplefunc=${ica_directory}/reg/example_func.nii.gz
    standard=${ica_directory}/reg/standard.nii.gz
    example_func2standard_mat=${ica_directory}/reg/example_func2standard.mat
    standard2example_func_mat=${ica_directory}/reg/standard2example_func.mat

    # Warp template to native space (based on the resting state data used for ICA)
    template2example_func=${ica_directory}/reg/template_networks2example_func.nii.gz
    flirt -in ${template_networks} -ref ${examplefunc} -out ${template2example_func} -init ${standard2example_func_mat} -applyxfm

    # Set paths for files needed for the next few steps 
    ## Unthresholded masks in native space
    dmn_uthresh=$ica_directory/dmn_uthresh.nii.gz
    cen_uthresh=$ica_directory/cen_uthresh.nii.gz

    # Correlate (spatially) ICA components (not thresholded) with DMN & CEN template files
    fslcc --noabs -p 3 -t -1 ${infile} ${template2example_func} >>${correlfile}
else
    # ICs in template space
    infile=$ica_directory/melodic_IC.nii.gz 
    # Correlate (spatially) ICA components (not thresholded) with DMN & CEN template files
    fslcc --noabs -p 3 -t -1 ${infile} ${template_networks} >>${correlfile}
fi



# Split ICs to separate files
split_outfile=$ica_directory/melodic_IC_
fslsplit ${infile} ${split_outfile}

# Selection of ICs most highly correlated with template networks
python rsn_get.py ${subj} ${ica_version}


## Unthresholded masks in mni space
dmn_mni_uthresh=$ica_directory/dmn_mni_uthresh.nii.gz
cen_mni_uthresh=$ica_directory/cen_mni_uthresh.nii.gz

## Thresholded masks in MNI space
dmn_mni_thresh=$ica_directory/dmn_mni_thresh.nii.gz
cen_mni_thresh=$ica_directory/cen_mni_thresh.nii.gz


# Hard code the number of voxels desired for each mask
num_voxels_desired=2000

# If single-run ICA, register non-thresholded masks to MNI space
if [ $ica_version == 'single_run' ]
then
    flirt -in  ${dmn_uthresh} -ref ${standard} -out ${dmn_mni_uthresh} -init ${example_func2standard_mat} -applyxfm
    flirt -in  ${cen_uthresh} -ref ${standard} -out ${cen_mni_uthresh} -init ${example_func2standard_mat} -applyxfm
fi

# Everything from here to the end of this step is in template space

# zero out voxels not included in the template masks (i.e. so we only select voxels within template DMN/CEN)
fslmaths ${dmn_mni_uthresh} -mul ${template_dmn} ${dmn_mni_uthresh}
fslmaths ${cen_mni_uthresh} -mul ${template_cen} ${cen_mni_uthresh}


# get number of non-zero voxels in masks, calculate percentile cutofff needed for the desired absolute number of voxels
voxels_in_dmn=$(fslstats ${dmn_mni_uthresh} -V | awk '{print $1}')
percentile_dmn=$(python -c "print(100*(1-${num_voxels_desired}/${voxels_in_dmn}))")
voxels_in_cen=$(fslstats ${cen_mni_uthresh} -V | awk '{print $1}')
percentile_cen=$(python -c "print(100*(1-${num_voxels_desired}/${voxels_in_cen}))")


# get threshold based on percentile
dmn_thresh_value=$(fslstats ${dmn_mni_uthresh} -P ${percentile_dmn})
cen_thresh_value=$(fslstats ${cen_mni_uthresh} -P ${percentile_cen})

# threshold masks in MNI space
fslmaths ${dmn_mni_uthresh} -thr ${dmn_thresh_value} -bin ${dmn_mni_thresh} -odt short
fslmaths ${cen_mni_uthresh} -thr ${cen_thresh_value} -bin ${cen_mni_thresh} -odt short

echo "Number of voxels in dmn mask: $(fslstats ${dmn_mni_thresh} -V)"
echo "Number of voxels in cen mask: $(fslstats ${cen_mni_thresh} -V)"

# copy masks to participant's mask directory
cp ${dmn_mni_thresh} ${subj_dir}/mask/mni/dmn_mni.nii.gz
cp ${cen_mni_thresh} ${subj_dir}/mask/mni/cen_mni.nii.gz


# Display masks with FSLEYES
fsleyes  mean_brain.nii.gz ${dmn_mni_thresh} -cm blue ${cen_mni_thresh} -cm red

fi


if [ ${step} = process_roi_masks_native ]
then
    clear
        echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        echo "+ Generating DMN & CEN Masks "
        echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        

    # Set up file paths needed for mask creation

    ## File to contain spatial correlations between ICs & template networks

    # first look for ICA feat directory based on multiple runs (.gica directory)
    ica_directory=$subj_dir/rest/rs_network.gica/groupmelodic.ica/

    if [ -d $ica_directory ]
    then
        ica_version='multi_run'

    # if ICA feat dir for multi-run ICA isn't present, look for single-run version
    elif [ -d "${subj_dir}/rest/rs_network.ica/filtered_func_data.ica/" ] 
    then
        ica_directory="${subj_dir}/rest/rs_network.ica/" 
        ica_version='single_run'
    else
        echo "Error: no ICA directory found for ${subj}. Exiting now..."
        exit 0
    fi
    correlfile=$ica_directory/template_rsn_correlations_with_ICs.txt
    touch ${correlfile}

    template_networks='template_networks.nii.gz'

    # Merge template files to 1 image
    fslmerge -tr ${template_networks} ${template_dmn} ${template_cen} 1

    echo $ica_version



    # If single-session, then ICA was done in native space, and registration is needed
    if [ $ica_version == 'single_run' ]
    then
        # ICs in native space
        infile=$ica_directory/filtered_func_data.ica/melodic_IC.nii.gz 
        # ICA file, template, and transform matrices needed for registration
        examplefunc=${ica_directory}/reg/example_func.nii.gz
        standard=${ica_directory}/reg/standard.nii.gz
        example_func2standard_mat=${ica_directory}/reg/example_func2standard.mat
        standard2example_func_mat=${ica_directory}/reg/standard2example_func.mat

        # Warp template to native space (based on the resting state data used for ICA)
        template2example_func=${ica_directory}/reg/template_networks2example_func.nii.gz
        dmn2example_func=${ica_directory}/reg/template_dmn2example_func.nii.gz
        cen2example_func=${ica_directory}/reg/template_cen2example_func.nii.gz
        flirt -in ${template_networks} -ref ${examplefunc} -out ${template2example_func} -init ${standard2example_func_mat} -applyxfm
        flirt -in ${template_dmn} -ref ${examplefunc} -out ${dmn2example_func} -init ${standard2example_func_mat} -applyxfm
        flirt -in ${template_cen} -ref ${examplefunc} -out ${cen2example_func} -init ${standard2example_func_mat} -applyxfm


        # Set paths for files needed for the next few steps 
        ## Unthresholded masks in native space
        dmn_uthresh=$ica_directory/dmn_uthresh.nii.gz
        cen_uthresh=$ica_directory/cen_uthresh.nii.gz

        # Correlate (spatially) ICA components (not thresholded) with DMN & CEN template files
        fslcc --noabs -p 3 -t -1 ${infile} ${template2example_func} >>${correlfile}
    else
        # ICs in template space
        infile=$ica_directory/melodic_IC.nii.gz 
        # Correlate (spatially) ICA components (not thresholded) with DMN & CEN template files
        fslcc --noabs -p 3 -t -1 ${infile} ${template_networks} >>${correlfile}
    fi



    # Split ICs to separate files
    split_outfile=$ica_directory/melodic_IC_
    fslsplit ${infile} ${split_outfile}

    # Selection of ICs most highly correlated with template networks
    python rsn_get.py ${subj} ${ica_version}


    ## Unthresholded masks in mni space
    dmn_mni_uthresh=$ica_directory/dmn_mni_uthresh.nii.gz
    cen_mni_uthresh=$ica_directory/cen_mni_uthresh.nii.gz

    ## Thresholded masks in MNI space
    dmn_thresh=$ica_directory/dmn_hresh.nii.gz
    cen_thresh=$ica_directory/cen_thresh.nii.gz


    # Hard code the number of voxels desired for each mask
    num_voxels_desired=2000

    # If single-run ICA, register non-thresholded masks to MNI space
    #if [ $ica_version == 'single_run' ]
    #then
    #    flirt -in  ${dmn_uthresh} -ref ${standard} -out ${dmn_mni_uthresh} -init ${example_func2standard_mat} -applyxfm
    #    flirt -in  ${cen_uthresh} -ref ${standard} -out ${cen_mni_uthresh} -init ${example_func2standard_mat} -applyxfm
    #fi

    # Everything from here to the end of this step is in template space

    # zero out voxels not included in the template masks (i.e. so we only select voxels within template DMN/CEN)
    fslmaths ${dmn_uthresh} -mul ${dmn2example_func} ${dmn_uthresh}
    fslmaths ${cen_uthresh} -mul ${cen2example_func} ${cen_uthresh}


    # get number of non-zero voxels in masks, calculate percentile cutofff needed for the desired absolute number of voxels
    voxels_in_dmn=$(fslstats ${dmn_uthresh} -V | awk '{print $1}')
    percentile_dmn=$(python -c "print(100*(1-${num_voxels_desired}/${voxels_in_dmn}))")
    voxels_in_cen=$(fslstats ${cen_uthresh} -V | awk '{print $1}')
    percentile_cen=$(python -c "print(100*(1-${num_voxels_desired}/${voxels_in_cen}))")


    # get threshold based on percentile
    dmn_thresh_value=$(fslstats ${dmn_uthresh} -P ${percentile_dmn})
    cen_thresh_value=$(fslstats ${cen_uthresh} -P ${percentile_cen})

    echo $dmn_thresh_value

    # threshold masks in MNI space
    fslmaths ${dmn_uthresh} -thr ${dmn_thresh_value} -bin ${dmn_thresh} -odt short
    fslmaths ${cen_uthresh} -thr ${cen_thresh_value} -bin ${cen_thresh} -odt short

    echo "Number of voxels in dmn mask: $(fslstats ${dmn_thresh} -V)"
    echo "Number of voxels in cen mask: $(fslstats ${cen_thresh} -V)"

    # copy masks to participant's mask directory
    cp ${dmn_thresh} ${subj_dir}/mask/dmn_native_rest.nii.gz
    cp ${cen_thresh} ${subj_dir}/mask/cen_native_rest.nii.gz


    # Display masks with FSLEYES
    fsleyes  ${ica_directory}/mean_func.nii.gz ${dmn_thresh} -cm blue ${cen_thresh} -cm red

fi



