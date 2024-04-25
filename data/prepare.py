# xml parsing package
import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join

sets = ['train', 'test', 'val']
classes = ['missing_hole', 'mouse_bite', 'open_circuit', 'short', 'spur', 'spurious_copper']

# Normalization operation
def convert(size, box):  # size: (original width, original height), box: (xmin, xmax, ymin, ymax)
    dw = 1./size[0]     # 1/width
    dh = 1./size[1]     # 1/height
    x = (box[0] + box[1]) / 2.0   # x coordinate of the center point of the object in the image
    y = (box[2] + box[3]) / 2.0   # y coordinate of the center point of the object in the image
    w = box[1] - box[0]           # actual pixel width of the object
    h = box[3] - box[2]           # actual pixel height of the object
    x = x * dw    # x coordinate ratio of the object center point (equivalent to x/original width)
    w = w * dw    # width ratio of the object (equivalent to w/original width)
    y = y * dh    # y coordinate ratio of the object center point (equivalent to y/original height)
    h = h * dh    # height ratio of the object (equivalent to h/original height)
    return (x, y, w, h)    # return the x ratio, y ratio, width ratio, and height ratio of the object relative to the original image, range [0-1]

# year ='2012', corresponding image id (filename)
def convert_annotation(image_id):
    '''
    Convert the xml file corresponding to the filename into a label file. The xml file contains information such as the bounding box and the size of the image,
    which is parsed, normalized, and then saved to a label file.
    Each image file corresponds to one xml file. After parsing and normalization, the corresponding information is saved into a unique label file.
    The format in the label file is: class x y w h. Additionally, since an image can have multiple categories, it can have multiple bounding box information.
    '''
    # Open the corresponding xml file by the year and image_id for the bound file
    in_file = open('D:\\Dataset\\PCB_dataset\\data\\Annotations\\%s.xml' % (image_id), encoding='utf-8')
    # Prepare to write the corresponding label in the image_id, which includes
    # <object-class> <x> <y> <width> <height>
    out_file = open('D:\\Dataset\\PCB_dataset\\data\\labels\\%s.txt' % (image_id), 'w', encoding='utf-8')
    # Parse the xml file
    tree = ET.parse(in_file)
    # Get the key-value pair
    root = tree.getroot()
    # Get image dimensions
    size = root.find('size')
    # If there is no marking in the xml, add a condition check
    if size is not None:
        # Get width
        w = int(size.find('width').text)
        # Get height
        h = int(size.find('height').text)
        # Iterate through the objects
        for obj in root.iter('object'):
            # Get the difficulty
            difficult = obj.find('difficult').text
            # Get the category = string type
            cls = obj.find('name').text
            # If the category is not in our predefined classes or difficult==1, skip it
            if cls not in classes or int(difficult) == 1:
                continue
            # Find the id through the category name
            cls_id = classes.index(cls)
            # Find the bndbox object
            xmlbox = obj.find('bndbox')
            # Get the array of the bndbox = ['xmin','xmax','ymin','ymax']
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
                 float(xmlbox.find('ymax').text))
            print(image_id, cls, b)
            # Bring into normalization operation
            # w = width, h = height, b = bndbox array = ['xmin','xmax','ymin','ymax']
            bb = convert((w, h), b)
            # bb corresponds to the normalized (x,y,w,h)
            # Generate class x y w h in the label file
            out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

# Get the current working directory
wd = getcwd()
print(wd)

for image_set in sets:
    '''
    Iterate through all the data sets:
        1. Traverse all image files, write their full paths into the corresponding txt file for easy location.
        2. Parse and convert all image files, saving all bounding box and category information to label files.
           Then, by directly reading the file, you can find the corresponding label information.
    '''
    # If the labels directory does not exist, create it
    if not os.path.exists('D:\\Dataset\\PCB_dataset\\data\\labels\\'):
        os.makedirs('D:\\Dataset\\PCB_dataset\\data\\labels\\')
    # Read the contents of the train, test, etc., files in ImageSets/Main
    # Which contain corresponding filenames
    image_ids = open('D:\\Dataset\\PCB_dataset\\data\\ImageSets\\%s.txt' % (image_set)).read().strip().split()
    # Prepare to write to the corresponding year_train.txt file
    list_file = open('D:\\Dataset\\PCB_dataset\\data\\%s.txt' % (image_set), 'w')
    # Write the corresponding file_id and full path into it and move to the next line
    for image_id in image_ids:
        list_file.write('D:\\Dataset\\PCB_dataset\\data\\images\\%s.jpg\n' % (image_id))
        # Call with the year and image_id
        convert_annotation(image_id)
    # Close the file
    list_file.close()
