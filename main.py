# - metadata tags baked into the files and an external library file, such that if the metadata is accidentally stripped during a file transfer, can reference and re-update files via the library (trivial)
# - image recognition / tag suggestion (extremely difficult problem as posted by @grandpa on google photos)
# - freeform text search of tags (trivial to get "good enough")
# - color detection (medium difficulty problem, is a matter of what method is used to determine "average" colors
# - Pay for api calls?

import os
import shutil
import hashlib
from PIL import Image
from PIL import UnidentifiedImageError
import imagehash
import pytesseract
import cv2
import ctoken
from PIL.ExifTags import TAGS
import pathlib
import datetime
from collections import defaultdict
import json
from PIL.ExifTags import GPSTAGS
from PIL.TiffImagePlugin import IFDRational
import colorgram
import numpy
import time

# EXTRACT --------------------------------------------------------------
def traverse(path_directory: str, dest: str, other:str, valid_extensions: set):
    """
    Flattens files from path, copies unique files (no duplicates) to destination.
    On Windows, should preserve file metadata.
    :param path_directory: path to be traversed.
    :param dest: destination directory files will be copied to.
    :param other: directory where non valid files are sent
    :param valid_extensions: set of valid file extensions without period (IE {"zip", "pdf"})
    :return: void return
    """
    output_store_filename = "metadata.dat"
    bad_file_store_filename = "bad-files.log"
    all_file_paths = set()
    unique_files = dict()  # {hash:path}
    metadata_dict = dict()  # {hash:{metadata:str}} # date created, location,
    '''
    0x9003	DateTimeOriginal	string	ExifIFD	(date/time when original image was taken)
    0x9004	CreateDate	string	ExifIFD	(called DateTimeDigitized by the EXIF spec.)
    0x9010	OffsetTime	string	ExifIFD	(time zone for ModifyDate)
    0x9011	OffsetTimeOriginal	string	ExifIFD	(time zone for DateTimeOriginal)
    0x9012	OffsetTimeDigitized	string	ExifIFD	(time zone for CreateDate)
    36867	0×9003	ASCII string	Date Taken	YYYY:MM:DD HH:MM:SS
    36868	0×9004	ASCII string	Date Created	YYYY:MM:DD HH:MM:SS
    '''
    bad_files = list()
    # Make Directory
    try:
        os.mkdir(dest)
    except FileExistsError:
        pass

    # file_count = sum([len(files) for root, _dirs, files in os.walk(path)])
    # print("file count", file_count)

    # Traverse Files
    for root, _dirs, files in os.walk(path_directory):
        for filename in files:
            if os.path.splitext(filename)[1].strip(".").lower() in valid_extensions:  # file extension
                try:
                    # Make Hash of File
                    # filename_hash = imagehash.phash(Image.open(os.path.join(root, filename)))
                    filename_hash = imagehash.whash(Image.open(os.path.join(root, filename)))
                    # Adding filenames to dict removes duplicate files
                    if filename_hash in unique_files.keys():
                        print("adding hash duplicate to bad files:", os.path.join(root, filename))
                        bad_files.append(os.path.join(root, filename))
                        # os.remove(os.path.join(root, filename))
                    else:
                        # Add to Filename Store
                        all_file_paths.add(os.path.join(root, filename))
                        # folder = os.path.basename(root)
                        unique_files[filename_hash] = os.path.join(root, filename)
                except UnidentifiedImageError:
                    print("error, potentially bad filename. adding to bad files:", filename)
                    bad_files.append(os.path.join(root, filename))
    print("all valid files", len(all_file_paths))
    print("all unique files", len(unique_files))
    dup_count = 0
    for file_hash_key in unique_files.keys():
        file_directory = unique_files[file_hash_key]
        try:
            shutil.copy2(file_directory, dest)
            metadata_dict[str(file_hash_key)] = extract_metadata(file_directory).copy()
        except shutil.Error:
            while True:
                dup_count += 1
                # full = os.path.basename(file_path)
                # filename = os.path.splitext(full)[0]
                extension = os.path.splitext(file_directory)[1].lower()
                final_des = os.path.join(dest, f"fd-{dup_count}{extension}")
                if os.path.exists(final_des):
                    break
                else:
                    metadata_dict[str(file_hash_key)] = extract_metadata(file_directory).copy()
                    shutil.copy2(file_directory, final_des)
                    break
        # LOAD AND RESIZE IMAGE
        t1 = time.perf_counter()
        img = Image.open(file_directory)
        orig_size = img.size
        MINIMUM_SIZE = (900,900)
        if img.size[0] > MINIMUM_SIZE[0] or img.size[1] > MINIMUM_SIZE[1]:
            diff = MINIMUM_SIZE[0]/max(img.size)
            x = int((img.size[0] * diff))
            y = int((img.size[1] * diff))
            img = img.resize((x, y), resample=Image.BILINEAR)
        # EXTRACT COLOR
        metadata_dict[str(file_hash_key)]["colors"] = colors(img)
        # TEXT EXTRACTION
        metadata_dict[str(file_hash_key)]["text"] = image2string(img)

        # MAYBE DO TAG SUGGESTION?
        print(f"{os.path.basename(file_directory)} ResizeXY:{orig_size}->{img.size} {time.perf_counter()-t1} milliseconds")
        print(metadata_dict[str(file_hash_key)]["text"])
    print("bad files:")
    print(bad_files)
    return metadata_dict


def get_coordinates(exif_gps_data):
    """
    Helper from https://developer.here.com/blog/getting-started-with-geocoding-exif-image-metadata-in-python3
    :param exif_gps_data:
    :return:
    """
    def get_decimal_from_dms(dms, ref):
        degrees = float(dms[0])
        minutes = float(dms[1]) / 60.0
        seconds = float(dms[2]) / 3600.0
        if ref in ['S', 'W']:
            degrees = -degrees
            minutes = -minutes
            seconds = -seconds
        return round(degrees + minutes + seconds, 10)

    lat = get_decimal_from_dms(exif_gps_data['GPSLatitude'], exif_gps_data['GPSLatitudeRef'])
    lon = get_decimal_from_dms(exif_gps_data['GPSLongitude'], exif_gps_data['GPSLongitudeRef'])
    return (lat,lon)


def extract_metadata(file_path:str) -> dict:
    """
    Extracts relevant exif and OS file metadata if possible: (earliest) date created, GPS data, camera model.
    :param image_file:
    :return: dictionary {exif_tag_name:}
    """
    valid_tagID = {306, 36867, 36868, 272, 271, 34853}
    # cr date, cr date, cr date, camera model, camera make, gps data
    valid_gps_tags = {"GPSAltitude", "GPSLongitude", "GPSLatitude", "GPSLatitudeRef", "GPSLongitudeRef"}
    metadata_entry = dict()
    metadata_entry["DateTime"] = dict()
    exifdata = Image.open(file_path).getexif()
    for tag_id in exifdata:
        try:
            if tag_id in valid_tagID:
                tag = TAGS.get(tag_id, tag_id)  # tag name
                data = exifdata.get(tag_id)
                # GPS TAG
                if tag_id == 34853:
                    exif_gps_data = {val:data[key] for (key, val) in GPSTAGS.items()
                                           if key in data and val in valid_gps_tags}
                    # Cleaning up IFDRational types to floats
                    for key in exif_gps_data.keys():
                        if type(exif_gps_data[key]) == IFDRational:
                            exif_gps_data[key] = float(exif_gps_data[key])
                        if type(exif_gps_data[key]) == tuple:
                            exif_gps_data[key] = list(exif_gps_data[key])
                            for index, val in enumerate(exif_gps_data[key]):
                                exif_gps_data[key][index] = float(exif_gps_data[key][index])
                    metadata_entry[tag] = exif_gps_data
                    metadata_entry["GPSInfo"]["GPSCoordinates"] = get_coordinates(exif_gps_data)
                # DATETIME TAG(S)
                elif tag_id == 306 or tag_id == 36867 or tag_id == 36868:
                    date_time_obj = datetime.datetime.strptime(data, '%Y:%m:%d %H:%M:%S')
                    metadata_entry["DateTime"][tag] = date_time_obj
                # OTHER TAG(S)
                else:
                    metadata_entry[tag] = data
                    # decode bytes
                    # if isinstance(data, bytes):
                    #     print(data)
                    #     data = str.encode(data, 'utf-8').decode()
                    #     print(data)
                    #     # data = data.decode()
                    # print(f"{tag_id}-{tag:25}: {data}")
        except UnicodeDecodeError:
            pass
    metadata_entry["DateTime"]["OSDateTime"] = datetime.datetime.fromtimestamp(pathlib.Path(file_path).stat().st_ctime)
    metadata_entry["DateTime"] = min(metadata_entry["DateTime"].values()).strftime("%Y-%m-%d %H:%M:%S")
    metadata_entry["folder"] = os.path.basename(os.path.dirname(file_path))
    metadata_entry["hash_scheme"] = "whash"
    metadata_entry["original_filename"] = os.path.basename(file_path)
    return metadata_entry


def write_metadata(metadata_dict:dict, metadata_filename="metadata.txt"):
    with open(metadata_filename, "w") as f:
        json.dump(metadata_dict, f)

# PROCESSING --------------------------------------------------------------
def image2string(PIL_image):
    img = PIL_image

    img = numpy.array(img.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # greyscale

    token_array = dict()
    token_array["norm"] = ctoken.tokenize(pytesseract.image_to_string(img, lang='eng').strip())  # tokenize

    img = cv2.bitwise_not(img)
    token_array["invert"] = ctoken.tokenize(pytesseract.image_to_string(img, lang='eng').strip())  # tokenize

    img = cv2.threshold(img, 0, 255, type=cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]  # threshold
    token_array["threshold"] = ctoken.tokenize(pytesseract.image_to_string(img, lang='eng').strip())  # tokenize

    final_tokens = max(sorted(token_array.items(), key=lambda x: len(x[1])))[1]

    return final_tokens


def colors(PIL_image, count=8):
    """
    Extracts colors from the image.
    :param image_filename: image filename
    :param count: number of colors to generate
    :return:
    """
    img = PIL_image
    # EXTRACT COLOR
    colors = colorgram.extract(img, count)
    return colors


if __name__ == "__main__":
    valid_file_extentions = {"gif", "jpg", "jpeg", "jpeg-large", "png", "webp"}
    # path = "/Users/connerward/Desktop"
    path_directory = "/Users/connerward/PycharmProjects/ImageTools/images"
    destination = "/Users/connerward/Documents/output-files"
    other_files_dest = "/Users/connerward/Documents/non-output-files"

    # EXTRACT / PROCESS --------------------------------
    # Flattens files from path, copies unique files (no duplicates) to destination, outputs metadata
    raw_file_metadata = traverse(path_directory=path_directory,
                                 dest=destination, other=other_files_dest,
                                 valid_extensions=valid_file_extentions)
    # # WRITE --------------------------------
    # # write_metadata(raw_file_metadata)