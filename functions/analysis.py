import os
import sys
import numpy as np
import pandas as pd

def get_data(subject:str | None=None, datadir: str | None=None, task: str | None = "ball_speed_change"):
    datadir = "/Users/wiegerscheurer/repos/physicspred/data" if datadir is None else datadir
    
    subs = [sub for sub in os.listdir(datadir) if sub.startswith("sub")] if subject is None else [subject]
        

    file_stack = []
    for sub in subs:

        datafiles = os.listdir(f"{datadir}/{sub}/{task}/")
        for file in datafiles:
        
            if file.endswith(".csv"):
                this_file = pd.read_csv(f"{datadir}/{sub}/{task}/{file}")
                file_stack.append(this_file)

        # Concatenate all DataFrames in the list into a single DataFrame
        combined_df = pd.concat(file_stack, ignore_index=True)

    return combined_df

def get_precision(df, hypothesis:str = "both", include_dubtrials=False, return_df:bool=False):
    """Precision: True positives / (True positives + False positives)
    Args:
        df (pd.dataframe): The data
        hypothesis (str): The hypothesis to test. Can be either "simulation", "abstraction" or "both"
        include_dubtrials (bool): Whether to include trials where both hypotheses are congruent
        return_df (bool): Whether to return the filtered DataFrame instead of the precision value
    
    """
    
    hypotheses_types = ["simulation", "abstraction"]
    hypotheses = hypotheses_types if hypothesis == "both" else [hypothesis]
    
    stat_dict = {}

    # if np.sum([f"{hypotheses_types[0][:3]}_congruent"]) 
    
    
    # elif df[f"{hypotheses_types[1][:3]}_congruent"].isna().all():
    #     null_dict = {h: None for h in hypotheses}
    #     return null_dict    
    # else:

    for hypothesis in hypotheses:
        other_hypothesis = [h for h in hypotheses_types if h != hypothesis][0]
        
        filtered_df = df[
            # (df['ball_change'] == True) & # Only trials with a target
            (df['response'] != None) & # Only trials with a target
            (df[hypothesis[:3] + '_congruent'] == True) & # Only trials congruent with the hypothesis
            (~df[other_hypothesis[:3] + '_congruent']) # Only trials incongruent with the other hypothesis
        ]
        if include_dubtrials:
            filtered_df = df[
                (df['ball_change'] == True) & # Only trials with a target
                (df[hypothesis[:3] + '_congruent'] == True)] # Only trials congruent with the hypothesis
        
        # Compute the mean, which works because you have 1 for True and 0 for False
        output = np.mean(filtered_df['accuracy']) if not return_df else filtered_df
        stat_dict[hypothesis] = output
        
    return stat_dict

def get_sensitivity(df, hypothesis:str = "both", include_dubtrials=False, return_df:bool=False):
    """Precision: True positives / (True positives + False negatives)
    Args:
        df (pd.dataframe): The data
        hypothesis (str): The hypothesis to test. Can be either "simulation", "abstraction" or "both"
        include_dubtrials (bool): Whether to include trials where both hypotheses are congruent
        return_df (bool): Whether to return the filtered DataFrame instead of the precision value
    
    """
    
    hypotheses_types = ["simulation", "abstraction"]
    hypotheses = hypotheses_types if hypothesis == "both" else [hypothesis]
    
    stat_dict = {}
    
    for hypothesis in hypotheses:
        other_hypothesis = [h for h in hypotheses_types if h != hypothesis][0]
        
        target_trials = df[
            (df['ball_change'] == True) & # Only trials with a target
            (df[hypothesis[:3] + '_congruent'] == True) & # Only trials congruent with the hypothesis
            (~df[other_hypothesis[:3] + '_congruent']) # Only trials incongruent with the other hypothesis
        ]
        if include_dubtrials:
            target_trials = df[
                (df['ball_change'] == True) & # Only trials with a target
                (df[hypothesis[:3] + '_congruent'] == True)] # Only trials congruent with the hypothesis
             
        output = np.mean(target_trials['accuracy']) if not return_df else target_trials
        stat_dict[hypothesis] = output
        
    return stat_dict
    
    
def get_f1_score(df, hypothesis:str = "both", include_dubtrials=False, return_df:bool=False):
    """F1 score: 2 * (precision * recall) / (precision + recall)
    Args:
        df (pd.dataframe): The data
        hypothesis (str): The hypothesis to test. Can be either "simulation", "abstraction" or "both"
        include_dubtrials (bool): Whether to include trials where both hypotheses are congruent
        return_df (bool): Whether to return the filtered DataFrame instead of the precision value
    
    """
    
    precision = get_precision(df, hypothesis, include_dubtrials, return_df)
    recall = get_sensitivity(df, hypothesis, include_dubtrials, return_df)
    
    f1 = {k: 2 * (precision[k] * recall[k]) / (precision[k] + recall[k]) for k in precision.keys()}
    
    return f1


def get_specificity():
    pass

def get_accuracy():
    pass

def get_confusion_matrix():
    pass

def get_roc_curve():
    pass

