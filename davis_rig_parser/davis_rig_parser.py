#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 14:27:01 2019

@author: bradly
"""
# =============================================================================
# Import stuff
# =============================================================================

# import Libraries
# Built-in Python libraries
import os # functions for interacting w operating system

# 3rd-party libraries
import numpy as np # module for low-level scientific computing
import easygui
import pandas as pd
import itertools
import glob
from datetime import date
from datetime import datetime, timedelta
# =============================================================================
# =============================================================================
# # #DEFINE ALL FUNCTIONS
# =============================================================================
# =============================================================================
#Assign day is a work in progress ---- No documentation yet
def assign_day(df):
    #uses a date column to assign a day column
    groups = []
    for name, group in df.groupby(['Animal']):
        mindate = min(df['Date'])
        group['Day'] = [(x).days + 1 for x in (group['Date'] - mindate)]
        groups.append(group)
    return pd.concat(groups)

def assign_time(df):

    # Update the Time column
    for i in range(len(df) - 1):
        if i>0:
            current_time = convert_to_datetime(df.at[i-1, 'Time'])
        else:
            current_time = convert_to_datetime(df.at[i, 'Time'])
        latency = (df.at[i, 'Latency'])/1000
        ipi = df.at[i, 'IPI']
        if i > 0:
            tri_len = df.at[i-1, 'LENGTH']
        else:
            tri_len = 0

        new_time = add_seconds_to_time(current_time, round(latency + ipi + tri_len))
        df.at[i, 'Time'] = new_time.strftime('%H:%M:%S')

    return df
# Function to convert time string to datetime object
def convert_to_datetime(time_str):
    return datetime.strptime(time_str, '%H:%M:%S')
# Function to add seconds to datetime object
def add_seconds_to_time(time_obj, seconds):
    return time_obj + timedelta(seconds=seconds)
def calculate_lick_rates(ili_list, bout_pause=300):
    if len(ili_list)==0:  # Check for empty list
        return [0]

    bouts = []
    current_bout = []

    for ili in ili_list:
        if ili >= 300:
            # End of a bout, calculate rate and start a new bout
            if current_bout:
                bouts.append((len(current_bout)+1)/ (sum(current_bout)/1000))
            current_bout = []
        else:
            current_bout.append(ili)

    # Handle the last bout
    if current_bout:
        bouts.append((len(current_bout)+1)/ (sum(current_bout)/1000))
        
    return bouts if bouts else [0]  # Return [0] if no bouts found

#Define a padding function
def boolean_indexing(v, fillval=np.nan):
    lens = np.array([len(item) for item in v])
    mask = lens[:,None] > np.arange(lens.max())
    out = np.full(mask.shape,fillval)
    out[mask] = np.concatenate(v)
    #if this function ouputs 
    #*** ValueError: could not convert string to float:
    #that means there is a comma without a value after it like
    #     1
    #     2
    # --> 3,
    #     4
    #     5
    #in the ILI section below the columns in the .txt files
    return out

#Define consecutive sequence finder
def ranges(nums):
    nums = sorted(set(nums))
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s+1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))

def MedMS8_reader_stone(file_name, file_check, min_latency=100, min_ILI=75, filter_false_licks=True):
    """
    Input: File Name (with directory) from MedAssociates Davis Rig (e.g. .ms8.text)
    
    Output: Dictionary containing a dataframe (all lick data categorized), file
            information (animal name, date of recording, etc), and a matrix
            with all latencies between licks by trial
            
    This function processes the raw data file from the Davis Rig/BAT rig and prepares it for further 
    analysis. It extracts relevant metadata, organizes lick data, and processes inter-lick
    intervals (ILIs).
    
    
    if scan for ghost licks is true, the following logic to eliminate artifacts
    will be implemented:
        For each trial: if the latency is less than 100ms, we consider this impossible
        as the rat can't react faster than 100ms (or min latency) to the sshutter opening. So, it must
        be that the "first lick" is actually the shutter opening. 
        So, I will add up the first ili to the latency and make that the true latency, and
        then make the 2nd ili the true first ili.
        Then flat out delete all ilis that are lower than the min_ILI
    

    """
    file_input = open(file_name)
    lines = file_input.readlines()

	#Create dictionary for desired file into
    Detail_Dict = {'FileName': None,\
                   'StartDate': None,\
				   'StartTime': None,\
				   'Animal': None,\
				   'Condition': None,\
				   'MaxWait': None,\
				   'Trials': None,\
				   'LickDF': None,\
				   'LatencyMatrix': None}
	
	#Extract file name and store
    Detail_Dict['FileName'] = file_name[file_name.rfind('/')+1:]

	#Store details in dictionary and construct dataframe	
    for i in range(len(lines)):
        if "Start Date" in lines[i]:
            Detail_Dict['StartDate'] = lines[i].split(',')[-1][:-1].strip()
        if "Start Time" in lines[i]:
            Detail_Dict['StartTime'] = lines[i].split(',')[-1][:-1]
        if "Animal ID" in lines[i]:
            Detail_Dict['Animal'] = lines[i].split(',')[-1][:-1]		
        if "Max Wait" in lines[i]:
            Detail_Dict['MaxWait'] = lines[i].split(',')[-1][:-1]			
        if "Max Number" in lines[i]:
            Detail_Dict['Trials'] = lines[i].split(',')[-1][:-1]			
        if "PRESENTATION" and "TUBE" in lines[i]:		
            ID_line = i
        if len(lines[i].strip()) == 0:		
            Trial_data_stop = i		
            if ID_line > 0 and Trial_data_stop > 0:

                #Create dataframe
                df = pd.DataFrame(columns=lines[ID_line].split(','),\
                                  data=[row.split(',') for row in \
                                        lines[ID_line+1:Trial_data_stop]])
               #raise ValueError
                #Remove spaces in column headers (caused by split)
                df.columns = df.columns.str.replace(' ', '')

                df.Latency = df.Latency.astype(float)
                df.IPI = df.IPI.astype(float)
                df.LENGTH = df.LENGTH.astype(float)
                df['StartTime'] = Detail_Dict['StartTime'] 
                #the assing time function uses an existing 'Time', 'Length' coluumn to add to
                df['Time'] = Detail_Dict['StartTime'] 

                #and make Time a string
                df.Time = df.Time.astype(str).str.strip()
                df.IPI = df.IPI.astype(float)

                df = assign_time(df)

                #The rig (occassionally) introduces a "ghost lick" whereby the shutter,
                #in and of itself registers a "lick" at an impossible ILI. For this reason
                #we will screen out ANY lick that occurs <min_latency
                first_lat = df['Latency']
                lat_set = boolean_indexing([row.split(',')\
                                 for row in lines[Trial_data_stop+1:]])

                #add first latency into larger extracted matrix
                #the first col of the matrix is PRESENTATION, the second is Latency, and the rest are the ILIs
                lat_set = np.insert(lat_set,1,np.asarray(first_lat),axis=1)
                lat_set = np.nan_to_num(lat_set)
                #the following lines will apply the filtering logic detailed in the 
                #function's docstring
                if filter_false_licks:
                    # First, store the first column in a variable called "presentations"
                    presentations = lat_set[:, 0]
                    # Then, remove the first column from lat_set
                    lat_set = np.delete(lat_set, 0, 1)
                    #for every row do the following of "lat_set", while the first
                    #entry is less than min_lat, the first row becomes the sum of the
                    #first entry and the second entry and all of the entries above
                    #the 1st shift to the left 1 place and the leftover rightmost
                    #entry becomes 0
                    cut_time = []
                    cutslist = []
                    for row in lat_set:
                        if len(row) < 2:
                            cutslist.append(0)
                            cut_time.append(0)
                            continue
                        cuts=0
                        if len(row) > 1:
                            cut_t = 0
                            while row[0] < min_latency:
                                cut_t += row[1] #total time cut from the trial in ms
                                row[0] = row[0] + row[1]
                                row[1:-1] = row[2:]
                                row[-1] = 0
                                cuts +=1
                                if cuts > len(row): #failsafe so the loop doesn't go infinite
                                    row[0] = np.nan
                                    break
                            #then, set all ILIs under min_ILI to 0 to be deleted later
                            for j in range(1, len(row)):
                                if row[j] < min_ILI and row[j] != 0:
                                    row[j] = 0
                                    cuts+=1
                        cutslist.append(cuts)
                        cut_time.append(cut_t)
                    #unite presentations and the rest of the ilis once again
                    lat_set = np.column_stack((presentations, lat_set))
                else:
                    cutslist = [0]*len(df['PRESENTATION'])
                    cut_time = [0]*len(df['PRESENTATION'])
                #cutslist is a list of deleted ilis for each presentation in the form
                #[[x deleted for pres 1], [y for pres 2], [z for pres 3] ..... ]
                    
                #flip through corrected matrix and remove the flagged ilis
                trimmed_set = [np.asarray([x for x in y if x != 0]) for y in lat_set]
                long_trial = max([len(x) for x in trimmed_set])
                padded_set = [x if len(x) == long_trial else\
                             np.hstack([x,np.zeros(long_trial-len(x))]) for x in trimmed_set ]
                padded_set = np.asarray(padded_set)
                padded_set[padded_set==0] = np.nan

                #count non-nan by row
                lick_set = [(~np.isnan(a)).sum(0) for a in padded_set[:,1:]]
                df['TriLength'] = [x/1000 for x in cut_time]
                #take out the amount of cuts from the licks
                df['LICKS'] = df['LICKS'].astype(int) - pd.Series(cutslist)
                #make any entry less than 0 equal to 0 instead
                df['LICKS'] = df['LICKS'].clip(lower=0)
                
                #raise ValueError
                #update the datarame to hold the fixed data
                df['Latency'] = padded_set[:,1]
                
                #remove the first latency from fixed matrtix
                padded_set = np.delete(padded_set, 1, 1)
                
                #Set concentrations to 0 if concentration column blank
                df['CONCENTRATION']=df['CONCENTRATION'].str.strip()
                df['CONCENTRATION'] = df['CONCENTRATION'].apply(lambda x: 0 if x == '' else x)

                #Convert specific columns to numeric
                df["SOLUTION"] = df["SOLUTION"].str.strip()
                df[["PRESENTATION","TUBE","LICKS","Latency"]] = \
                    df[["PRESENTATION","TUBE","LICKS","Latency"]].apply(pd.to_numeric)

                df['CONCENTRATION'] = pd.to_numeric(df['CONCENTRATION'], errors='coerce').fillna(df['CONCENTRATION'])
                
                #Add in identifier columns
                df.insert(loc=0, column='Animal', value=Detail_Dict['Animal'])
                df.insert(loc=0, column='Date', value=Detail_Dict['StartDate'])
                df.insert(loc=3, column='Trial_num', value='')
                df['Trial_num'] = df.groupby('TUBE').cumcount()+1

                #convert the dates to datetime
                df['Date'] =  pd.to_datetime(df['Date'], format='%Y/%m/%d')
                
                #Store in dataframe
                Detail_Dict['LickDF'] = df		

                #Grab all ILI data, pad with NaNs to make even matrix
                #Store in dictionary (TrialXILI count)
                Detail_Dict['LatencyMatrix'] = padded_set[:,:max(lick_set)]
    
	#Add column if 'Retries' Column does not exist
    if 'Retries' not in df:   
        df.insert(df.columns.get_loc("Latency")+1,'Retries', '      0')
		
		
    #Check if user has data sheet of study details to add to dataframe
    if len(file_check) != 0:

        detail_df=pd.read_csv(file_check[0], header=0,sep='\t')

        #Check data with detail sheeet
        detail_row = np.array(np.where(detail_df.Date==Detail_Dict['StartDate'].strip()))
        for case in range(detail_row.shape[1]):
            if detail_df.Notes[detail_row[:,case][0]].lower() in \
                Detail_Dict['FileName'][Detail_Dict['FileName'].rfind('_')+1:].lower()\
                and detail_df.Animal[detail_row[:,case][0]] in Detail_Dict['Animal']:
                
                    
                #Add details to dataframe    
                df.insert(loc=1, column='Notes', \
                    value=detail_df.Notes[detail_row[:,case][0]].lower())
                detail_df['Condition'] = detail_df['Condition'].fillna('none')

                df.insert(loc=2, column='Condition', \
                    value=detail_df.Condition[detail_row[:,case][0]].lower())
                break
                
    if len(file_check) == 0:
        #Add blank columns
        df.insert(loc=1, column='Notes', value='')
        df.insert(loc=2, column='Condition', value='')

    return Detail_Dict	

def LickMicroStructure_stone(dFrame_lick,latency_array, bout_crit):
# =============================================================================
#     Function takes in the dataframe and latency matrix pertaining to all 
#     licking data obtained from MedMS8_reader_stone as the data sources. This 
#     requires a bout_crit 
#     
#     Input: 1) Dataframe and Licking Matrix (obtained from MedMS8_reader_stone)
#            2) Bout_crit; variable which is the time (ms) needed to pause between
#               licks to count as a bout (details in: Davis 1996 & Spector et al. 1998).
# 
#     Output: Appended dataframe with the licks within a bout/trial, latency to 
#             to first lick within trial    
# =============================================================================

    #Find where the last lick occured in each trial
    last_lick = list(map(lambda x: [i for i, x_ in enumerate(x) if not \
                                    np.isnan(x_)][-1], latency_array))
    
    #Create function to search rows of matrix avoiding 'runtime error' caused by Nans
    crit_nan_search = np.frompyfunc(lambda x: (~np.isnan(x)) & (x >=bout_crit), 1, 1)
    i = 0
    #Create empty list to store number of bouts by trial
    bouts = []; ILIs_win_bouts = []
    for i in range(latency_array.shape[0]):
        #Create condition if animal never licks within trial
        if last_lick[i] == 0:
            bouts.append(last_lick[i])
            ILIs_win_bouts.append(last_lick[i])
            
        else:
            bout_pos = np.where(np.array(crit_nan_search(latency_array[i,:])).astype(int))
            
            #Insert the start number or row to get accurate count
            bout_pos = np.insert(bout_pos,0,0)  # inserting at the start
            
            #Caclulate bout duration
            bout_dur = np.diff(bout_pos) 

    
            #Flip through all bouts and calculate licks between and store
            if last_lick[i] != bout_pos[-1]:
                #Insert the last lick row to get accurate count
                bout_pos = np.insert(bout_pos, len(bout_pos), last_lick[i])
                        
                #Calculate bout duration
                bout_dur = np.diff(bout_pos) 
                    
            #Append the time diff between bouts to list (each number symbolizes a lick)
            bouts.append(np.array(bout_dur))                
        
            #Grab all ILIs within bouts and store
            trial_ILIs = []

            # Handle the ILIs
            for lick in range(len(bout_pos)):
                # For the first bout, include the second ILI (index 1)
                if lick == 0:
                    start_index = 1
                else:
                    start_index = bout_pos[lick - 1] + 1 # +1 to get the ILI after the bout
            
                end_index = bout_pos[lick] + 1 if lick < len(bout_pos) else None # +1 to include the last ILI in the bout
                
                # Ensure indices are within the valid range
                if start_index < latency_array.shape[1] and (end_index is None or end_index <= latency_array.shape[1]):
                    trial_ILIs.append(list(latency_array[i, start_index : end_index]))
            
            ILIs_win_bouts.append(trial_ILIs)
    #convert the data from arrays to lists because I like them better
    # ILIs_win_bouts = [list(item) for item in ILIs_win_bouts]
    #Store bout count into dframe
    #do a quality of life filter
    ILIs_win_bouts = [[] if x == 0 else x[1:] for x in ILIs_win_bouts]
    dFrame_lick["Bouts"] = bouts
    dFrame_lick["ILIs"] = ILIs_win_bouts        
    if latency_array.shape[1] <= 1:
        dFrame_lick["Lat_First"] = np.nan
    else:
        # Handle the case when the array doesn't have enough columns
        dFrame_lick["Lat_First"] = latency_array[:, 1]
    return dFrame_lick	    

# =============================================================================
# =============================================================================
# # IMPORTANT FUNCTION
# =============================================================================
# =============================================================================

def create_df(dir_name="ask", info_name='ask', bout_pause=300, min_latency=100, min_ILI=75, save_df=True):
    asked = False
    if dir_name=="ask":
        dir_name = easygui.diropenbox()
    os.chdir(dir_name)
    if info_name == 'ask':
        info_name = easygui.diropenbox(msg='Do you have a ".txt" supplementary info file? (If none click cancel)')
        asked = True
    
    if info_name != None:
        file_check = glob.glob(info_name + '/*.txt')
    else:
        file_check = []
    
    if file_check == [] and asked:
        print('''
              
              davis_rig_parser.create_df()
                  If you don't have extra info and you don't want the pop up everytime, pass info_name=None into create_df()
    
    ''')
    #Initiate a list to store individual file dataframes                
    merged_data = []   
    #Look for the ms8 files in the directory
    file_list = os.listdir('./')
    med_name = ''
    for files in file_list:
        if files[-3:] == 'txt':
            med_name = files
            file_name = dir_name+'/'+med_name
        
            #Run functions to extract trial data
            out_put_dict = MedMS8_reader_stone(file_name, file_check, min_latency, min_ILI=min_ILI)
            MaxWait = out_put_dict['MaxWait']
            dfFull = LickMicroStructure_stone(out_put_dict['LickDF'], out_put_dict['LatencyMatrix'], bout_pause)
    
            #Merge the data into a list
            merged_data.append(dfFull)
    
    #Append dataframe with animal's details
    merged_df = pd.concat(merged_data)
    
    #Format to capitalize first letter of labels
    merged_df['Condition'] = merged_df.Condition.str.title()
    
    # Extract dataframe for ease of handling
    df = merged_df
    
    # Ensure all entries in the 'Bouts' column are lists
    df['Bouts'] = df['Bouts'].apply(lambda x: [x] if isinstance(x, int) else x)
    
    # Expand the lists in the 'Bouts' column into a DataFrame
    df_lists = pd.DataFrame(df['Bouts'].tolist())
    
    # Replace 0s with NaNs to prevent them from being counted
    df_lists = df_lists.replace(0, np.nan)
    
    # Compute bout counts (non-NaN values per row)
    df['bout_count'] = df_lists.count(axis=1)
    
    # Compute the mean of bouts, skipping NaNs
    df['Bouts_mean'] = df_lists.mean(axis=1, skipna=True)



    #Work on ILI means
    # Ensure the index is unique
    df = df.reset_index(drop=True)
    
    # Expand the lists in the 'ILIs' column into a DataFrame
    df_lists = pd.DataFrame(df['ILIs'].apply(lambda x: [sublist for sublist in x]).tolist())
    
    # Flatten nested lists into all_trials
    all_trials = []
    for _, row in df_lists.iterrows():
        trial_ILI = []
        for sublist in row.dropna():
            trial_ILI.append(sublist)
        flat_trial = list(itertools.chain(*trial_ILI))
        # Exclude NaN values
        all_trials.append([i for i in flat_trial if not np.isnan(i)])
    #Store ILIs extended into dataframe
    df['ILI_all'] = all_trials
    df['Animal'] = df['Animal'].str.strip()
    
    #Length is the length given to the shutter opening, but since the 
    #first lick(s) could be false, the actual time the rat has to lick
    #is Tri_Length
    df['TriLength'] = df['LENGTH'] - df['TriLength']
    
    df['Bouts'] = df['Bouts'].apply(lambda x: [] if isinstance(x, int) and x == 0 else x)

    i = 1
    groups = []
    #assign experiment and subject numbers
    for name, group in df.groupby(['Animal']):
        group['Subject'] = f'Animal{i}'
        i+=1
        groups.append(group)
    df = pd.concat(groups)
    
    #add how long the rat has to start licking
    df['MaxWait'] = MaxWait
    df['MaxWait'] = df['MaxWait'].apply(lambda x: float(str(x).strip()))

    cols = df.columns.tolist()
    
    # rearrange the columns to place 'Time' next to 'Date'
    date_index = cols.index('Date')
    time_index = cols.index('Time')
    cols.insert(date_index + 1, cols.pop(time_index))
    
    # rearrange the columns to place 'Subject' next to 'Animal'
    animal_index = cols.index('Animal')
    subject_index = cols.index('Subject')
    cols.insert(animal_index + 1, cols.pop(subject_index))
    
    # rearrange the columns to place 'TriLength' next to 'LENGTH'
    length_index = cols.index('LENGTH')
    tri_length_index = cols.index('TriLength')
    cols.insert(length_index + 1, cols.pop(tri_length_index))
    
    # rearrange the columns to place 'MaxWait' next to 'Latency'
    latency_index = cols.index('Latency')
    max_wait_index = cols.index('MaxWait')
    cols.insert(latency_index + 1, cols.pop(max_wait_index))
    
    # Reorder the DataFrame
    df = df[cols]
    

    
    #Wow, look at you, reading through the code! Good job keep it up.
    
    df = df.rename(columns={'PRESENTATION': 'Presentation'})
    df = df.rename(columns={'Trial_num': 'TrialNum'})
    df = df.rename(columns={'TUBE': 'Tube'})
    df = df.rename(columns={'CONCENTRATION': 'Concentration'})
    df = df.rename(columns={'SOLUTION': 'Solution'})
    df = df.rename(columns={'LENGTH': 'Length'})
    df = df.rename(columns={'LICKS': 'Licks'})
    df = df.rename(columns={'Lat_First': 'LatFirst'})
    df = df.rename(columns={'bout_count': 'BoutCount'})
    df = df.rename(columns={'Bouts_mean': 'BoutsMean'})
    df = df.rename(columns={'ILI_all': 'AllILIs'})
    df = df.rename(columns={'CloseError\n': 'CloseError'})

    #add lickrate too
    df['LickRate'] = df['AllILIs'].apply(calculate_lick_rates, bout_pause=300)
    #Save dataframe for later use/plotting/analyses
    #timestamped with date
    if save_df==True:
        df.to_pickle(dir_name+'/%s_grouped_dframe.df' %(date.today().strftime("%d_%m_%Y")))

    return df

