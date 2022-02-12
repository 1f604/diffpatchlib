# diffpatchlib
Python library for generating and applying diffs

Instructions for use:

* Put diffpatchlib.py in the same directory as your Python script.
* Follow the usage instructions in diffpatchlib.py

Run test.py to check that the library works. You will need to do so on a Linux machine where the `diff` utility is available. It will tell you whether Python's built-in difflib diff implementation is slower than the Linux command line `diff` utility.

Here are the results of running the test on my Linux machine:

```
reading files into memory took: 0.02922677993774414 seconds
diff has 897 lines
generating diff took: 0.4916975498199463 seconds
writing diff to file took: 0.000362396240234375 seconds
applying diff took: 0.004746198654174805 seconds
In total it took: 0.5261399745941162 seconds
====== Now trying the Unix command line diff ======
reading files into memory took: 0.03214669227600098 seconds
running command: diff file0.txt file1.txt -u0 > unified_patch0
running Unix diff took: 0.05245018005371094 seconds
reading diff took: 0.0002472400665283203 seconds
applying diff took: 0.007016181945800781 seconds
In total it took: 0.09199309349060059 seconds
```
