import numpy as np
import pandas as pd
import pickle
import random
song_df = pd.read_csv('ml_model/Final Dataset.csv')
song_df['song'] = song_df['title'].map(str) + " - " + song_df['artist_name']




class item_similarity_recommender_py():
    def __init__(self):
        self.train_data = None
        self.user_id = None
        self.item_id = None
        self.cooccurence_matrix = None
        self.songs_dict = None
        self.rev_songs_dict = None
        self.item_similarity_recommendations = None
        
    def get_user_items(self, user):
        user_data = self.train_data[self.train_data[self.user_id] == user]
        user_items = list(user_data[self.item_id].unique())
        return user_items
        
    def get_item_users(self, item):
        item_data = self.train_data[self.train_data[self.item_id] == item]
        item_users = set(item_data[self.user_id].unique()) 
        return item_users
        
    def get_all_items_train_data(self):
        all_items = list(self.train_data[self.item_id].unique())  
        return all_items
        
    def construct_cooccurence_matrix(self, user_songs, all_songs):
        user_songs_users = []        
        for i in range(0, len(user_songs)):
            user_songs_users.append(self.get_item_users(user_songs[i]))
        cooccurence_matrix = np.matrix(np.zeros(shape=(len(user_songs), len(all_songs))), float)
        for i in range(0,len(all_songs)):
            songs_i_data = self.train_data[self.train_data[self.item_id] == all_songs[i]]
            users_i = set(songs_i_data[self.user_id].unique())
            for j in range(0,len(user_songs)):       
                users_j = user_songs_users[j]
                users_intersection = users_i.intersection(users_j)
                if len(users_intersection) != 0:
                    users_union = users_i.union(users_j)
                    cooccurence_matrix[j,i] = float(len(users_intersection))/float(len(users_union))
                else:
                    cooccurence_matrix[j,i] = 0
        return cooccurence_matrix

    def generate_top_recommendations(self, user, cooccurence_matrix, all_songs, user_songs, verbose=False):
        if verbose : print("Non zero values in cooccurence_matrix :%d" % np.count_nonzero(cooccurence_matrix))
        user_sim_scores = cooccurence_matrix.sum(axis=0)/float(cooccurence_matrix.shape[0])
        user_sim_scores = np.array(user_sim_scores)[0].tolist()
        sort_index = sorted(((e,i) for i,e in enumerate(list(user_sim_scores))), reverse=True)
        columns = ['user_id', 'song', 'score', 'rank']
        df = pd.DataFrame(columns=columns)
        rank = 1 
        for i in range(0,len(sort_index)):
            if ~np.isnan(sort_index[i][0]) and all_songs[sort_index[i][1]] not in user_songs and rank <= 10:
                df.loc[len(df)]=[user,all_songs[sort_index[i][1]],sort_index[i][0],rank]
                rank = rank+1
        if df.shape[0] == 0:
            print("The current user has no songs for training the item similarity based recommendation model.")
            return -1
        else:
            return df
 
    def create(self, train_data, user_id, item_id):
        self.train_data = train_data
        self.user_id = user_id
        self.item_id = item_id
    
    def recommend(self, user, verbose=False):
        user_songs = self.get_user_items(user)    
        if verbose : print("No. of unique songs for the user: %d" % len(user_songs))
        all_songs = self.get_all_items_train_data()
        if verbose : print("no. of unique songs in the training set: %d" % len(all_songs))
        cooccurence_matrix = self.construct_cooccurence_matrix(user_songs, all_songs)
        df_recommendations = self.generate_top_recommendations(user, cooccurence_matrix, all_songs, user_songs)
        return df_recommendations
    
    def get_similar_items(self, item_list, verbose=False):
        user_songs = item_list
        all_songs = self.get_all_items_train_data()
        if verbose : print("no. of unique songs in the training set: %d" % len(all_songs))
        cooccurence_matrix = self.construct_cooccurence_matrix(user_songs, all_songs)
        user = ""
        df_recommendations = self.generate_top_recommendations(user, cooccurence_matrix, all_songs, user_songs)
        return df_recommendations


def clean_name (name) :
    all_characters = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM:/.?_=-+()*&^%$#@!~`\|<>, '
    to_return = ''
    for character in name : 
        if character in all_characters : to_return += character 
    return to_return

# Get youtube links for recomended songs 
# Input the recomended column, this will return all links in form of list or dictionary 
# set return_dictionary to True if we need dictionary else it will return only links as list, no song names
def generate_link (list_song_names, return_dictionary=True) :
    to_return = 0
    if return_dictionary :
        to_return = {}
        for name in list_song_names :
            to_return[name] = 'https://www.youtube.com/results?search_query=' + clean_name(name).replace(' ','_') 
    else :
        to_return = []
        for name in list_song_names :
            to_return.append('https://www.youtube.com/results?search_query=' + clean_name(name).replace(' ','_'))
    return to_return

def get_main_song_name(song_name, dataframe) :
    for full_name in list(dataframe['song']) :
        if song_name.replace(' ','').lower() in full_name.replace(' ','').lower() : return full_name
    return None    

def get_required_dataframe(song_name, dataframe) :
    year = list(dataframe[dataframe['song']==song_name]['year'])[0]
    new_df = dataframe[dataframe['year']==year].reset_index()[:20000]
    return new_df



# get recomendation based on song name : main part of project 
# Takes input as song name and gives recomendation as list or dataframe with recomendations 
# input must be song inside dataframe, else will return no recomendations
# This is faster than UserID based recomendations and we mainly need this only 
def get_recomendation_song_name(song_name, dataframe, return_dataframe=True) : 
    if song_name not in list(dataframe['song']) :
        song_name = get_main_song_name(song_name, dataframe)
    if song_name is None :
        print('Song Not Available in Database')
        to_return = []
    else : 
        dataframe = get_required_dataframe(song_name, dataframe)
        is_model = item_similarity_recommender_py()
        is_model.create(dataframe, 'user_id', 'song')
        if return_dataframe : to_return = is_model.get_similar_items([song_name])
        else : to_return = list(is_model.get_similar_items([song_name])['song'])
    return to_return

input_name = 'Eenie Meenie - Sean Kingston and Justin Bieber'
recommended = generate_link(get_recomendation_song_name(input_name, song_df, return_dataframe=False), return_dictionary=True)
print(recommended)