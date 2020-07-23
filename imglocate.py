#!/usr/bin/env python3

#
# Copyright (c) 2020 Leonardo Taccari
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#


from typing import List
import collections
import configparser
import csv
import logging
import os
import sys

import cv2
import numpy as np


DetectedObject = collections.namedtuple('DetectedObject', [
    'label',
    'confidence',
    'x',
    'y',
    'width',
    'height',
])
DetectedObject.__doc__ += 'Detected object'
DetectedObject.label.__doc__ = 'label'
DetectedObject.confidence.__doc__ = 'confidence'
DetectedObject.x.__doc__ = 'x coordinates of the bounding box'
DetectedObject.y.__doc__ = 'y coordinates of the bounding box'
DetectedObject.width.__doc__ = 'width of the bounding box'
DetectedObject.height.__doc__ = 'height of the bounding box'


def read_annotations(filename: str) -> List[tuple]:
    """
    Read annotations from a file.

    Given annotations in `file' return a list of annotations in the form of a
    tuple with the following elements (in the corresponding order):

     - label
     - x
     - y
     - height
     - width
    """
    annotations = []

    try:
        with open(filename, mode='r') as f:
            annotations_reader = csv.reader(f,
                                            delimiter='\t',
                                            doublequote=False,
                                            quoting=csv.QUOTE_NONE)
            for row in annotations_reader:
                if len(row) == 6:
                    label, confidence, x, y, height, width = row
                    annotations.append((str(label), int(x), int(y),
                                        int(height), int(width)))
    except OSError as e:
        logging.warning('Could not open %s: %s, ignoring', filename, e)

    return annotations


def read_config(config_file: str = '~/.imglocaterc') -> dict:
    """
    Read configuration file config_file.

    Read the configuration file config_file, if not specified `~/.imglocaterc',
    via `configparser'.
    The configuration file should have a `[imglocate]' main section and the
    following entries:

     - weights: path to the deep learning network weights
     - config: path to the deep learning network config
     - labels: path to the labels of the classes returned by the deep learning
               network. There should be one label per line.
     - confidence_threshold: confidence threshold
     - nms_threshold: NMS (Non-Maximum Suppression) threshold

    If the file is not present or a configuration entry is missing the program
    exit with a 1 exit status.

    Returns the parsed configuration as `dict'.
    """
    cp = configparser.ConfigParser()
    cp.read(os.path.expanduser(config_file))

    config = {
        'weights': cp.get('imglocate', 'weights', fallback=None),
        'config': cp.get('imglocate', 'config', fallback=None),
        'labels': cp.get('imglocate', 'labels', fallback=None),
        'confidence_threshold': cp.get('imglocate', 'confidence_threshold', fallback=None),
        'nms_threshold': cp.get('imglocate', 'nms_threshold', fallback=None),
    }

    for k in ('weights', 'config', 'labels'):
        if config[k]:
            config[k] = os.path.expanduser(config[k])

    for k in ('confidence_threshold', 'nms_threshold'):
        if config[k]:
            config[k] = float(config[k])

    for k in config:
        if not config[k]:
            logging.error('Missing configuration option %s', k)

    if any(not config[k] for k in config):
        logging.critical('Configuration file not properly populated')
        sys.exit(1)

    return config


def boxes(detected_objects: List[DetectedObject]) -> List[List]:
    """
    Given a list of DetectedObject return bounding boxes as a list of list.

    boxes() takes a list of DetectedObject `detected_objects' and return
    bounding boxes as a list of list.  Each element of the returned list (single
    bounding box) has the following element:

     - x
     - y
     - width
     - height
    """
    return [[o.x, o.y, o.width, o.height] for o in detected_objects]


def confidences(detected_objects: List[DetectedObject]) -> List[float]:
    """
    Given a list of DetectedObject return confidences as a list.

    confidences() takes a list of DetectedObject `detected_objects' and return
    the list of confidences.
    """
    return [o.confidence for o in detected_objects]


def object_detection(image: str, weights: str,
                     config: str, labels: str,
                     confidence_threshold: float = 0.5,
                     nms_threshold: float = 0.4,
                     scale: float = 0.00392) -> List[DetectedObject]:
    """
    Perform object detection given an image.

    object_detection() takes a path of an `image', `weights' and `config' of the
    deep learning network (passed to `cv2.dnn.readNet()'), a path to text file
    `labels' containing corresponding labels one per line and optional
    `confidence_threshold' and `nms_threshold'.

    It return a list of DetectedObject found (or an empty list when no object
    could be found).
    """
    class_labels = ()
    detected_objects = []

    with open(labels, mode='r') as f:
        class_labels = tuple(line.strip() for line in f.readlines())

    # read deep learning network
    logging.debug('Loading deep learning network with weight/config %s/%s', weights, config)
    net = cv2.dnn.readNet(weights, config)

    # read the image
    logging.debugging('Loading image %s', image)
    img = cv2.imread(image)

    # create 4d blob from image resizing it to 416x416
    logging.debugging('Creating 4D blob')
    blob = cv2.dnn.blobFromImage(img, scale, (416, 416), (0, 0, 0), True, crop=False)

    # set the input
    net.setInput(blob)

    # run inference through the network
    logging.debugging('Running inference through the network')
    outs = net.forward(net.getUnconnectedOutLayersNames())

    last_layer = net.getLayer(net.getLayerNames()[-1])

    if last_layer.type == 'Region':
        # Network produces output blob with a shape NxC where N is a number of
        # detected objects and C is a number of classes + 4 where the first 4
        # numbers are [center_x, center_y, width, height]
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = float(scores[class_id])
                if confidence > confidence_threshold:
                    width = int(detection[2] * img.shape[1])
                    height = int(detection[3] * img.shape[0])
                    x = int(int(detection[0] * img.shape[1]) - width / 2)
                    y = int(int(detection[1] * img.shape[0]) - height / 2)
                    detected_objects.append(DetectedObject(
                        label=class_labels[class_id],
                        confidence=confidence,
                        x=x,
                        y=y,
                        width=width,
                        height=height))

    logging.debugging('Running Non-Maximum Suppression')
    indices = cv2.dnn.NMSBoxes(boxes(detected_objects), confidences(detected_objects), confidence_threshold, nms_threshold)

    return [detected_objects[i[0]] for i in indices]


def annotations(detected_objects: List[DetectedObject]):
    """
    Print all detected objects as TSV
    """
    s = ''
    for o in detected_objects:
        s += '{label}\t{confidence:.5f}\t{x}\t{y}\t{width}\t{height}\n'.format(
            label=o.label,
            confidence=o.confidence,
            x=o.x,
            y=o.y,
            width=o.width,
            height=o.height)

    return s


def annotate(images: List[str], config: dict, simulate: bool = False,
             force: bool = False):
    """
    Given a list of `images' annotate them.

    Given a list of `images', for each of them detect objects and write
    annotations containing classes found with a `.txt' suffix appended to the
    image path.

    If the annotation file already exists and its mtime is newer than the mtime
    of the corresponding image file and `force' is False no object detection is
    done.

    If `simulate' is True annotations are printed to the stdout.
    """
    for i, image in enumerate(images):
        image = os.path.expanduser(image)
        annotations_file = '{image}.txt'.format(image=image)
        annotations_text = ''

        # Read possible already existent annotation if the regen is not forced
        # and the mtime of the annotations file is newer than the mtime of the
        # image.
        if not force and \
           os.path.exists(annotations_file) and \
           os.path.getmtime(annotations_file) > os.path.getmtime(image):
            logging.info('Reusing already existent annotations %s',
                         annotations_file)
            with open(annotations_file, mode='r') as f:
                annotations_text = f.read()

        if not annotations_text:
            logging.info('Detecting objects in %s', image)
            detected_objects = object_detection(image,
                                                config['weights'],
                                                config['config'],
                                                config['labels'],
                                                config['confidence_threshold'],
                                                config['nms_threshold'])
            logging.info('Preparing annotations in %s', image)
            annotations_text = annotations(detected_objects)

        if simulate:
            if i > 0:
                print()
            print('{image}:'.format(image=image))
            print(annotations_text, end='')
        else:
            logging.info('Writing annotations in %s', annotations_file)
            with open(annotations_file, mode='w') as f:
                f.write(annotations_text)


def search(images: List[str], label: str) -> List[str]:
    """
    Given a list of `images' search the ones with the label `label'.

    Search for `label' label in annotations file of each corresponding image in
    `images' and return a list of all matching images.
    """
    matching_images = []
    for image in images:
        image = os.path.expanduser(image)
        annotations_file = '{image}.txt'.format(image=image)
        if os.path.isfile(annotations_file) and \
           os.path.isfile(image):
            annotations = read_annotations(annotations_file)
            if label in [a[0] for a in annotations]:
                matching_images.append(image)

    return matching_images


if __name__ == '__main__':
    import argparse

    logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s')

    ap = argparse.ArgumentParser(
        prog='imglocate',
        description='Locate objects in images'
    )
    sp = ap.add_subparsers(dest='action', help='action')
    ap.add_argument('-c', type=str, default='~/.imglocaterc',
                   metavar='config_file', help='configuration file')

    # annotate subcommand
    asp = sp.add_parser('annotate', help='annotate images')
    asp.add_argument('-f', action='store_true',
                    help='force regen of already existent annotations')
    asp.add_argument('-s', action='store_true',
                    help='only print annotations (do not write them)')
    asp.add_argument('images', nargs='+', type=str, metavar='image',
                    help='image to annotate')

    # search subcommand
    ssp = sp.add_parser('search', help='search annotated images')
    ssp.add_argument('label', type=str,
                    help='force regen of already existent annotations')
    ssp.add_argument('images', nargs='+', type=str, metavar='image',
                    help='image to search')

    args = ap.parse_args()

    if args.action == 'annotate':
        config = read_config(args.c)
        annotate(args.images, config, simulate=args.s, force=args.f)
        sys.exit(0)

    if args.action == 'search':
        for image in search(args.images, args.label):
            print(image)
        sys.exit(0)

    # No action selected, print help message
    ap.print_help()
    sys.exit(1)
