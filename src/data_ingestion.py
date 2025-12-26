import os
import pandas as pd
from google.cloud import storage
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:

    def __init__(self,config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.folder_name = self.config["bucket_folder_name"]
        self.file_names =  self.config["bucket_file_name"]

        os.makedirs(RAW_DIR, exist_ok= True )

        logger.info("Data Ingestion class intialized")

    def download_from_gcp(self):
        try:

            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blobs = bucket.list_blobs(prefix = self.folder_name)
            for blob in blobs:
                #print(blob.name)
                if blob.name == self.folder_name:
                    continue

                relative_path = blob.name[len(self.folder_name):]

                if not relative_path:
                    continue
                file_path = os.path.join(RAW_DIR, relative_path)

                if blob.name == "mlops-project-2-rhic/animelist.csv":
                    # gcs_path = f"gs://{self.bucket_name}/{blob.name}"
                    # print(gcs_path)
                    blob.download_to_filename(file_path)
                    # bytes_data = blob.download_as_bytes()

                    data = pd.read_csv(file_path,nrows=5000000)
                    data.to_csv(file_path, index=False)

                    logger.info("Download 5 million rows from animelist.csv ")

                else:
                    blob.download_to_filename(file_path) 
                    logger.info("Downloading other files")
        
        except Exception as e:
            logger.error("Error while downloading data from GCP")
            raise CustomException("Failed to download data from GCP",e)

    def run(self):
        try:
            logger.info("Starting data ingestion process")
            self.download_from_gcp()
            logger.info("Data ingestion completed")
        
        except Exception as e:
            logger.error(f"CustomException: {str(e)}")
        
        finally:
            logger.info("Data Injestion done ... ... ...")

if __name__  == "__main__":
    data_loader = DataIngestion(read_yaml(CONFIG_PATH))
    data_loader.run()



