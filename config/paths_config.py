import os

#### Data Ingestion ####
RAW_DIR = "artifacts/raw"
CONFIG_PATH = "config/config.yaml"


### Data processing ###
PROCESSED_DIR = "artifacts/processed"
ANIMELIST_CSV = "artifacts/raw/animelist.csv"
ANIME_CSV = "artifacts/raw/anime.csv"
ANIME_WITH_SYNOPSIS_CSV = "artifacts/raw/anime_with_synopsis.csv"

X_TRAIN_ARRAY = os.path.join(PROCESSED_DIR, "x_train_array.pk")
X_TEST_ARRAY = os.path.join(PROCESSED_DIR, "x_test_array.pk")
Y_TRAIN = os.path.join(PROCESSED_DIR, "y_train.pk")
Y_TEST = os.path.join(PROCESSED_DIR, "y_test.pk")
DF_RATING_CSV = os.path.join(PROCESSED_DIR, "df_rating.csv")
DF_CSV = os.path.join(PROCESSED_DIR, "df.csv")
DF_SYNOPSIS_CSV = os.path.join(PROCESSED_DIR, "df_synopsis.csv")

USER_ID_ENCODED = os.path.join(PROCESSED_DIR,"user_id_encoded.pk")
USER_ID_DECODED = os.path.join(PROCESSED_DIR,"user_id_decoded.pk")

ANIME_ID_ENCODED = os.path.join(PROCESSED_DIR,"anime_id_encoded.pk")
ANIME_ID_DECODED = os.path.join(PROCESSED_DIR,"anime_id_decoded.pk")


### Model storage ###
MODEL_DIR = "artifacts/models"
WEIGHTS_DIR = "artifacts/weights"
MODEL_PATH = os.path.join(MODEL_DIR, "model.h5")
ANIME_WEIGHTS_PATH = os.path.join(WEIGHTS_DIR,"anime_weights.pk")
USER_WEIGHTS_PATH = os.path.join(WEIGHTS_DIR,"user_weights.pk")
CHECKPOINT_MODEL_FILE_PATH = "artifacts/model_checkpoint/weights.weights.h5"