from src.data_processing import DataProcessor
from src.model_training import ModelTraining
from utils.common_functions import read_yaml
from config.paths_config import *
from src.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    
    data_processor = DataProcessor(input_file= ANIMELIST_CSV,
                                   output_dir= PROCESSED_DIR)
    data_processor.run()
    trainer = ModelTraining(PROCESSED_DIR)
    model = trainer.train_model()
    trainer.save_model_weights(model)

