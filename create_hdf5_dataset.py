import h5py
import os
import numpy as np
from skimage.io import imread
from tqdm import tqdm
import sys


def collect_filenames(data_dir, filenames_array):
    walk = list(os.walk(data_dir))[0]
    subdirs = walk[1]
    filenames = walk[2]
    for filename in filenames:
        if filename.endswith('rgb.png'):
            filenames_array.append(os.path.join(data_dir, filename[:-7]))
    for subdir in subdirs:
        collect_filenames(os.path.join(data_dir, subdir), filenames_array)
        
        
def read_img_pairs(filenames):
    filenames.sort()
    image_pairs = []
    for filename in tqdm(filenames):
        rgb_filename = filename + 'rgb.png'
        depth_filename = filename + 'depth.png'
        try:
            rgb_img = imread(rgb_filename)
            depth_img = imread(depth_filename)
        except:
            continue
        image_pairs.append((rgb_img, depth_img))
    return image_pairs


def random_crop(image_pair, h=224, w=224, n_crops=1):
    rgb_image, depth_image = image_pair
    H, W, _ = rgb_image.shape
    result = []
    for k in range(n_crops):
        i = np.random.randint(0, H - h)
        j = np.random.randint(0, W - w)
        rgb_crop = rgb_image[i:i+h, j:j+w, :]
        depth_crop = depth_image[i:i+h, j:j+w]
        result.append([rgb_crop, depth_crop])
    return result


def id_function(x):
    return x


def create_hdf5_dataset(data_dir, 
                        destination, 
                        percent=100.,
                        crops_per_image=1,
                        h=224,
                        w=224,
                        processing_function=None,
                        chunk_size=1024,
                        channels_first=True,
                        rgb_postprocessing=id_function,
                        depth_postprocessing=id_function):
    filenames = []
    print("Collecting image names...")
    collect_filenames(data_dir, filenames)
    print("Done")
    
    n_imgs = int(len(filenames) * percent / 100.)
    filenames = np.random.choice(filenames, size=n_imgs, replace=False)
    n_chunks = int(np.ceil(len(filenames) / chunk_size))
    for chunk_id in range(n_chunks):
        print("Processing chunk {} of {}".format(chunk_id + 1, n_chunks))
        print("Reading images...")
        image_pairs = read_img_pairs(filenames[chunk_id * chunk_size:(chunk_id + 1) * chunk_size])
        print("Done")
        print("Processing images...")
        cropped_image_pairs = []
        for image_pair in tqdm(image_pairs):
            if processing_function is None:
                cropped_image_pairs += random_crop(image_pair, h=h, w=w, n_crops=crops_per_image)
            else:
                cropped_image_pairs += processing_function(image_pair, crops_per_image)
        rgbs = np.array([resize(x[0], (h, w, 3)) for x in cropped_image_pairs if x[0].shape != (h, w, 3)])
        depths = np.array([resize(x[1], (h, w)) for x in cropped_image_pairs if x[1].shape != (h, w)])
        print("Done")
        print("Writing to dataset...")
        if channels_first:
            rgbs = np.transpose(rgbs, [0, 3, 1, 2])
        if chunk_id == 0:
            with h5py.File(destination, 'w') as f:
                f.create_dataset("data", data=rgbs, maxshape=[None] + list(rgbs.shape[1:]))
                f.create_dataset("label", data=depths, maxshape=[None] + list(depths.shape[1:]))
        else:
            with h5py.File(destination, 'a') as f:
                data = f["data"]
                label = f["label"]
                data.resize(data.shape[0] + rgbs.shape[0], axis=0)
                label.resize(label.shape[0] + depths.shape[0], axis=0)
                data[data.shape[0]:data.shape[0] + rgbs.shape[0]] = rgbs
                label[label.shape[0]:label.shape[0] + depths.shape[0]] = depths
        print("Done")
    
    
argv = sys.argv
usage_message = """
Usage

python create_hdf5_dataset.py \[params\] data_dir destination

data_dir is a path to directory contains preprocessed RGB and depth images.
Names of paired RGB and depth images must have the same prefix and must end with "rgb.png" and "depth.png" respectfully. For example, "image0001_rgb.png" and "image0001_depth.png".
destination is a desired path to HDF5 dataset.

Params

-h, --height: height of the cropped image. Default is 224
-w, --width: width of the cropped image. Default is 224
-n, --n_crops: number of crops taken from each image. Default is 1
-p, --percent: percentage (0 to 100) of data included in hdf5 dataset. Default is 100
-c, --chunksize: number of images read and processed in one chunk (to deal with large datasets that don't fit into RAM). Default is 1024
--channels_first: True or False: are channels the first dimension of image, or the last dimension. Default is True

Result

The result is HDF5 database with two datasets: "data" (RGB images) and "label" (depth images). RGB images have shape (3, h, w) if channels_first parameter is set to True, and (h, w, 3) otherwise. Depth images have shape (h, w).

Example

python create_hdf5_dataset.py -h 224 -w 224 -n 1 -p 100 --channels-first True ./Data ./data.hdf5
"""

if __name__ == '__main__':
    # Show usage message
    if len(argv) < 3:
        print(usage_message)
        exit(0)

    # Initialize params
    h = 224
    w = 224
    n_crops = 1
    channels_first = True
    percent =  100
    cnunksize = 1024

    # Specify params from argv
    for i in range(1, len(argv)):
        if argv[i] in ['-h', '--height']:
            try:
                h = int(argv[i + 1])
                assert(h > 0 and h <= 400)
            except:
                print(usage_message)
                print("Specify image height as positive integer number no more than 400")
                exit(0)
        if argv[i] in ['-w', '--width']:
            try:
                w = int(argv[i + 1])
                assert(w > 0 and w <= 550)
            except:
                print(usage_message)
                print("Specify image width as positive integer number no more than 550")
                exit(0)
        if argv[i] in ['-p', '--percent']:
            try:
                percent = float(argv[i + 1])
                assert(percent > 0 and percent <= 100)
            except:
                print(usage_message)
                print("Specify percent of source dataset as float number from 0 to 100")
                exit(0)
        if argv[i] in ['-n', '--n_crops']:
            try:
                n_crops = int(argv[i + 1])
                assert(n_crops > 0)
            except:
                print(usage_message)
                print("Specify number of crops per image as positive integer number")
        if argv[i] == '--channels_first':
            try:
                channels_first = (argv[i + 1] == "True")
            except:
                print(usage_message)
                print("Specify channels_first parameter as True or False")
                exit(0)
        if argv[i] in ['-c', '--chunksize']:
            try:
                cnunksize = int(argv[i + 1])
            except:
                print(usage_message)
                print("Specify size of image batch as positive integer number")
    data_dir = argv[-2]
    destination = argv[-1]

    # Create HDF5 dataset
    create_hdf5_dataset(data_dir,
                        destination,
                        h=h,
                        w=w,
                        percent=percent,
                        crops_per_image=n_crops,
                        channels_first=channels_first,
                        cnunk_size=cnunksize
                       )
