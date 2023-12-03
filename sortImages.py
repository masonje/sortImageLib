from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import logging
from datetime import datetime
from dateutil import parser
import shutil

def move_file(source_path, destination_folder):
    try:
        # Ensure the source file exists
        if os.path.isfile(source_path):
            # Ensure the destination folder exists; create it if it doesn't
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            
            # Move the file to the destination folder
            shutil.move(source_path, os.path.join(destination_folder, os.path.basename(source_path)))
            print(f"File '{source_path}' moved to '{destination_folder}' successfully.")
            return True
        else:
            print(f"Source file '{source_path}' does not exist.")
            return False
        
    except Exception as e:
        print(f"Error moving file: {e}")
        return False

def create_folder_path(folder_path):
    try:
        # Use makedirs to create the directory and its parent directories if they don't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder path '{folder_path}' created successfully.")
        else:
            print(f"Folder already exists '{folder_path}'.")
        
        return True
    except OSError as e:
        print(f"Error creating folder path '{folder_path}': {e}")
        return False
    
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
                    #print(f"{tag_name}: {value}")
        else:
            print("No Exif data found.")
    return ret

def exit_error(string_error):
    logger.error("Quitting on error: {}".format(string_error))
    quit(1)

if __name__ == "__main__":
    log_file_path = "logs/sortImages.log"
    logger = setup_logging(log_file_path)

    dir_file = "/run/user/1000/gvfs/smb-share:server=nas.local,share=pictures/"
    dir_scan = dir_file + "CameraUploads/Camera/"

    result_list = list_all_files_and_folders(dir_scan)

    for item in result_list:
        logger.debug("File: " + item)
        if os.path.isdir(item):
            logger.debug("Skipping folder " + item)
        else:
            split_tup = os.path.splitext(item)
            file_name = split_tup[0]
            file_extension = split_tup[1]

            process_file = False
            pdt = '2000:01:01 00:00:00'
            pdt_format = '%Y:%m:%d %H:%M:%S'

            if file_extension == '.jpg':
                file_info = extract_metadata(item)
                if "DateTimeOriginal" in file_info.keys():
                    pdt = file_info['DateTimeOriginal']
                process_file = True
            elif file_extension == '.mp4':
                fname = os.path.basename(item)
                dy = fname[:4]
                dm = fname[4:6]
                dd = fname[6:8]
                pdt = "{}:{}:{} 00:00:00".format(dy, dm, dd)
                logger.debug("Format build: {}".format(pdt))

                #validate all of the date values pulled
                if int(dy) in range(2000, 2050):
                    if int(dm) in range(1, 13):
                        if int(dd) in range(1, 32):
                            process_file = True
                        else:
                            exit_error("Projected date out of expected range 1-31 {}".format(pdt))
                    else:
                        exit_error("Projected month out of expected range 1-12 {}".format(pdt))
                else:
                    exit_error("Projected year out of expected range 2000-2050 {}".format(pdt))

            #ensure we want to process that type of file
            if process_file:
                dt = datetime.strptime(pdt, pdt_format)
                if (len(str(dt.month)) == 1):
                    dm = "0" + str(dt.month)
                else:
                    dm = str(dt.month)

                if (len(str(dt.day)) == 1):
                    dd = "0" + str(dt.day)
                else:
                    dd = str(dt.day)

                if (len(str(dt.year)) != 4):
                    exit_error("Year isn't 4 digets long: " + str(dt.year))

                dir_move_to = dir_file + str(dt.year) + "/" + dm + "/" + dd + "/"
                if create_folder_path(dir_move_to):
                    if move_file(item, dir_move_to):
                        logger.info("Successfully moved " + item + " -to- " + dir_move_to)
                    else:
                        logger.error("failed to moved " + item + " -to- " + dir_move_to)
            else:
                logger.info("Skipping file: " + item)
