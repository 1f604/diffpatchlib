from diffpatchlib import check_hash_matches, get_diff, get_unix_diff, apply_diff
import time

# Python's difflib is about 10x slower than Unix command line diff.
# To check, run this in your shell: time diff file0.txt file1.txt -u0
# The Unix diff ran in about 0.05s on my machine
# The Python difflib diff took about 0.45s to run by contrast
# After running this script, you can compare the diffs using this command:
# diff pydiff.txt unixdiff.txt

start1 = time.time()
for i in range(1):
    old_filename = "file" + str(i) + ".txt"
    new_filename = "file" + str(i+1) + ".txt"
    start = time.time()
    with open(old_filename) as f:
        a = f.readlines()
    with open(new_filename) as f:
        b = f.readlines()
    end = time.time()
    print("reading files into memory took:", end - start, "seconds")
    start = time.time()
    diff = get_diff(a,b, old_filename=old_filename, new_filename=new_filename)
    print("diff has", len(diff), "lines")
    end = time.time()
    print("generating diff took:", end - start, "seconds")

    start = time.time()
    with open("pydiff.txt", 'w') as f:
        f.writelines(diff)
    end = time.time()
    print("writing diff to file took:", end - start, "seconds")

    #print(diff)
    start = time.time()
    assert(apply_diff(a,diff) == b)
    end = time.time()
    print("applying diff took:", end - start, "seconds")

    check_hash_matches(a, "pydiff.txt")

end1 = time.time()
print("In total it took:", end1 - start1, "seconds")

diff = None
a = None
# now we try the Unix diff utility
print("====== Now trying the Unix command line diff utility ======")

start1 = time.time()
for i in range(1):
    old_filename = "file" + str(i) + ".txt"
    new_filename = "file" + str(i+1) + ".txt"
    start = time.time()
    with open(old_filename) as f:
        a = f.readlines()
    with open(new_filename) as f:
        b = f.readlines()
    end = time.time()
    print("reading files into memory took:", end - start, "seconds")

    start = time.time()
    diff = get_unix_diff(old_filename, new_filename)
    print("diff has", len(diff), "lines")
    end = time.time()
    print("running Unix diff took:", end - start, "seconds")

    start = time.time()
    with open("unixdiff.txt", 'w') as f:
        f.writelines(diff)
    end = time.time()
    print("writing diff to file took:", end - start, "seconds")

    #print(diff)
    start = time.time()
    new_a = apply_diff(a,diff) 
    assert(apply_diff(a,diff) == b)
    end = time.time()
    print("applying diff took:", end - start, "seconds")

    check_hash_matches(a, "unixdiff.txt")

end1 = time.time()
print("In total it took:", end1 - start1, "seconds")
