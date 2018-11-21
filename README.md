# HDF5 creator for NYU depth dataset

This utility is to create HDF5 database of NYU depth dataset. Images of the dataset are cropped randomly into particular size.

## Requiremetns

Required Python libraries: h5py, scikit-image, tqdm.
This code is tested with Python 3.6, but it probably works with Python 2.
    
## Use in command line

python create_hdf5_dataset.py \[params\] data_dir destination

`data_dir` is a path to directory contains preprocessed RGB and depth images.
Names of paired RGB and depth images must have the same prefix and must end with "rgb.png" and "depth.png" respectfully. For example, "image0001_rgb.png" and "image0001_depth.png".

`destination` is a desired path to HDF5 dataset.

### Params

`-h, --height`: height of the cropped image. Default is 224

`-w, --width`: width of the cropped image. Default is 224

`-n, --n_crops`: number of crops taken from each image. Default is 1

`-p, --percent`: percentage (0 to 100) of data included in hdf5 dataset. Default is 100

`--channels_first`: True or False: are channels the first dimension of image, or the last dimension. Default is True

### Result

The result is HDF5 database with two datasets: "data" (RGB images) and "label" (depth images). RGB images have shape (3, h, w) if `channels_first` parameter is set to True, and (h, w, 3) otherwise. Depth images have shape (h, w).

### Example

`python create_hdf5_dataset.py -h 224 -w 224 -n 1 -p 100 --channels-first True ./Data ./data.hdf5`

## Use as Python module

```
from create_hdf5_dataset import create_hdf5_dataset
create_hdf5_dataset(data_dir, destination, h=224, w=224, n_crops=1, percent=100, channels_first=True)
```
