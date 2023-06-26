import json
import networkx as nx
import gzip
import pandas as pd
import sys
import os
import numpy as np
import jsonlines
import glob
import plotly.express as px


def get_director_id_and_films(path_to_drive):
  director_id_folders = [] #to get the name of the director id
  all_films_by_director_id = [] #to store the path of a file to access all of the movies a director has done
  path_to_drive_files = os.listdir(path_to_drive)
  for item in path_to_drive_files:
    if item != 'gen_networkv3.py': #my own system had this file saved in this folder which I wanted to for reviewing the data.
      director_id_folders.append(item) 
  for dir_id in director_id_folders:
    all_films_by_director_id.append(f"{path_to_drive}/{dir_id}/feature_films/*.jsonl")
  return all_films_by_director_id

films_path = get_director_id_and_films(path_to_drive) #should manually be replaced with the file path of where the folders are stored on a computer.

def get_director_id(path_to_drive): #is similar to the function above, but returns the director id instead.
  director_id_folders = []
  all_films_by_director_id = []
  path_to_drive_files = os.listdir(path_to_drive)
  for item in path_to_drive_files:
    if item != 'gen_networkv3.py':
      director_id_folders.append(item) 
  return director_id_folders

def homogeneity_score_test(data, role_name):
  store = []
  director_info = []
  new_store = []
  store_unique = []
  measure = 0
  for d in data:
    if 'role' in d:
      if d['role'].startswith("Writing Credits"): # checks if 'role' parameter starts with 'Writing Credits'
         d['role'] = "Writing Credits" # return writing credits if it does to normalize it.
      if d['role'] == role_name: #holds onto each crew member with that role, including the director.
        store += d['crew']
      if d['role'] == 'Directed by':
        director_info += d['crew']
  for item in store:
    if item not in director_info:
      new_store.append(item) #holds onto each crew member with that role across the movies, with the exception of the director.
  for item in new_store:
    if item not in store_unique:
      store_unique.append(item) #store_unique holds each unique crew member's name (doesn't include doubles)
  if len(new_store) < 1: #this if condition is meant to account for a role not having any crew members a director's movies, except for potentially the director
    measure = -1
  else:
    measure = 1 - (len(store_unique)/len(new_store)) #implements the homogeneity.
  return measure

def score_by_role_test(data, role_names):
  homogeneity_by_director = []
  store_keeper = []
  store_keeper_new = []
  for item in role_names:
      store_keeper.append(homogeneity_score_test(data, item)) #holds onto the average homogeneity for each role given for 1 specific director
  for item in store_keeper:
    if item != -1:
      store_keeper_new.append(item) #appends the average homogeneity for every role that has a cast member who is not the director.
  homogeneity_by_director = np.mean(store_keeper_new)
  return homogeneity_by_director

def all_directors():
  store_all = []
  average_homogeneity = []
  i = 0
  while i < len(films_path): #runs for all 101 directors to get average homogeneity for the given roles
    for file_path in glob.glob(films_path[i]): 
      with jsonlines.open(file_path) as reader:
        for item in reader:
          store_all.append(item)
    average_homogeneity.append(score_by_role_test(store_all, ['Sound Department', 'Makeup Department', 'Special Effects by', 'Writing Credits', 'Cinematography by', 'Film Editing by', 'Music by', 'Production Design by', 'Costume Design by']))
    store_all.clear()
    i += 1
  return average_homogeneity

#below- involves using the 101 film directors csv file.

dataframe = pd.read_csv('100_film_directors.csv') #reads in the data file with all of the attributes about the directors

dataframe = dataframe.rename(columns = {'IMDb_URI':'director_id'}) #renaming the column, since for analysis purposes, the imdb site link is not needed

dataframe['director_id'] = dataframe['director_id'].str.replace('https://www.imdb.com/name/', '') #modifying the names of the values in the director_id column, to just get to the director id

dataframe['director_id'] = dataframe['director_id'].str.replace('/', '') #same as above

second_data_frame = pd.DataFrame(get_director_id(('/Users/manasalagisetty/Documents/GroupProject/director_crew_info'))) #making a new data frame with the director id

second_data_frame.columns = ['director_id'] #naming the column director id

second_data_frame['average_homogeneity'] = all_directors() #adding the average homogeneity score by director id to the data frame (since it's in order, just doing this is enough)

def number_of_films_directed(data): #to help me get the number of films that one director had directed
  director_repetitions = []
  for d in data:
    if 'role' in d:
      if (d['role'] == 'Directed by'):
        director_repetitions.append(d['crew'])
        #print(d.get('crew'))
  return len(director_repetitions)

def films_for_all_directors(): #implements the number of films that the 101 directors in the film were involved in directing.
  store_all = []
  director_repetitions = []
  i = 0
  while i < len(films_path):
    for file_path in glob.glob(films_path[i]): 
      with jsonlines.open(file_path) as reader:
        for item in reader:
          store_all.append(item)
    director_repetitions.append(number_of_films_directed(store_all))
    store_all.clear()
    i += 1
  return director_repetitions

second_data_frame['number_of_films'] = films_for_all_directors()

second_data_frame = pd.merge(dataframe, second_data_frame, on = 'director_id') #merging the first and second data frames together, so that average homogeneity corresponds to the correct director

print(second_data_frame['number_of_films'].sum()) #sum of number of films

second_data_frame = second_data_frame.sort_values(by='average_homogeneity', ascending=False)

#below here- it was intended to look at the interesting director nodes.

second_data_frame.loc[second_data_frame['LastName'] == 'Coppola']

second_data_frame.loc[second_data_frame['LastName'] == 'Wachowski']

print(second_data_frame.groupby("Sex").mean(numeric_only=True)) #F = Female, M = Male, getting breakdown for average homogeneity for each of these groups.

print(second_data_frame.groupby("Labels").mean(numeric_only=True)) #H = highest grossing directors, Q = LGBT, getting breakdown for average homogeneity for each of these groups.

print(second_data_frame.groupby("Ethnicity_Race").mean(numeric_only=True)) #getting breakdown by race for average homogeneity.

print(second_data_frame.groupby(['Sex', 'Ethnicity_Race']).size()) #tells us number of directors by a particular group.

#for developing the information into a histogram, separating scores into categories below.

zero_to_ten = second_data_frame.loc[second_data_frame['average_homogeneity'] < 0.10]
zero_to_ten = zero_to_ten['average_homogeneity'].values
ten_to_twenty = second_data_frame.loc[(second_data_frame['average_homogeneity'] >= 0.10) & (second_data_frame['average_homogeneity'] < 0.20)]
ten_to_twenty = ten_to_twenty['average_homogeneity'].values
twenty_to_thirty = second_data_frame.loc[(second_data_frame['average_homogeneity'] >= 0.20) & (second_data_frame['average_homogeneity'] < 0.30)]
twenty_to_thirty = twenty_to_thirty['average_homogeneity'].values
thirty_to_forty = second_data_frame.loc[(second_data_frame['average_homogeneity'] >= 0.30) & (second_data_frame['average_homogeneity'] < 0.40)]
thirty_to_forty = thirty_to_forty['average_homogeneity'].values
forty_to_fifty = second_data_frame.loc[(second_data_frame['average_homogeneity'] >= 0.40) & (second_data_frame['average_homogeneity'] < 0.50)]
forty_to_fifty = forty_to_fifty['average_homogeneity'].values
fifty_plus = second_data_frame.loc[second_data_frame['average_homogeneity'] >= 0.50]
fifty_plus = fifty_plus['average_homogeneity'].values

x = 'zero_to_ten', 'ten_to_twenty', 'twenty_to_thirty', 'thirty_to_forty', 'forty_to_fifty', 'fifty_plus'

y = [len(zero_to_ten), len(ten_to_twenty), len(twenty_to_thirty), len(thirty_to_forty), len(forty_to_fifty), len(fifty_plus)]

y

fig = px.histogram(x=x, y = y)
#fig.show()

fig.update_layout(
    title="Directors with Varying Homogeneity Scores", title_x = 0.5,
    xaxis_title="Homogeneity Scores",
    yaxis_title="Number of Directors",
    font=dict(
        family="Times New Roman, monospace",
        size=14,
        color="black"
    )
)
fig.write_image("fig1.png")

print(second_data_frame)


 
    



