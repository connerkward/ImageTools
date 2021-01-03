
import colorgram
import PIL


img = PIL.Image.open("image3.jpg")
# img.show()
if img.size[0] > 1200:
    x = int((img.size[0]/10))
    y = int((img.size[1]/10))
else:
    x = img.size[0]
    y = img.size[1]
img_r = img.resize((x, y), resample=PIL.Image.BILINEAR)

colors = colorgram.extract(img_r, 8)
print(colors)
# colorsr = colorgram.extract(img_r, 8)
# for color in colors:
#     print(color.rgb)
#     print(color.proportion)
#     img = PIL.Image.new('RGB', (60, 30), color=color.rgb)
#     img.show()
#
# for color in colorsr:
#     print(color.rgb)
#     print(color.proportion)
#     img = PIL.Image.new('RGB', (60, 30), color=color.rgb)
#     img.show()