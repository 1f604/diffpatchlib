# diffpatchlib
Python library for generating and applying diffs

Instructions for use:

* Put `diffpatchlib.py` in the same directory as your Python script.
* Look at the example usage in diffpatchlib.py

Run `test.py` to check that the library works. You will need to do so on a Linux machine where the `diff` utility is available. It will tell you whether Python's built-in difflib diff implementation is slower than the Linux command line `diff` utility.

Here is the output from running `test.py` on my Linux machine:

```
$ python test.py 
reading files into memory took: 0.03214383125305176 seconds
diff has 897 lines
generating diff took: 0.47491002082824707 seconds
writing diff to file took: 0.0002875328063964844 seconds
applying diff took: 0.0041806697845458984 seconds
In total it took: 0.5116124153137207 seconds
====== Now trying the Unix command line diff utility ======
reading files into memory took: 0.030364036560058594 seconds
running command: diff file0.txt file1.txt -u0 > unified_patch0
running Unix diff took: 0.02668166160583496 seconds
reading diff took: 0.0002357959747314453 seconds
applying diff took: 0.006578922271728516 seconds
In total it took: 0.0639808177947998 seconds
```
