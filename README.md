[![Total alerts](https://img.shields.io/lgtm/alerts/g/iamleot/imglocate.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/iamleot/imglocate/alerts/)

# imglocate

imglocate is a Python 3 script that uses [OpenCV](https://opencv.org/)
to detect objects in images and write annotations in separate text
files as TSV (tab-separated values) containing: label, confidence and
bounding box (as an x, y, height, width tuple).

![Office at Night, Edward Hopper (1940), oil-on-canvas annotated via imglocate (chair, person, diningtable, person)](/examples/office_at_night.annotated.jpg)


## Configuration

imglocate needs to be configured before it can be used.
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

```
% imglocate -h
usage: imglocate [-h] {annotate,search} ...

Locate objects in images

positional arguments:
  {annotate,search}  action
    annotate         annotate images
    search           search annotated images

optional arguments:
  -h, --help         show this help message and exit
```
