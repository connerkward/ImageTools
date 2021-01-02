
# - metadata tags baked into the files and an external library file, such that if the metadata is accidentally stripped during a file transfer, can reference and re-update files via the library (trivial)
# - image recognition / tag suggestion (extremely difficult problem as posted by @grandpa on google photos) - freeform text search of tags (trivial to get "good enough")
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


def traverse(path: str, dest: str, other:str, valid_extensions: set) -> None:
    """
    Flattens files from path, copies unique files (no duplicates) to destination.
    On Windows, should preserve file metadata.
    :param path: path to be traversed.
    :param dest: destination directory files will be copied to.
    :param other: directory where non valid files are sent
    :param valid_extensions: set of valid file extensions without period (IE {"zip", "pdf"})
    :return: void return
    """
    output_store_filename = "index.dat"
    all_file_paths = set()
    unique_files = dict()
    bad_files = list()
    # Make Directory
    try:
        os.mkdir(dest)
    except FileExistsError:
        pass

    # file_count = sum([len(files) for root, _dirs, files in os.walk(path)])
    # print("file count", file_count)

    # Traverse Files
    for root, _dirs, files in os.walk(path):
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
                        unique_files[filename_hash] = os.path.join(root, filename)
                except UnidentifiedImageError:
                    print("error, potentially bad filename. adding to bad files:", filename)
                    bad_files.append(os.path.join(root, filename))
    print("all valid files", len(all_file_paths))
    print("all unique files", len(unique_files))
    dup_count = 0
    for file_hash_key in unique_files.keys():
        file_path = unique_files[file_hash_key]
        try:
            shutil.copy2(file_path, dest)
        except shutil.Error:
            while True:
                dup_count += 1
                full = os.path.basename(file_path)
                print(full)
                filename = os.path.splitext(full)[0]
                extension = os.path.splitext(file_path)[1].lower()
                final_des = os.path.join(dest, f"fd-{dup_count}{extension}")
                if os.path.exists(final_des):
                    break
                else:
                    shutil.copy2(file_path, final_des)
                    print(final_des)
                    break
    print("bad files:")
    print(bad_files)
    # Logs
    # os.remove(output_store_filename)
    # with open(output_store_filename, "w") as f:
    #     for file_hash in unique_files.keys():
    #         f.write(f"{unique_files[file_hash]}\n")

def image2string(path):
    img = cv2.imread(path)  # read file
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # greyscale
    img = cv2.threshold(img, 0, 255, type=cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]  # threshold
    return ctoken.tokenize(pytesseract.image_to_string(img, lang='eng').strip())  # tokenize

if __name__ == "__main__":
    valid_file_extentions = {"gif", "jpg", "jpeg", "jpeg-large", "png", "webp"}
    path = "/Users/connerward/Desktop"
    destination = "/Users/connerward/Documents/output"
    other_files_dest = "other-files/"

    # Flattens files from path, copies unique files (no duplicates) to destination.
    traverse(path=path, dest=destination, other=other_files_dest, valid_extensions=valid_file_extentions)


