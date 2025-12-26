import os
import comet_ml
import joblib
import numpy as np
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from src.base_model import RecommendationModel

logger = get_logger(__name__)

class ModelTraining:

    def __init__(self,data_path):

        self.data_path = data_path
        logger.info("Model training initialized")
        self.experiment = comet_ml.Experiment(
            api_key="7Fw5Ymzl85n7s6Pfurlb04fQw",
            project_name="mlops-recommendation-system",
            workspace="mohammad-tayyeb-sheikh"
        )
        logger.info("Model training and COMET ML initialized ...")

    def load_data(self):
        try:
            x_train_array = joblib.load(X_TRAIN_ARRAY)
            x_test_array = joblib.load(X_TEST_ARRAY)
            y_train = joblib.load(Y_TRAIN)
            y_test  = joblib.load(Y_TEST)

            logger.info("Data loaded successfully for Model training")
            return x_train_array,x_test_array,y_train,y_test
        
        except Exception as e:
            logger.error("data loading for model training failed")
            raise CustomException("data loading for model training failed",e)
    
    def lrfn(self,epoch,ramup_epochs,sustain_epochs,start_lr,min_lr,max_lr,exp_decay):
        if epoch > ramup_epochs:
            return (max_lr-start_lr)/ramup_epochs*epoch + start_lr
        
        elif epoch < ramup_epochs + sustain_epochs:
            return max_lr
        
        else:
            return (max_lr-min_lr)*exp_decay**(epoch-ramup_epochs-sustain_epochs) + min_lr


    def train_model(self):
        try:
            x_train_array,x_test_array,y_train,y_test = self.load_data()
            num_users = len(joblib.load(USER_ID_ENCODED))
            num_animes = len(joblib.load(ANIME_ID_ENCODED))
            recommender = RecommendationModel(CONFIG_PATH)
            model = recommender.base_model(num_users,num_animes)
            start_lr = 1e-5
            min_lr = 1e-4
            max_lr = 5e-5
            batch_size = 10000
            ramup_epochs = 5
            sustain_epochs = 0
            exp_decay = 0.8

            lr_callback = LearningRateScheduler( 
                                    lambda epoch: self.lrfn(epoch,ramup_epochs,
                                                            sustain_epochs,
                                                            start_lr,min_lr,
                                                            max_lr,exp_decay),
                                                 verbose = 0)
            model_checkpoint = ModelCheckpoint(filepath=CHECKPOINT_MODEL_FILE_PATH,
                                   save_weights_only =True,
                                   monitor="val_loss",
                                   mode = "min",
                                   save_best_only=True)
            early_stopping = EarlyStopping(patience=4 ,# after 3 epochs, no improvement in performance
                                monitor = "val_loss",
                                restore_best_weights = True
                                )    
            my_callbacks = [model_checkpoint,lr_callback,early_stopping] 

            os.makedirs(os.path.dirname(CHECKPOINT_MODEL_FILE_PATH),exist_ok=True)
            os.makedirs(MODEL_DIR,exist_ok=True)
            os.makedirs(WEIGHTS_DIR,exist_ok=True)

            logger.info("Starting training the model on training data")
            history = model.fit(
                                x = x_train_array,
                                y = y_train,
                                batch_size = batch_size,
                                epochs = 20,
                                verbose =1,
                                validation_data = (x_test_array,y_test),
                                callbacks = my_callbacks
                                )   
            model.load_weights(CHECKPOINT_MODEL_FILE_PATH)
            logger.info("Model training completed")

            for epoch in range(len(history.history['loss'])):
                train_loss = history.history['loss'][epoch]
                val_loss = history.history['val_loss'][epoch]

                self.experiment.log_metric("train_loss",train_loss,step=epoch)
                self.experiment.log_metric("val_loss",val_loss,step=epoch)

            return model
        
        except Exception as e:
            logger.error(f"model training failed {str(e)}")
            raise CustomException("model training failed",e)
    
    def save_model_weights(self,model):
        try:
            # print(dir(model))
            model.save(MODEL_PATH)
            logger.info(f"Model saved to {MODEL_PATH}")
            anime_weights = model.get_layer("anime_embedding").get_weights()[0]
            user_weights = model.get_layer("user_embedding").get_weights()[0]
            joblib.dump(anime_weights,ANIME_WEIGHTS_PATH)
            joblib.dump(user_weights,USER_WEIGHTS_PATH)

            self.experiment.log_asset(MODEL_PATH)
            self.experiment.log_asset(ANIME_WEIGHTS_PATH)
            self.experiment.log_asset(USER_WEIGHTS_PATH)

            logger.info("user and anime weights saved successfully")

        except Exception as e:
            logger.error(f"Error during saving model and weights {str(e)}")
            raise CustomException("Error during saving model and weights",e)            

if __name__ == "__main__":
    trainer = ModelTraining(PROCESSED_DIR)
    model = trainer.train_model()
    trainer.save_model_weights(model)
