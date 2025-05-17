# -*- coding: utf-8 -*-
"""
Created on Sat May 10 18:07:14 2025

@author: Engin-Eer
"""


### BEGIN - IMPORTS ###
import pandas as pd
import numpy as np
import random
import math
from typing import Tuple,List
from collections import Counter
import sys
### END   - IMPORTS ###


### BEGIN - DATA IMPORTS ###
data_components = pd.read_excel("C:/Users/Engin-Eer/OneDrive - University of Southampton/Semester 2/MATH 6119 - Analytical Consultancy Skills/New Code/NewCode.xlsx", sheet_name="Sheet1")
compatibility = pd.read_excel("C:/Users/Engin-Eer/OneDrive - University of Southampton/Semester 2/MATH 6119 - Analytical Consultancy Skills/New Code/NewCode.xlsx", sheet_name="Sheet2")
data_feeder = pd.read_excel("C:/Users/Engin-Eer/OneDrive - University of Southampton/Semester 2/MATH 6119 - Analytical Consultancy Skills/New Code/NewCode.xlsx", sheet_name="Sheet3")
### END   - DATA IMPORTS ###

### BEGIN - REQUIRED FUNCTIONS ###
#random.seed(3428)

def euclidean(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
### END   - REQUIRED FUNCTIONS ###

####################################################### BEGINNING OF INITIALIZATION #######################################################

### BEGIN - GENERATE RANDOM CHROMOSOMES ###
def generate_random_chromosome(data_components: pd.DataFrame, compatibility: pd.DataFrame) -> pd.DataFrame:
    # Merge all compatible HeadType options
    compatibility_expanded = data_components.merge(
        compatibility,
        left_on="Group",
        right_on="CompType",
        how="left"
    )

    # Group by original component and collect all compatible head types
    grouped = compatibility_expanded.groupby("comp")["HeadType"].apply(list).reset_index()

    # Add Option1 to Option4 columns by splitting the list
    for i in range(4):
        grouped[f"Option{i+1}"] = grouped["HeadType"].apply(lambda x: x[i] if i < len(x) else None)

    # Calculate number of valid options
    grouped["num_options"] = grouped[[f"Option{i+1}" for i in range(4)]].apply(
        lambda row: sum(pd.notnull(row)), axis=1
    )

    # Assign individual probabilities
    for i in range(4):
        option_col = f"Option{i+1}"
        prob_col = f"{option_col}_probability"
        grouped[prob_col] = grouped.apply(
            lambda row: round(1 / row["num_options"], 3) if pd.notnull(row[option_col]) and row["num_options"] > 0 else 0.0,
            axis=1
        )

    # Choose chromosome from non-None options only
    def choose_chromosome(row):
        options = [row[f"Option{i+1}"] for i in range(4) if pd.notnull(row[f"Option{i+1}"])]
        return random.choice(options) if options else None

    grouped["chromosome"] = grouped.apply(choose_chromosome, axis=1)

    # Drop temporary columns
    grouped.drop(columns=["HeadType", "num_options"], inplace=True)

    # Merge with original data_components to bring in all the other columns
    data = data_components.merge(grouped, on="comp", how="left")

    # Create unique code: comp,chromosome
    data['Comp_Chromosome'] = data[['comp', 'chromosome']].apply(
        lambda x: ','.join(x.dropna().astype(str)), axis=1
    )    

    return data


### END   - GENERATE RANDOM CHROMOSOMES ###
  

### BEGIN - GENERATE n POPULATIONS ###

populations = {}
n=True
k=0
while n==True:
    num_populations = 20
    for i in range(1, num_populations + 1):
        chromosome_df = generate_random_chromosome(data_components, compatibility)
        
        # Rename X and Y columns to XComp and YComp
        chromosome_df.rename(columns={"X": "XComp", "Y": "YComp"}, inplace=True)
        
        # Create the population table with the renamed columns
        populations[f"population_{i}"] = chromosome_df[["comp", "chromosome", "Group", "XComp", "YComp"]].copy()
    
    # Loop through each population and merge X, Y from data_feeder
    for i in range(1, num_populations + 1):
        # Get the current population dataframe
        population_df = populations[f"population_{i}"]
        
        # Merge the X and Y from data_feeder based on Feeder and Group
        population_df = population_df.merge(data_feeder[['Feeder', 'X', 'Y']], 
                                             left_on='Group', 
                                             right_on='Feeder', 
                                             how='left')
        
        # Rename the X and Y columns to XFeeder and YFeeder
        population_df.rename(columns={"X": "XFeeder", "Y": "YFeeder"}, inplace=True)
        
        # Store the updated dataframe back in the dictionary
        populations[f"population_{i}"] = population_df
    del(population_df,i,num_populations)
    
    
    ### END   - GENERATE n POPULATIONS ###
    
    
    ### BEGIN - HEAD & MACHINE ASSIGNMENT BY BALANCING WORKLOAD BASED ON NUMBER OF TASKS ###
    
    # Function to assign exactly 3 chromosomes to each machine randomly (total 9 chromosomes, 3 machines)
    def assign_chromosomes_to_machines(populations):
        machines = ['M1', 'M2', 'M3']
    
        # Step 1: Get all unique chromosomes
        unique_chromosomes = set()
        for population_df in populations.values():
            unique_chromosomes.update(population_df['chromosome'])
    
        if len(unique_chromosomes) != 9:
            raise ValueError("Expected exactly 9 unique chromosomes for 3 machines with 3 each.")
    
        # Step 2: Shuffle and assign 3 chromosomes to each machine
        shuffled_chromosomes = list(unique_chromosomes)
        random.shuffle(shuffled_chromosomes)
    
        chromosome_to_machine = {}
        for i, machine in enumerate(machines):
            assigned_chromosomes = shuffled_chromosomes[i*3:(i+1)*3]
            for chrom in assigned_chromosomes:
                chromosome_to_machine[chrom] = machine
    
        # Step 3: Assign machines based on chromosome mapping
        for population_df in populations.values():
            population_df['Machine'] = population_df['chromosome'].map(chromosome_to_machine)
    
        return populations
    
    
    # Perform the chromosome assignment and update the populations
    populations = assign_chromosomes_to_machines(populations)
    
    
    ### END   - HEAD & MACHINE ASSIGNMENT BY BALANCING WORKLOAD BASED ON NUMBER OF TASKS ###
    
    ####################################################### END OF INITIALIZATION #######################################################
    
    ####################################################### BEGINNING OF EVALUATE FITNESS #######################################################
    
    ### BEGIN - RUN THE ALGORITHM ###
    
    def pick_and_place_components(populations: dict) -> dict:
        results_dict = {}
    
        for population_name, df in populations.items():
            results = []
            index = 1
            df = df.copy()
            machine_groups = df.groupby("Machine")
    
            for machine, machine_df in machine_groups:
                remaining_df = machine_df.copy()
    
                while not remaining_df.empty:
                    picked_rows = []
                    used_heads = set()
                    pos = np.array([0, 0])
    
                    while len(picked_rows) < 3 and not remaining_df.empty:
                        remaining_df["Distance"] = remaining_df.apply(
                            lambda row: euclidean(pos, [row["XFeeder"], row["YFeeder"]]), axis=1
                        )
                        sorted_df = remaining_df.sort_values("Distance")
    
                        found = False
                        for idx, row in sorted_df.iterrows():
                            head = row["chromosome"]
                            if head not in used_heads:
                                picked_rows.append((idx, row))
                                used_heads.add(head)
                                pos = np.array([row["XFeeder"], row["YFeeder"]])
                                found = True
                                break
    
                        if not found:
                            break
    
                    if not picked_rows:
                        break
    
                    batch_distance = 0.0
                    pos = np.array([0, 0])  # Reset to origin
    
                    for idx, row in picked_rows:
                        pick_pos = np.array([row["XFeeder"], row["YFeeder"]])
                        batch_distance += euclidean(pos, pick_pos)
                        results.append([
                            index, *pick_pos, row["comp"], "Pick", machine, batch_distance, row["chromosome"]
                        ])
                        pos = pick_pos
                        index += 1
    
                    for idx, row in picked_rows:
                        place_pos = np.array([row["XComp"], row["YComp"]])
                        batch_distance += euclidean(pos, place_pos)
                        results.append([
                            index, *place_pos, row["comp"], "Place", machine, batch_distance, row["chromosome"]
                        ])
                        pos = place_pos
                        index += 1
    
                    batch_distance += euclidean(pos, np.array([0, 0]))
                    results.append([
                        index, 0, 0, "", "Return", machine, batch_distance, ""
                    ])
                    index += 1
    
                    processed_indices = [idx for idx, _ in picked_rows]
                    remaining_df = remaining_df.drop(index=processed_indices)
    
            results_df = pd.DataFrame(results, columns=["Index", "X", "Y", "Component", "Action", "Machine", "RouteDistance", "HeadType"])
            results_dict[population_name] = results_df
    
        return results_dict
    
    
    # Running the algorithm on the populations
    results_dict = pick_and_place_components(populations)
    
    # Export results
    #for pop_name, df in results_dict.items():
    #    print(f"\nResults for {pop_name}:\n", df)
    #    df.to_excel(f"pick_and_place_results_{pop_name}.xlsx", index=False)
    
    #del(pop_name,df)
    
    
    
    
    ### END   - RUN THE ALGORITHM ###
    
    ### BEGIN - SUMMARY TABLE FOR POPULATIONS ###
    
    # Create a list to collect rows
    summary_rows = []
    
    for pop_name, df in results_dict.items():
        # Filter to only 'Return' actions
        return_rows = df[df["Action"] == "Return"]
    
        # Calculate total distance for each machine from Return rows only
        m1_dist = return_rows[return_rows["Machine"] == "M1"]["RouteDistance"].sum()
        m2_dist = return_rows[return_rows["Machine"] == "M2"]["RouteDistance"].sum()
        m3_dist = return_rows[return_rows["Machine"] == "M3"]["RouteDistance"].sum()
    
        # TotalDistance is based on the max among M1, M2, M3 (not sum)
        total_distance = max(m1_dist, m2_dist, m3_dist)*3
    
        summary_rows.append({
            "Population": pop_name,
            "M1TotalDistance": m1_dist,
            "M2TotalDistance": m2_dist,
            "M3TotalDistance": m3_dist,
            "TotalDistance": total_distance
        })
    
    # Convert to final summary DataFrame
    results_2 = pd.DataFrame(summary_rows)
    results_2.set_index("Population", inplace=True)
    
    # Show the summary
    #print(results_2)
    del(m1_dist,m2_dist,m3_dist,pop_name,summary_rows,total_distance,df,return_rows)
    
    
    ### END   - SUMMARY TABLE FOR POPULATIONS ###
    
    
    
    
    
    ### BEGIN - PENALTY FOR FITNESS CHECK ###
    def calculate_fitness(row):
        distances = [row['M1TotalDistance'], row['M2TotalDistance'], row['M3TotalDistance']]
        std_penalty = np.std(distances) * 40
        fitness = row['TotalDistance'] + std_penalty
        return fitness
    
    # Apply the function to each row in results_2
    results_2['Fitness'] = results_2.apply(calculate_fitness, axis=1)
    
    
    ### END   - PENALTY FOR FITNESS CHECK ###
    
    
    
    ### BEGIN - RANK SYSTEM TO CHOOSE ELITES ###
    
    
    # Calculate fitness percentiles
    q25 = results_2['Fitness'].quantile(0.05)
    q75 = results_2['Fitness'].quantile(0.35)
    
    # Assign Rank based on fitness tiers
    results_2['Rank'] = results_2['Fitness'].apply(
        lambda x: 1 if x <= q25 else (3 if x > q75 else 2)
    )
    
    # Get all Rank 1 populations (from the index)
    rank1 = results_2[results_2['Rank'] == 1].index.tolist()
    
    # Get half of Rank 2 populations randomly (from the index)
    rank2 = results_2[results_2['Rank'] == 2].sample(frac=0.5, random_state=42).index.tolist()
    
    # Combine
    selected_populations = rank1 + rank2
    
    ##MY ELITES, MY PRECIOUS!!! <3
    results_fit = pd.DataFrame({'Population': selected_populations})
    
    del(rank1,rank2,q25,q75,selected_populations)
    
    ### END   - RANK SYSTEM TO CHOOSE ELITES ###
    
    ####################################################### END OF OF EVALUATE FITNESS #######################################################
    
    
    
    
    ####################################################### BEGINNING OF CROSSOVER #######################################################
    # Step 1: Make a copy of the populations dictionary
    populations_1 = populations.copy()
    
    # Step 2: Filter populations_1 to only keep items that are in results_fit['Population']
    valid_populations = results_fit['Population'].unique()  # Get unique populations from results_fit
    
    # Filter populations_1 to keep only valid populations
    filtered_populations = {k: v for k, v in populations_1.items() if k in valid_populations}
    
    # Step 3: Convert the filtered populations to a long list, keeping only 'comp' and 'chromosome' columns
    long_list = []
    
    # Loop through the dictionary
    for population_name, population_data in filtered_populations.items():
        # Iterate through each component and its corresponding chromosome
        for comp, chromosome in zip(population_data['comp'], population_data['chromosome']):
            long_list.append({'Comp': comp, 'Chromosome': chromosome, 'Population': population_name})
    
    # Convert the list to a DataFrame
    long_list_df = pd.DataFrame(long_list)
    
    del(long_list,population_data,population_name,populations_1,valid_populations,comp,chromosome,filtered_populations)
    
    # Perform a left join to merge long_list_df with results_2 on the "Population" column
    long_list_df = pd.merge(long_list_df, results_2[['Rank']], left_on='Population', right_index=True, how='left')
    
    
    # Combine 'Comp' and 'Chromosome' into a single column, separated by a comma
    long_list_df['Comp_Chromosome'] = long_list_df['Comp'] + ',' + long_list_df['Chromosome']
    
    # Drop the old columns 'Comp', 'Chromosome', and 'Population'
    long_list_df = long_list_df.drop(columns=['Comp', 'Chromosome', 'Population'])
    
    # Sort by 'Rank' in ascending order
    long_list_df = long_list_df.sort_values(by='Rank', ascending=True)
    
    
    # Define a function to check number of None values
    def check_mutation(row):
        options = [row['Option1'], row['Option2'], row['Option3'], row['Option4']]
        none_count = options.count(None)
        return 'Noway' if none_count >= 3 else 'Possible'
    
    # Apply the function to create 'ifMutation' column
    chromosome_df['ifMutation'] = chromosome_df.apply(check_mutation, axis=1)
    
    # Split 'Comp_chromosome' into two new columns: 'Comp' and 'chromosome'
    long_list_df[['Comp', 'chromosome']] = long_list_df['Comp_Chromosome'].str.split(',', expand=True)
    
    # Perform left join to bring 'ifMutation' from chromosome_df into long_list_df
    long_list_df = long_list_df.merge(
        chromosome_df[['comp', 'ifMutation']], 
        how='left', 
        left_on='Comp', 
        right_on='comp'
    )
    
    # Optional: drop the redundant 'comp' column from chromosome_df if you want a cleaner result
    long_list_df.drop(columns=['comp'], inplace=True)
    
    long_list_df = long_list_df[long_list_df['ifMutation'] != 'Noway'].reset_index(drop=True)
    
    
    ##Chosing another Option, chromosome crossover happens here!!
    
    # Step 1: Ensure 'comp' in chromosome_df is renamed to match long_list_df
    chromosome_df_renamed = chromosome_df.rename(columns={'comp': 'Comp'})
    
    
    # Step 2: Merge on 'Comp' to bring in the option columns
    merged_df = pd.merge(long_list_df, chromosome_df_renamed[['Comp', 'Option1', 'Option2', 'Option3', 'Option4']], on='Comp', how='left')
    
    # Step 3: Function to pick a valid random option
    def get_valid_random_option(row):
        options = [row['Option1'], row['Option2'], row['Option3'], row['Option4']]
        valid_options = [opt for opt in options if pd.notna(opt) and opt != row['chromosome']]
        return random.choice(valid_options) if valid_options else None
    
    # Step 4: Apply the function
    merged_df['RandomNewChromosome'] = merged_df.apply(get_valid_random_option, axis=1)
    
    # Step 5: Drop the option columns if not needed
    final_df = merged_df.drop(columns=['Option1', 'Option2', 'Option3', 'Option4'])
    
    # Optional: Assign back to long_list_df if you’re continuing
    long_list_df = final_df
    
    #######################################################    END OF CROSSOVER    #######################################################
    
    
    
    
    #######################################################    BEGINNING OF A NEW GENERATION    #######################################################
        #Updating Initial setup   
    def update_probabilities_from_long_list(chromosome_df: pd.DataFrame, long_list_df: pd.DataFrame) -> pd.DataFrame:
        option_cols = [f"Option{i}" for i in range(1, 5)]
        prob_cols = [f"{opt}_probability" for opt in option_cols]
    
        for comp_chrom in long_list_df['Comp_Chromosome']:
            # Locate matching row in chromosome_df
            match_rows = chromosome_df[chromosome_df['Comp_Chromosome'] == comp_chrom]
            if match_rows.empty:
                continue  # Skip if no match found
    
            row_idx = match_rows.index[0]
            row = chromosome_df.loc[row_idx]
    
            # Identify which Option matches the selected chromosome
            T = None
            for i in range(4):
                if pd.notnull(row[option_cols[i]]) and row['chromosome'] == row[option_cols[i]]:
                    T = i + 1
                    break
    
            if T is None:
                continue  # No matching OptionX found, skip this row
    
            # Get valid options (non-None)
            valid_indices = [i for i in range(4) if pd.notnull(row[option_cols[i]])]
            n = len(valid_indices)
    
            if n < 2:
                continue  # Nothing to redistribute, skip
    
            # Increase OptionT_probability by 25%
            original_prob = row[f"Option{T}_probability"]
            new_prob_T = min(round(original_prob * 1.25, 6), 1.0)  # Cap at 1.0
    
            # Calculate remaining probability to distribute
            remaining_prob = max(1.0 - new_prob_T, 0.0)
    
            # Redistribute among other valid options
            other_indices = [i for i in valid_indices if i + 1 != T]
            redistributed_prob = round(remaining_prob / len(other_indices), 6) if other_indices else 0.0
    
            # Update probabilities in the DataFrame
            chromosome_df.at[row_idx, f"Option{T}_probability"] = new_prob_T
            for i in other_indices:
                chromosome_df.at[row_idx, f"Option{i+1}_probability"] = redistributed_prob
    
        return chromosome_df
    chromosome_df = update_probabilities_from_long_list(chromosome_df, long_list_df)
    min_distance_index = results_2['TotalDistance'].idxmin()
    min_distance_value = results_2['TotalDistance'].min()
    print(f"{min_distance_index} has: {min_distance_value}")
    k += 1
    if k==50:
        sys.exit()



#######################################################    END OF A NEW GENERATION          #######################################################

