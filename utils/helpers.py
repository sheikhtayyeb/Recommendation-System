import pandas as pd
import numpy as np
import joblib
from config.paths_config import *



#### 1. get ANIME frame ####
def getAnimeFrame(anime,path_df):
    df = pd.read_csv(path_df)
    if isinstance(anime,int):
        return df[df.anime_id ==anime]
    
    else:
        return df[df.eng_version ==anime]

#### 2. getSynopsis ####  
def getSynopsis(anime,path_df_synopsis):
    df = pd.read_csv(path_df_synopsis)
    if isinstance(anime,int):
        return df[df.MAL_ID ==anime]['sypnopsis']
    
    else:
        return df[df.Name ==anime]['sypnopsis']


#### 3. Content Recommendation ####
def find_similar_animes(name,path_anime_weights,path_anime_id_encoded,
                        path_anime_id_decoded,path_df,path_df_synopsis,
                        num_recomendations = 10,
                        return_dist = False,
                        neg = False):
    
    anime_weights = joblib.load(path_anime_weights)
    anime_id_encoded = joblib.load(path_anime_id_encoded)
    anime_id_decoded = joblib.load(path_anime_id_decoded)

    df = pd.read_csv(path_df)
    df_synopsis = pd.read_csv(path_df_synopsis)

    index = getAnimeFrame(name,path_df).anime_id.values[0]
    encoded_index = anime_id_encoded.get(index)
    weights = anime_weights

    dists = np.dot(weights,weights[encoded_index])
    sorted_dists = np.argsort(dists)
    # print(sorted_dists)
    # print(np.sort(dists))
    num_recomendations = num_recomendations+1

    if neg:
        closest = sorted_dists[:num_recomendations]

    else:
        closest = np.flip(sorted_dists)[:num_recomendations]

    # print(f"Anime closest to {name}")

    if return_dist:
        return dists, closest
    
    Smilarity_Arr = []
    for close in closest:
        decoded_id = anime_id_decoded.get(close)

        synopsis = getSynopsis(decoded_id,path_df_synopsis)

        anime_frame = getAnimeFrame(decoded_id,path_df)

        anime_name = anime_frame.eng_version.values[0]
        # print(f"anime_name : {anime_name}")

        genre = anime_frame.Genres.values[0]
        # print(f"genre: {genre}")
        
        similarity = dists[close]
        # print(f" similarity: {similarity}")
        Smilarity_Arr.append({
            "anime_id": decoded_id,
            "name": anime_name,
            "similarity":similarity,
            "genre": genre,
            "synopsis":synopsis
        })

    df_out = pd.DataFrame(Smilarity_Arr).sort_values(by = "similarity",ascending =False)
    return df_out[df_out.anime_id != index].drop(['anime_id'],axis=1)


#### 4. get similar user ####
def find_similar_users(item_input,
                       path_user_weights,
                       path_user_id_encoded,
                       path_user_id_decoded,
                       num_recommendations = 10,
                       return_dist=False,
                       neg = False):
    
    user_weights = joblib.load(path_user_weights)
    user_id_encoded = joblib.load(path_user_id_encoded)
    user_id_decoded = joblib.load(path_user_id_decoded)
    index = item_input
    encoded_index = user_id_encoded.get(index)
    weights = user_weights
    dists = np.dot(weights,weights[encoded_index])
    sorted_dists = np.argsort(dists)
    num_recommendations = num_recommendations+1

    if neg:
        closest = sorted_dists[:num_recommendations]

    else:
        closest = np.flip(sorted_dists)[:num_recommendations]

    # print(f"Animes closest to {item_input}")

    if return_dist:
        return dists, closest
    
    Smilarity_Arr = []
    for close in closest:
        
        similarity = dists[close]
        # print(f" similarity: {similarity}")

        if isinstance(item_input,int):
            decode_id = user_id_decoded.get(close)
            Smilarity_Arr.append({
                "similar_user":decode_id,
                "similarity":similarity
            }
            )


    similar_users = pd.DataFrame(Smilarity_Arr).sort_values(by = "similarity",ascending =False)
    return similar_users[similar_users.similar_user != item_input]


#### 5. get user preferences ###
def get_user_preferences(user_id,path_df_rating,path_df,plot=False):

    df_rating = pd.read_csv(path_df_rating)
    df = pd.read_csv(path_df)
    animes_watched_by_user = df_rating[df_rating.user_id ==user_id]
    user_rating_percentile = np.percentile(animes_watched_by_user.rating,75)
    animes_watched_by_user = animes_watched_by_user[animes_watched_by_user.rating>=user_rating_percentile]
    top_anime_by_user = animes_watched_by_user.sort_values(by = "rating",ascending=False).anime_id.values
    df_anime = df[df["anime_id"].isin(top_anime_by_user)]
    df_anime = df_anime[["eng_version","Genres"]]

    return df_anime


#### 6. user recommendation ####
def user_recommendation(similar_users,
                        user_pref,
                        path_df,
                        path_df_synopsis,
                        path_df_rating,
                        num_recommendations = 10
                        ):
    
    df = pd.read_csv(path_df)
    df_synopsis = pd.read_csv(path_df_synopsis)
    df_rating = pd.read_csv(path_df_rating)
    recommended_animes = []
    anime_list = []

    for user_id in similar_users.similar_user.values:
        pref_list = get_user_preferences(user_id,path_df_rating,path_df)
        pref_list = pref_list[~pref_list.eng_version.isin(user_pref.eng_version.values)]

        if not pref_list.empty:
            anime_list.append(pref_list.eng_version.values)
        
    if anime_list:
        df_anime = pd.DataFrame(anime_list)
        sorted_list = pd.DataFrame(pd.Series(df_anime.values.ravel()).value_counts()).head(num_recommendations)
        for i,anime_name in enumerate(sorted_list.index):
            n_user_pref = sorted_list[sorted_list.index ==anime_name].values[0][0]

            if isinstance(anime_name,str):
                anime_frame = getAnimeFrame(anime_name,path_df)
                anime_id = anime_frame.anime_id.values[0]
                # print(anime_id)
                genre = anime_frame.Genres.values[0]
                synopsis = getSynopsis(int(anime_id),path_df_synopsis)
                recommended_animes.append({
                        "num_users_liked":n_user_pref,
                        "anime_name":anime_name,
                        "genre":genre,
                        "synopsis":synopsis
                })

    return pd.DataFrame(recommended_animes).head(num_recommendations)
        
