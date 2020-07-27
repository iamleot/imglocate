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
import csv
import sys

import cv2


def draw_bounding_box(img, label: str,
                      x: int, y: int, width: int, height: int) -> None:
    """
    Draw a bounding box

    Given an opened image via cv2.imread(), draw a bounding box for the label
    `label' inside a rectangle with the coordinates (x, y) and area of (width,
    height).
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 255), (255, 255, 0)]
    color = colors[len(label) % len(colors)]
    cv2.rectangle(img, (x, y), (x + width, y + height), color, 2)
    ts = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
    cv2.rectangle(img, (x - 1, y - ts[0][1] - 6), (x + ts[0][0] + 6, y), color, cv2.FILLED)
    cv2.putText(img, label, (x + 2, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 2)


def read_annotations(filename: str) -> List[tuple]:
    """
    Read annotations from a file.

    Given annotations in `file' return a list of annotations in the form of a
    tuple with the following elements (in the corresponding order):

     - label
     - x
     - y
     - width
     - height
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
                    label, confidence, x, y, width, height = row
                    annotations.append((str(label), int(x), int(y),
                                        int(width), int(height)))
    except OSError as e:
        print('Could not open {filename}: {e}, ignoring'.format(
              filename=filename, e=e), file=sys.stderr)

    return annotations


if __name__ == '__main__':
    import argparse

    ap = argparse.ArgumentParser(
        prog='draw_bounding_boxes',
        description='Draw bounding boxes annotations in image'
    )

    ap.add_argument('-s', action='store_true',
                    help='show image')
    ap.add_argument('image', type=str, nargs='+',
                    help='image files')
    args = ap.parse_args()

    for image in args.image:
        annotations = '{image}.txt'.format(image=image)
        base, _, ext = image.rpartition('.')
        annotated_image = '{base}.annotated.{ext}'.format(base=base, ext=ext)

        img = cv2.imread(image)

        if img is None:
            print('Could not open {image}, ignoring'.format(image=image),
                  file=sys.stderr)
            continue

        labels = read_annotations(annotations)
        if not labels:
            # ignore image with no labels
            continue

        for label in labels:
            draw_bounding_box(img, *label)

        if args.s:
            cv2.imshow('draw_bounding_boxes', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            cv2.imwrite(annotated_image, img)
