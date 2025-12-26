import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Activation,BatchNormalization,Input,Embedding,Dot,Dense,Flatten
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml


logger = get_logger(__name__)

class RecommendationModel:

    def __init__(self,config_path):
        self.config = read_yaml(config_path)
        logger.info("Reading configuration from config.yaml")

    def base_model(self,num_users,num_animes):
        try:
            logger.info("Model building started")

            embedding_size = self.config["model"]["embedding_size"]

            user = Input(name='user',shape=[1])
            user_embedding = Embedding(name="user_embedding",input_dim=num_users,output_dim=embedding_size)(user)

            anime = Input(name='anime',shape=[1])
            anime_embedding = Embedding(name="anime_embedding",input_dim=num_animes,output_dim=embedding_size)(anime)

            x = Dot(name='dot_product',normalize=True,axes=2)([user_embedding,anime_embedding])
            x = Flatten()(x)
            x = Dense(1,kernel_initializer='he_normal')(x)
            x = BatchNormalization()(x)
            x = Activation("sigmoid")(x)

            model = Model(inputs=[user,anime], outputs=x)
            model.compile(loss = self.config["model"]["loss"],
                        metrics = self.config["model"]["metrics"],
                        optimizer = self.config["model"]['optimizer'] )
            return model
        
        except Exception as e:
            logger.error(f"Error occured during model creation{str(e)}")