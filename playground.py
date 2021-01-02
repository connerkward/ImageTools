from PIL.ExifTags import TAGS
from PIL import Image
import pathlib
import datetime
# path to the image or video
imagename = "image2.jpeg"

# read the image data using PIL
image = Image.open(imagename)
# extract EXIF data
exifdata = image.getexif()
valid_tagID = {306, 36867, 36868, 272, 271, 34853}
# cr date, cr date, cr date, camera model, camera make, gps data
selected_exif_data = dict()

# iterating over all EXIF data fields
for tag_id in exifdata:
    try:
        if tag_id in valid_tagID:
            # get the tag name, instead of tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            # decode bytes
            if isinstance(data, bytes):
                data = data.decode()
            # print(f"{tag_id}-{tag:25}: {data}")
            selected_exif_data[tag] = data
    except UnicodeDecodeError:
        pass

fname = pathlib.Path('image.jpg')
selected_exif_data["OSDateTime"] = datetime.datetime.fromtimestamp(fname.stat().st_ctime)
print(selected_exif_data)