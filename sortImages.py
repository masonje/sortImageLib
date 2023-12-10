from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import logging
from datetime import datetime
from dateutil import parser
import shutil
import platform
import json

def read_settings_from_json(file_path):
    try:
        with open(file_path, 'r') as json_file:
            settings = json.load(json_file)
            return settings
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def creation_date(path_to_file):
    logger.debug("Getting date for: {}".format(path_to_file))
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            logger.warning("Error getting st_birthtime, returning st_mtime")
            return stat.st_mtime
        
def move_file(source_path, destination_folder):
    try:
        # Ensure the source file exists
        if os.path.isfile(source_path):
            # Ensure the destination folder exists; create it if it doesn't
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            
            # Move the file to the destination folder
            shutil.move(source_path, os.path.join(destination_folder, os.path.basename(source_path)))
            logger.debug(f"File '{source_path}' moved to '{destination_folder}' successfully.")
            return True
        else:
            logger.debug(f"Source file '{source_path}' does not exist.")
            return False
        
    except Exception as e:
        logger.error("Error moving file: {}".format(source_path))
        logger.error(f"Error: {e}")
        return False

def create_folder_path(folder_path):
    try:
        # Use makedirs to create the directory and its parent directories if they don't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.debug(f"Folder path '{folder_path}' created successfully.")
        else:
            logger.debug(f"Folder already exists '{folder_path}'.")
        
        return True
    except OSError as e:
        logger.error(f"Error creating folder path '{folder_path}': {e}")
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

def get_files_recursively(directory_path):
    try:
        # Initialize an empty list to store file names
        files = []

        # Walk through the directory tree using os.walk
        for root, dirs, filenames in os.walk(directory_path):
            # Skip hidden folders by removing them from the list of directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Add the file names to the list
            files.extend([os.path.join(root, file) for file in filenames])

        return files
    except OSError as e:
        print(f"Error: {e}")
        return None

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
    logger.debug("Extract image info for: {}".format(image_path))
    ret={}
    try:
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
                        logger.debug(" -{}:{}".format({tag_name},{value}))
                        #print(f"{tag_name}: {value}")
            else:
                logger.warning("No Exif data found.")
        return ret
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return ret

def prune_log_files(directory_path, max_file_size_bytes):
    try:
        # Walk through the directory tree using os.walk
        for root, dirs, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)

                # Check if the file is a log file and exceeds the max size
                if filename.endswith(".log") and os.path.getsize(file_path) > max_file_size_bytes:
                    print(f"Pruning {file_path}...")
                    
                    # Open the file in write mode to truncate its content
                    with open(file_path, 'w') as log_file:
                        log_file.truncate()

    except OSError as e:
        print(f"Error: {e}")

def exit_error(string_error):
    logger.error("Quitting on error: {}".format(string_error))
    exit(1)

def get_json_value(json_object, key):
    try:
        # Attempt to retrieve the value for the given key
        value = json_object[key]
        return value
    except KeyError:
        print(f"Key '{key}' not found in the JSON object.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    json_file_path = "./settings.json"
    settings = read_settings_from_json(json_file_path)

    log_file_dir = get_json_value(settings, "logDir")
    log_file = get_json_value(settings, "logfile")
    log_file_path = log_file_dir + "/" + log_file
    log_file_path_size = get_json_value(settings, "logfileMaxSize")
    dir_file = get_json_value(settings, "scanRoot")
    dirs_scan = get_json_value(settings, "scanDirs")
    dir_scan_core = get_json_value(settings, "scanDir")
    targetRootDir = get_json_value(settings, "targetRootDir")

    prune_log_files(log_file_dir, int(log_file_path_size))

    logger = setup_logging(log_file_path)
    #logger = setup_logging(log_file_path, logging.DEBUG)
    logger.info("------------------------------------------------------------------------------------------------------")

    logger.info("Base dir for sorting: {}".format(dir_file))
    logger.info("Dir to push file too: {}".format(targetRootDir))

    for ds in dirs_scan:
        dir_scan = "{}/{}/{}".format(dir_file, dir_scan_core, ds)

        logger.info("-------------------")
        logger.info("Scanning dir: {}".format(dir_scan))

        result_list = get_files_recursively(dir_scan)
        logger.info("Number of items returned: {}".format(str(len(result_list))))

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
                fname = os.path.basename(item)

                if file_extension.lower() in ['.jpg','.jpeg']:
                    file_info = extract_metadata(item)
                    if "DateTimeOriginal" in file_info.keys():
                        pdt = file_info['DateTimeOriginal']
                    else:
                        pdt = datetime.utcfromtimestamp(creation_date(item)).strftime(pdt_format)
                    process_file = True

                elif file_extension.lower() == '.gif':
                    pdt = datetime.utcfromtimestamp(creation_date(item)).strftime(pdt_format)
                    process_file = True
                elif file_extension.lower() == '.png':
                    pdt = datetime.utcfromtimestamp(creation_date(item)).strftime(pdt_format)
                    process_file = True

                elif file_extension.lower() == '.mp4':
                    try:
                        fname = fname.strip("VID_")
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
                                    logger.error("Projected date out of expected range 1-31 {}".format(pdt))
                            else:
                                logger.error("Projected month out of expected range 1-12 {}".format(pdt))
                        else:
                            logger.error("Projected year out of expected range 2000-2050 {}".format(pdt))

                        # Failed to get date info from video name.
                        # Pull the information from the file system info. 
                        if process_file == False:
                            logger.info("Pulling date from file system attributes")
                            pdt = datetime.utcfromtimestamp(creation_date(item)).strftime(pdt_format)
                            process_file = True

                    except Exception as err:
                        logger.error("Processing date from file name {}".format(fname))
                        logger.error(f"Unexpected {err=}, {type(err)=}")

                        logger.info("Pulling date from file system attributes")
                        pdt = datetime.utcfromtimestamp(creation_date(item)).strftime(pdt_format)
                        process_file = True
                else:
                    logger.warning("Unknown file type in {}".format(fname) )

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
                        exit_error("Year isn't 4 digits long: " + str(dt.year))

                    dir_move_to = "{}/{}/{}/{}".format(targetRootDir, str(dt.year), dm, dd)
                    if create_folder_path(dir_move_to):
                        logger.debug("Moving {} -to- {}".format(item, dir_move_to))
                        if move_file(item, dir_move_to):
                            logger.info("Successfully moved {} -to- {}".format(fname,dir_move_to.strip(targetRootDir)))
                        else:
                            logger.error("failed to moved {} -to- {}".format(fname,dir_move_to.strip(targetRootDir)))
                else:
                    logger.info("Skipping file: " + item)
        logger.info("Scan/management of dir complete: {}".format(dir_scan))
    logger.info("Script Complete")
