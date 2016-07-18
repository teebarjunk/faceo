# Faceo 0.1

Extract face from photos and reorient them based on an input face.

I can't afford an artist atm, so I wrote this to create quick temporary texture for characters in a game. Simply give it a face texture to go off of, it will use opencv and dlib to find the points, then it will go through a folder of images, extracting faces and orienting them for you. This could be modified 

## Overview
Given a template face texture like:
![results](current_merged.isomap.png)
and a folder of faces, you'll get a folder of faces aligned to the template.
Which could be optionally merged with faceMerge.py:
![results](results.png)

These are some in Unity examples of how the results could be used.
(None of this was touched up, and they are all sharing the same face model, but it gives a rough idea.)
![results](results2.png)

But the scripts could be used however you want:
![results](results3.png)

## Requirements
```
pip3 install numpy
pip3 install opencv
pip3 install dlib
```
and if you want to use the image enhance feature in faceMerge.py
```
pip3 install wand
```

## Future plans (Will probably never be implemented.)
* GUI + Precompiled .exe
* Get face pose/rotation, then only grab triangles from side of face closest to camera. (For better quality.)