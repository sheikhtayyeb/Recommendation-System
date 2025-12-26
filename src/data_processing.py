import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
import sys

logger = get_logger(__name__)

class DataProcessor:

    def __init__(self,input_file,output_dir):
        self.input_file = input_file
        self.output_dir = output_dir

        self.df_rating = None
        self.df_anime = None
        self.x_train_array = None
        self.y_train = None
        self.x_test_array = None
        self.y_test = None

        self.user_id_encoded = {}
        self.user_id_decoded = {}
        self.anime_id_encoded = {}
        self.anime_id_decoded = {}

        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("Data Processing initialized")

    def load_data(self,usecols):
        try:
            self.df_rating = pd.read_csv(self.input_file, low_memory=True,usecols=usecols)
            logger.info("Data loaded successfully for Data processing")
        
        except Exception as e:
            raise CustomException("Falied to load data",sys)
        
    def filter_users(self, min_rating = 400):
        try:
            n_rating = self.df_rating['user_id'].value_counts()
            n_rating = n_rating[n_rating >=min_rating]
            self.df_rating["user_to_keep"] = self.df_rating['user_id'].apply(lambda i: True  if i in n_rating.index else False )
            self.df_rating = self.df_rating[self.df_rating["user_to_keep"]==True]
            self.df_rating.drop(columns = ["user_to_keep"],inplace=True)

            logger.info("Filtered users succesfully")
        
        except Exception as e:
            raise CustomException("Falied to filter data",sys)

    def scale_rating(self):
        try:
            min_rating =  min(self.df_rating['rating'])
            max_rating = max(self.df_rating['rating'])
            # average_rating = self.df_rating['rating'].mean()
            self.df_rating['rating'] = self.df_rating['rating'].apply(lambda i: (i- min_rating)/(max_rating-min_rating))

            logger.info("Rating are scaled suceesfully")

        except Exception as e:
            raise CustomException("Falied to scale data",sys)

    def encode_decode_data(self):
        try:
            logger.info("Creating mapping for encoding and decoding user_id")
            user_id = self.df_rating["user_id"].unique().tolist()
            self.user_id_encoded = {id: encode  for encode,id in enumerate(user_id)}
            self.user_id_decoded = {decode: id  for decode,id in enumerate(user_id)}
            self.df_rating["user_id_encoded"] = self.df_rating["user_id"].apply(lambda i :self.user_id_encoded[i] )

            logger.info("Creating mapping for encoding and decoding anime_id")
            anime_id = self.df_rating["anime_id"].unique().tolist()
            self.anime_id_encoded = {id: encode  for encode,id in enumerate(anime_id)}
            self.anime_id_decoded = {decode: id  for decode,id in enumerate(anime_id)}
            self.df_rating["anime_id_encoded"]= self.df_rating["anime_id"].apply(lambda i :self.anime_id_encoded[i] )

            logger.info("Encoded and Decoded user_ids and anime_ids sucessfully")

        except Exception as e:
            raise CustomException("Falied to encode/decode data",sys)
        
    def split_data(self, train_test_split = 0.01):
        try:
            self.df_rating=self.df_rating.sample(frac=1,random_state=43).reset_index(drop=True)
            x = self.df_rating[['user_id_encoded','anime_id_encoded']]
            y = self.df_rating[['rating']]

            total_size = len(x)
            train_size = int((1-train_test_split)*total_size)
            x_train = x[:train_size]
            self.y_train = y[:train_size]
            x_test = x[train_size:]
            self.y_test = y[train_size:]

            self.x_train_array = [x_train.iloc[:,0],x_train.iloc[:,1]]
            self.x_test_array = [x_test.iloc[:,0],x_test.iloc[:,1]]

            logger.info(f"Data splitted with training data: {train_size} samples and test data: {total_size-train_size} samples")

        except Exception as e:
            raise CustomException("Falied to aplit data",sys)

    def save_artifacts(self):
        try:
            artifacts = {
                "user_id_encoded": self.user_id_encoded,
                "user_id_decoded": self.user_id_decoded,
                "anime_id_encoded": self.anime_id_encoded,
                "anime_id_decoded": self.anime_id_decoded
            }

            for name, data in artifacts.items():
                joblib.dump(data , os.path.join(self.output_dir,f"{name}.pk"))
                logger.info(f"file {name}.pk saved at {self.output_dir}")

            joblib.dump(self.x_train_array, X_TRAIN_ARRAY)
            joblib.dump(self.x_test_array, X_TEST_ARRAY)
            joblib.dump(self.y_train, Y_TRAIN)
            joblib.dump(self.y_test, Y_TEST)
            self.df_rating.to_csv(DF_RATING_CSV, index=False)

            logger.info("Training, testing data, df_rating , ancoding and decodings saved successfully")

        except Exception as e:
            raise CustomException("Falied to save processed data",sys)

    def getAmineName(self,anime_id,df):
        name = df[df.anime_id == anime_id].eng_version.values[0]
        if name is np.nan:
            name = df[df.anime_id == anime_id].Name.values[0]

        return name
    
    def process_anime_data(self):
        try:
            df = pd.read_csv(ANIME_CSV,low_memory=True)

            cols = ["MAL_ID","Name","Genres","sypnopsis"]
            df_synopsis = pd.read_csv(ANIME_WITH_SYNOPSIS_CSV,usecols=cols)

            df.replace("Unknown",np.nan,inplace=True)

            df["anime_id"] = df["MAL_ID"]
            df["eng_version"] = df["English name"]
            df["eng_version" ] = df.anime_id.apply(lambda id :self.getAmineName(id,df))

            df.sort_values(by = ["Score"],
                            inplace=True,
                            ascending=False,
                            kind = 'quicksort',
                            na_position = 'last'
                          )
            
            df = df [["anime_id","eng_version","Score","Genres",
                         "Episodes","Type","Premiered","Members"]]
            df.to_csv(DF_CSV,index=False)
            df_synopsis.to_csv(DF_SYNOPSIS_CSV,index=False)

            logger.info("df and df_synopsis saved succesfully  ...")

        except Exception as e:
            raise CustomException("Falied to save process_anime_data",sys)

    def run(self):
        try:
            self.load_data(usecols = ["user_id","anime_id","rating"])
            self.filter_users(min_rating = 400)
            self.scale_rating()
            self.encode_decode_data()
            self.split_data(train_test_split=0.01)
            self.save_artifacts()
            self.process_anime_data()

            logger.info("Data processing suceesfully completed")
        
        except Exception as e:
            logger.error(str(e))
            raise CustomException("Data processing pipeline failed",sys)
        
if __name__ == "__main__":
    data_processor = DataProcessor(input_file= ANIMELIST_CSV,
                                   output_dir= PROCESSED_DIR)
    data_processor.run()
    



            
        
