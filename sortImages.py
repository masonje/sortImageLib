from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import logging
from datetime import datetime
from dateutil import parser
import dateparser

def parse_unknown_format_datetime(datetime_str):
    try:
        # Attempt to parse the datetime string
        parsed_datetime = dateparser.parse(datetime_str)
        
        if parsed_datetime:
            return parsed_datetime
        else:
            print(f"Unable to parse datetime string: {datetime_str}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def setup_logging(log_file_path='app.log', log_level=logging.INFO):
    """
    Set up logging configuration.

    Parameters:
        log_file_path (str): Path to the log file.
        log_level (int): Logging level (default is INFO).

    Returns:
        logging.Logger: Configured logger.
    """
    # Create the log directory if it doesn't exist
    log_directory = os.path.dirname(log_file_path)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Create a logger and set the level
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Create a file handler and add it to the logger
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create a console handler and add it to the logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def list_all_files_and_folders(directory):
    result = []
    
    def recursive_list(current_directory):
        try:
            with os.scandir(current_directory) as entries:
                for entry in entries:
                    result.append(entry.path)
                    if entry.is_dir():
                        recursive_list(entry.path)
        except FileNotFoundError:
            print(f"The specified directory '{current_directory}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred: {e}")
            #quit()
        

    # Start the recursive listing
    recursive_list(directory)
    return result

def write_to_file(file_path, content):
    try:
        with open(file_path, 'a') as file:
            file.write(content + '\n')
        print(f"Content successfully written to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_metadata(image_path):
    # Open the image
    ret = {}
    with Image.open(image_path) as img:
        # Get the Exif data
        exif_data = img._getexif()

        # Check if there is any Exif data
        if exif_data is not None:
            # Iterate through Exif data and print metadata
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if "date" in tag_name.lower():
                    ret[tag_name] = value
                    print(f"{tag_name}: {value}")
        else:
            print("No Exif data found.")
    return ret

if __name__ == "__main__":
    log_file_path = "logs/sortImages.log"
    logger = setup_logging(log_file_path)

    directory_path = "/run/user/1000/gvfs/smb-share:server=nas.local,share=pictures/CameraUploads/Alternate/"
    result_list = list_all_files_and_folders(directory_path)

    for item in result_list:
        logger.debug("File: " + item)
        if os.path.isdir(item):
            logger.debug("Skipping folder " + item)
        else:
            split_tup = os.path.splitext(item)
            file_name = split_tup[0]
            file_extension = split_tup[1]

            pdt = '2000:00:00:00 00:00:00'

            if file_extension == '.jpg':
                file_info = extract_metadata(item)
                if "DateTimeOriginal" in file_info.keys():
                    pdt = file_info['DateTimeOriginal']

            x = parse_unknown_format_datetime(pdt)
            dt = datetime.strptime(pdt, '%Y:%m:%d %H:%M:%S')

            print(dt.year, dt.month, dt.day)




    # extract_metadata(image_path)



# if __name__ == "__main__":
#     directory_path = "/run/user/1000/gvfs/smb-share:server=nas.local,share=pictures/CameraUploads/"

#     log_file_path = "logs/deadboltCleanup.log"
#     logger = setup_logging(log_file_path)

    
#     skip_this=["@Recycle",".Trash-1000", "@Recently-Snapshot", '.syncing_db','.@QNAPCloudDriveSyncTemp_0_1']
#     items = os.listdir(directory_path)
#     directories = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]


#     for d in directories:
#         if d not in skip_this:
#             print("Loading " + d)
#             copy_files_over(directory_path + "/" + d)