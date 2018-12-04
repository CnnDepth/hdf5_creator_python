# HDF5 creator for NYU depth dataset

This utility is to create HDF5 database of NYU depth dataset. Images of the dataset are cropped randomly into particular size.

## Requiremetns

See required Python libraries in file `requirements.txt`. This code was tested with Python 3.6.
    
## Usage in command line

`python create_hdf5_dataset.py [params] data_dir destination`

`data_dir` is a path to directory contains preprocessed RGB and depth images.
Names of paired RGB and depth images must have the same prefix and must end with "rgb.png" and "depth.png" respectfully. For example, "image0001_rgb.png" and "image0001_depth.png".

`destination` is a desired path to HDF5 dataset.

### Example

`python create_hdf5_dataset.py -h 224 -w 224 -n 1 -p 100 -j 160 --channels-first True --chunksize 1024 ./Data ./data.hdf5`

### Parameters

* `-h, --height`: height of the cropped image. Default is 224
* `-w, --width`: width of the cropped image. Default is 224
* `-n, --n_crops`: number of crops taken from each image. Default is 1
* `-p, --percent`: percentage (0 to 100) of data included in hdf5 dataset. Default is 100
* `-c, --chunksize`: number of images in one chunk. Default is 1024
* `-j, --jobs`: number of jobs for parallel processing. Default is 1
* `--channels_first`: True or False: are channels the first dimension of image, or the last dimension. Default is True

### Result

The result is HDF5 database with two datasets: "data" (RGB images) and "label" (depth images). RGB images have shape (3, h, w) if `channels_first` parameter is set to True, and (h, w, 3) otherwise. Depth images have shape (h, w).

## Usage as Python module

This utility is also available for usage as Python module. Module should be called as shown below:

### Example

```python
from create_hdf5_dataset import create_hdf5_dataset
create_hdf5_dataset(data_dir,
                    destination,
                    h=224,
                    w=224,
                    processing_function=None,
                    crops_per_image=1,
                    percent=100,
                    channels_first=True,
                    chunk_size=1024,
                    n_jobs=1
                    )
```

### Parameters

* **`h:`** desired height of image, integer number

* **`w:`** desired width of image, integer number

* **`processing_function:`** function that processes images.

This function takes a tuple of arguments: ((RGB_image, depth_image), h, w, n_crops).
It must return a list of processed (RGB, depth) pairs with size of number of crops. Input RGB image shape is (h, w, 3). 

Input depth image shape is (h, w). RGB images have pixel values from 0 to 255, depth images have pixel vaues from 0 to 65535.
Output RGB image must have shape (h, w, 3), output depth image must have shape (h, w).

Example of `processing_function`:
```python
def processing_function(args):
    image_pair, h, w, n_crops = args
    rgb_image, depth_image = image_pair
    result = []
    for i in range(n_crops):
        result.append((rgb_image[:h, :w, :], depth_image[:h, :w]))
    return result
```

* **`crops_per_image:`** number of crops taken from each source image, integer number

* **`percent:`** the percent of data of source collection that will be included into the dataset. Float number from 0 to 100

* **`channels_first:`** is dimension of channels the first dimension or not. Boolean value. If True, shape of processed image will be (3, h, w). If False, the shape will be (h, w, 3)

* **`chunk_size:`** number of images in one chunk (dataset processing is chunk-wise to deal with large datasets). Integer number

### Result

The result is HDF5 database with two datasets: "data" (RGB images) and "label" (depth images). RGB images have shape (3, h, w) if `channels_first` parameter is set to True, and (h, w, 3) otherwise. Depth images have shape (h, w).