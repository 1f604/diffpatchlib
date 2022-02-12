#!/usr/bin/env python
# coding=utf-8
# License: Public domain (CC0)
# Isaac Turner 2016/12/05
# 1f604 2022/02/11

""" Example usage:

from diffpatchlib import get_diff, apply_diff

a = ["aa", "bb", "cc\n"]
b = ["aa", "dd", "cc\n"]

diff = get_diff(a, b)
print(diff)
print(apply_diff(a, diff))

with open("file1.txt") as f:
    a = f.readlines()
with open("file2.txt") as f:
    b = f.readlines()

diff = get_diff(a, b, old_filename = "file1", new_filename = "file2")
print(diff)
print(apply_diff(a,diff) == b)
"""

from __future__ import print_function

import difflib
import re
import traceback
import sys
import subprocess

_hdr_pat = re.compile("^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$")

def __check_newline_terminated(files):
    for filename, lines in files:
        if lines[-1][-1] != '\n':
            print("ERROR: Missing newline at end of file {} ending in: ".format(filename))
            print(lines[-1])
            exit(1)

def __make_patch(oldlines, newlines, filename1, filename2):
    """
    Get unified string diff between two strings.
    Returns empty string if strings are identical.
    """
    # ensure strings are newline terminated
    __check_newline_terminated(((filename1, oldlines), (filename2, newlines)))
    # get the unified diff
    diffs = difflib.unified_diff(oldlines, newlines, fromfile=filename1, tofile=filename2, n=0)
    # diffs = list(diffs); print(diffs)
    return list(diffs)

def __apply_patch(oldlines, patchlines):
    """
    Apply unified diff patch to string old to recover newer string.
    """
    if not patchlines:
        return oldlines
    result = []
    patch_pointer = 0
    old_current_pointer = 0
    allowed_line_starts = "@+-"
    #for char in allowed_line_starts:
    #    print("allowed:", char, ord(char))
    while patch_pointer < len(patchlines) and patchlines[patch_pointer].startswith(("---","+++")): 
        patch_pointer += 1 # skip header lines
    while patch_pointer < len(patchlines):
        # get starting line number from hunk header
        m = _hdr_pat.match(patchlines[patch_pointer])
        if not m: 
            print(patchlines)
            raise Exception("Cannot process diff")
        patch_pointer += 1
        old_start_pointer = int(m.group(1))-1 + (m.group(2) == '0')
        result.extend(oldlines[old_current_pointer:old_start_pointer])
        old_current_pointer = old_start_pointer
        # go through hunk
        while patch_pointer < len(patchlines) and patchlines[patch_pointer][0] != '@':
            if patch_pointer + 1 < len(patchlines) and patchlines[patch_pointer+1][0] not in allowed_line_starts:
                print("ERROR: line does not begin with expected symbol:", ord(patchlines[patch_pointer+1][0]), patchlines[patch_pointer+1])
                exit(1)
            line = patchlines[patch_pointer]
            patch_pointer += 1
            assert(len(line) > 0)
            assert(line[0] in allowed_line_starts)
            if line[0] == '+': 
                result.append(line[1:])
            else:
                old_current_pointer += 1
    result.extend(oldlines[old_current_pointer:])
    return result

def __test_patch(a, b, patch):
  try:
    assert __apply_patch(a, patch) == b
  except Exception as e:
    print("=== a ===")
    print([a])
    print("=== b ===")
    print([b])
    print("=== patch ===")
    print([patch])
    print("=== a with patch applied ===")
    print(__apply_patch(a, patch))
    traceback.print_exc()
    sys.exit(-1)

def __get_tested_patch(oldlines, newlines, filename1, filename2):
    """
        This is the function you want to call 99% of the time.
    """
    # first generate the patch
    patch = __make_patch(oldlines, newlines, filename1, filename2)
    # now test it
    __test_patch(oldlines, newlines, patch)
    # now return it
    return patch
        
def get_diff(old_lines, new_lines, *, old_filename = "old_file", new_filename = "new_file"):
    """
    Parameters
    ----------
    old_lines : [string]
    new_lines : [string]
    old_filename : string
    new_filename : string

    Returns
    -------
    patch_lines : [string]
    """
#    with open(filename1) as f:
#        old_lines = f.readlines()
#    with open(filename2) as f:
#        new_lines = f.readlines()
    return __get_tested_patch(old_lines, new_lines, old_filename, new_filename)

def get_unix_diff(old_filename, new_filename):
    """
    Parameters
    ----------
    old_filename : string
    new_filename : string

    Returns
    -------
    patch_lines : [string]
    """
    try:
        subprocess.check_output(['diff', old_filename, new_filename, '-u0'])
        return []
    except subprocess.CalledProcessError as e:
        if e.returncode != 0 and e.returncode != 1:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return str(e.output, 'utf-8').splitlines(True)

def apply_diff(old_lines, patch_lines):
    """
    Parameters
    ----------
    old_lines : [string]
    patch_lines : [string]

    Returns
    -------
    new_lines : [string]
    """
    return __apply_patch(old_lines, patch_lines)

if __name__ == '__main__': 
    print("This library provides 3 useful functions:")
    print("1. get_diff(old, new, old_filename, new_filename)")
    print("2. get_unix_diff(old_filename, new_filename)")
    print("3. apply_diff(old, patch)")
