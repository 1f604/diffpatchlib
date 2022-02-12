# diffpatchlib
Python library for generating and applying diffs

## Instructions for use:

* Put `diffpatchlib.py` in the same directory as your Python script.
* Look at the example usage in diffpatchlib.py

## Benchmarking

Run `test.py` to check that the library works. You will need to do so on a Linux machine where the `diff` utility is available. It will tell you whether Python's built-in difflib diff implementation is slower than the Linux command line `diff` utility.

Here is the output from running `test.py` on my Linux machine:

```
$ python test.py 
reading files into memory took: 0.0336148738861084 seconds
diff has 897 lines
generating diff took: 0.4804341793060303 seconds
writing diff to file took: 0.00028586387634277344 seconds
applying diff took: 0.004276752471923828 seconds
In total it took: 0.5187017917633057 seconds
====== Now trying the Unix command line diff utility ======
reading files into memory took: 0.030704975128173828 seconds
diff has 897 lines
running Unix diff took: 0.052553415298461914 seconds
writing diff to file took: 0.0003330707550048828 seconds
applying diff took: 0.01743173599243164 seconds
In total it took: 0.10115647315979004 seconds
```
