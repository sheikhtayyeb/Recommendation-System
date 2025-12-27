from utils.helpers import *
from config.paths_config import *
from pipeline.prediction_pipeline import *

# print(getAnimeFrame(1230,DF_CSV))
# print(getSynopsis(1230,DF_SYNOPSIS_CSV))
# print(find_similar_animes("Two Tea Two",ANIME_WEIGHTS_PATH,ANIME_ID_ENCODED,
#                      ANIME_ID_DECODED,DF_CSV,DF_SYNOPSIS_CSV)
#                         )
# print("++++++++++++++++++++++++++++++++++++++++++++++++")

# similar_users = find_similar_users(4564,
#                     USER_WEIGHTS_PATH,
#                     USER_ID_ENCODED,
#                     USER_ID_DECODED,
#                     num_recommendations = 10)
# user_pref = get_user_preferences(4564,DF_RATING_CSV,DF_CSV)
# recommendations = user_recommendation(similar_users,
#                         user_pref,
#                         DF_CSV,
#                         DF_SYNOPSIS_CSV,
#                         DF_RATING_CSV)

# print(similar_users)
# print("--------------------------------")
# print(user_pref)
# print(".................................")
# print(recommendations)

recommended_animes = hybrid_recommendation(int(5555),
                          user_weightage=0.5, 
                          content_weightage=0.5)
print(recommended_animes)

