imglocate should be considered mostly feature complete.
There are several known (and probably unknown) bugs:


## TODO/Known bugs

 - More gracefully handle possible exceptions/errors
 - Add a `setup.py`
 - GitHub actions seems non-completely reproducible. Sometimes the
   `Check and test imglocate' fails due different confidence values, e.g.
   (<https://github.com/iamleot/imglocate/runs/902549902>)

```
--- examples/office_at_night.jpg.txt	2020-07-23 12:18:55.690638388 +0000
+++ /dev/fd/63	2020-07-23 12:19:07.258682391 +0000
@@ -1,4 +1,4 @@
 person	0.8456319570541382	176	161	81	258
-chair	0.7067238688468933	109	264	87	141
-person	0.6016818881034851	363	276	46	70
-diningtable	0.26269155740737915	251	327	269	184
+chair	0.7067239880561829	109	264	87	141
+person	0.6016820073127747	363	276	46	70
+diningtable	0.26269131898880005	251	327	269	184
##[error]Process completed with exit code 1.
```

   It should be investigated if there are possible subtle platform
   differences (but that will be probably not be easy).
