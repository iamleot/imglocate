![Check and test imglocate](https://github.com/iamleot/imglocate/workflows/Check%20and%20test%20imglocate/badge.svg)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/iamleot/imglocate.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/iamleot/imglocate/alerts/)

# imglocate

imglocate is a Python 3 script that uses [OpenCV](https://opencv.org/)
to detect objects in images and write annotations in separate text
files as TSV (tab-separated values) containing: label (object
detected), confidence and bounding box (as an x, y, height, width
tuple).

Annotating an image is simple as `imglocate annotate`!:

```
% imglocate annotate office_at_night.jpg
% cat office_at_night.jpg.txt
person	0.84563	176	161	81	258
chair	0.70672	109	264	87	141
person	0.60168	363	276	46	70
diningtable	0.26269	251	327	269	184
```

...and, the corresponding image with bounded boxes drawn via
`draw_bounding_boxes.py` helper script:

![Office at Night, Edward Hopper (1940), oil-on-canvas annotated via imglocate (chair, person, diningtable, person)](/examples/office_at_night.annotated.jpg)


## Configuration

imglocate needs to be configured before it can be used.
A configuration file can be provided via the `-c` option.
By default the configuration file `~/.imglocaterc` is used.

The configuration field should have an `[imglocate]` section and should
contains all the following entries:

 - `weights`: path to the deep learning network weights
 - `config`: path to the deep learning network config
 - `labels`: path to the labels of the classes returned by the deep learning
   network. There should be one label per line.
 - `confidence_threshold`: confidence threshold
 - `nms_threshold`: NMS (Non-Maximum Suppression) threshold

For example, given `weights`, `config`, `labels` in a `~/.imglocate`
directory and using [YOLOv3-tiny](https://pjreddie.com/darknet/yolo/),
a confidence threshold of 0.2 (can be from 0 to 1) and an NMS
threshold of 0.3 (can be from 0 to 1):

```
[imglocate]
weights = ~/.imglocate/yolov3-tiny.weights
config = ~/.imglocate/yolov3-tiny.cfg
labels = ~/.imglocate/yolov3.labels
confidence_threshold = 0.2
nms_threshold = 0.3
```

The frameworks supported are the ones supported by
[`cv.dnn.readNet()`](https://docs.opencv.org/3.4/d6/d0f/group__dnn.html#ga3b34fe7a29494a6a4295c169a7d32422).


## Usage

imglocate supports two subcommands: `annotate` and `search`.
A short usage message of imglocate can be get via the `-h` option:

```
% imglocate -h
usage: imglocate [-h] [-c config_file] [-v] {annotate,search} ...

Locate objects in images

positional arguments:
  {annotate,search}  action
    annotate         annotate images
    search           search annotated images

optional arguments:
  -h, --help         show this help message and exit
  -c config_file     configuration file
  -v                 logging level
```

The following global options are supported:

 - `-h` prints a short usage message about `imglocate` or its subcommands
 - `-c` specify an alternative configuration file instead of using the
   default `~/.imglocaterc`
 - `-v` increase logging level, can be specified multiple times


### annotate

`annotate` subcommand annotate all images passed as arguments and
stores the annotations in a TSV (tab-separated values) text file in the
same path of each image appending to them the `.txt` suffix.

Every line in the annotations file correspond to a detected object.
The fields are, in order:

 - label (object detected)
 - confidence
 - x coordinate of the bounding box
 - y coordinate of the bounding box
 - height of the bounding box
 - width of the bounding box tuple

By default, if the annotations file for the image already exists and
its `mtime` is newer then the `mtime` of image no object detection is
performed.

```
% imglocate annotate -h
usage: imglocate annotate [-h] [-f] [-s] image [image ...]

positional arguments:
  image       image to annotate

optional arguments:
  -h, --help  show this help message and exit
  -f          force regen of already existent annotations
  -s          only print annotations (do not write them)
```

The following options are supported:

 - `-h` prints a short usage message
 - `-f` always do the object detection (also if there are annotations with
   an `mtime` newer than the image)
 - `-s` do not write any annotations file, print the annotations to the
   standard output


### search

`search` subcommand, given one or more `image` that were previously
annotated via `imglocate annotate`, search if label `label` print all
the resulting images containing the label to the standard output.

```
% imglocate search -h
usage: imglocate search [-h] label image [image ...]

positional arguments:
  label       force regen of already existent annotations
  image       image to search

optional arguments:
  -h, --help  show this help message and exit
```

The following options are supported:

 - `-h` prints a short usage message


## Examples

*TODO*: add some trivial and non trivial usage examples
