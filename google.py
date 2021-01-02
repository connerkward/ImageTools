import imagehash
from PIL import Image
import hashlib
import pytesseract
import cv2
import os
import ctoken
from google.cloud import vision
import io
# from imageai.Prediction.Custom import ModelTraining

# google api calls -------------------------------------
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gvision_credentials.json"
# client = vision.ImageAnnotatorClient()
# path = "f41020448.jpg"
# with io.open(path, 'rb') as image_file:
#     content = image_file.read()
# image = vision.Image(content=content)
#
# response = client.label_detection(image=image)
# labels = response.label_annotations
# print('Labels:')
#
# for label in labels:
#     print(label.description)
#
# if response.error.message:
#     raise Exception(
#         '{}\nFor more info on error messages, check: '
#         'https://cloud.google.com/apis/design/errors'.format(
#             response.error.message))

# main -------------------------------------
# # get grayscale image
# def get_grayscale(image):
#     return cv2.cvtColor(src=image, code=cv2.COLOR_BGR2GRAY)
#
# # thresholding
# def thresholding(image):
#     return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#
# # for dirpath, dirnames, filenames in os.walk(""):
# #       for filename in filenames:
# #         path = f"{dirpath}/{filename}"
#
# path = "asdf.png"
# cv2_img = cv2.imread(path)
# pil_img = Image.fromarray(cv2_img)
# thresh_invert = cv2.bitwise_not(thresholding(get_grayscale(cv2_img)))
# thresh = thresholding(get_grayscale(cv2_img))
# # cv2.namedWindow('image', cv2.WINDOW_NORMAL)
# # cv2.resizeWindow('image', 200, 200)
# # cv2.imshow('image', cv2_img)
# # cv2.waitKey(0)
# # cv2.imshow("image", thresh)
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()
# image_text = ctoken.tokenize(pytesseract.image_to_string(thresh, lang='eng'))
# image_text2 = ctoken.tokenize(pytesseract.image_to_string(pil_img, lang='eng'))
# image_text3 = ctoken.tokenize(pytesseract.image_to_string(thresh_invert, lang='eng'))
# image_whash = imagehash.whash(pil_img)
# md5_hash = hashlib.md5(cv2_img)
# print(image_text) # thresholded
# print(image_text3) # thresh invert
# print(image_whash)
# print(md5_hash.hexdigest())
# print("-----------------------")

 # google API features
 # IMAGE_PROPERTIES
 # LABEL_DETECTION

 # {"type": enum (Type), "maxResults": number, "model": string}
# client = vision.ImageAnnotatorClient()
# response = client.annotate_image({
#   'image': {'source': {'image_uri': 'gs://my-test-bucket/image.jpg'}},
#   'features': [{'type': vision.enums.Feature.Type.FACE_DETECTION}],
# })

# imageai ------------------------------------------------
# model_trainer = ModelTraining()
# model_trainer.setModelTypeAsResNet()
# model_trainer.setDataDirectory("pets")
# model_trainer.trainModel(num_objects=4, num_experiments=100, enhance_data=True, batch_size=32, show_network_summary=True)
