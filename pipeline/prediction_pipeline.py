from config.paths_config import *
from utils.helpers import *



def hybrid_recommendation(user_id,
                          user_weightage=0.5, 
                          content_weightage=0.5
                          ):
    
    # User recommendation
    similar_users = find_similar_users(user_id,
                                       USER_WEIGHTS_PATH,
                                       USER_ID_ENCODED,
                                       USER_ID_DECODED,
                                       num_recommendations=10)
    
    user_pref = get_user_preferences(user_id,DF_RATING_CSV,DF_CSV)

    user_recommended_animes =   user_recommendation(similar_users,
                        user_pref,
                        DF_CSV,
                        DF_SYNOPSIS_CSV,
                        DF_RATING_CSV)
    
    user_recommended_animes_list =  user_recommended_animes["anime_name"].to_list()
    # print(user_recommended_animes_list)
    # content recommendation
    
    content_recommended_animes = []
    for anime in user_recommended_animes_list:
        similar_animes = find_similar_animes(anime,
                                             ANIME_WEIGHTS_PATH,
                                             ANIME_ID_ENCODED,
                                             ANIME_ID_DECODED,
                                             DF_CSV,
                                             DF_SYNOPSIS_CSV,
                                            num_recomendations = 10,
                                            return_dist = False,
                                            neg = False)
        
        if similar_animes is not None and not similar_animes.empty:
            content_recommended_animes.extend(similar_animes["name"].to_list())
        else:
            print(f"No similar anime found for anime: {anime}")
    # print(content_recommended_animes)

    combined_scores = {}
    for anime in user_recommended_animes_list:
        combined_scores[anime] = combined_scores.get(anime,0) + user_weightage
    for anime in content_recommended_animes:
        combined_scores[anime] = combined_scores.get(anime,0) + content_weightage
    sorted_animes = sorted(combined_scores.items(),key = lambda i : i[1] ,reverse = True)
    return [anime for anime,score in sorted_animes[:10]]
