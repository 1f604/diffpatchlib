#!/usr/bin/env python
# coding=utf-8
# License: Public domain (CC0)
# Isaac Turner 2016/12/05
# 1f604 2022/02/11

""" Example usage:

from diffpatchlib import get_verified_unix_diff, apply_diff_unchecked

with open("file0.txt") as f:
    a = f.readlines()
with open("file1.txt") as f:
    b = f.readlines()

diff = get_verified_unix_diff("file0.txt", "file1.txt")
print(diff)
print(apply_diff_unchecked(a,diff) == b)
"""

from __future__ import print_function

import difflib
import hashlib
import re
import traceback
import sys
import subprocess

_diff_header_pat = re.compile("^sha256s: ([0-9a-f]+) ([0-9a-f]+)$")
_hdr_pat = re.compile("^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$")

# https://stackoverflow.com/a/44873382
def sha256sum(filename):
    """
    Parameters
    ----------
    filename : string

    Returns
    -------
    hex_digest : string
    """
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

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
    old_hash = sha256sum(old_filename)
    new_hash = sha256sum(new_filename)
    result = ["sha256s: " + old_hash + " " + new_hash + '\n']
    return result + __get_tested_patch(old_lines, new_lines, old_filename, new_filename)

def get_verified_unix_diff(old_filename, new_filename):
    """
    Parameters
    ----------
    old_filename : string
    new_filename : string

    Returns
    -------
    patch_lines : [string]
    """
    old_hash = sha256sum(old_filename)
    new_hash = sha256sum(new_filename)
    result = ["sha256s: " + old_hash + " " + new_hash + '\n']
    try:
        subprocess.check_output(['diff', old_filename, new_filename, '-u0'])
        result = []
    except subprocess.CalledProcessError as e:
        if e.returncode != 0 and e.returncode != 1:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        result += str(e.output, 'utf-8').splitlines(True)
    # verify the patch
    with open(old_filename) as f:
        old_lines = f.readlines()
    applied_lines = apply_diff_unchecked(old_lines, result)
    check_hash_matches(applied_lines, new_hash)
    return result

def get_hashes(patch_filename):
    with open(patch_filename) as f:
        patch_line = f.readline()
        return __get_hashes(patch_line)

def __get_hashes(first_line_of_patch):
    m = _diff_header_pat.match(first_line_of_patch)
    if not m:
        print(first_line_of_patch)
        raise Exception("Expected hashes at first line of patch")
    return m.group(1), m.group(2)

def apply_diff_unchecked(old_lines, patch_lines):
    """
    VERY IMPORTANT: You must manually verify that the results are correct.

    This is because the verification functions are slow.

    Parameters
    ----------
    old_lines : [string]
    patch_lines : [string]

    Returns
    -------
    new_lines : [string]
    """
    return __apply_patch(old_lines, patch_lines[1:])

def __apply_diff_verified(old_lines, patch_lines):
    """
    Parameters
    ----------
    old_lines : [string]
    patch_lines : [string]

    Returns
    -------
    new_lines : [string]
    """
    old_hash, new_hash = __get_hashes(patch_lines[0])
    check_hash_matches(old_lines, old_hash)
    new_lines = __apply_patch(old_lines, patch_lines[1:])
    check_hash_matches(new_lines, new_hash)
    return new_lines

def check_hash_matches(lines, hash):
    contents = ''.join(lines).encode('utf-8')
    hash_of_lines = hashlib.sha256(contents).hexdigest()
    if hash != hash_of_lines:
        raise Exception("Hash of lines does not match the hash supplied")

def __apply_diff_verified(old_lines, patch_lines):
    """
    Parameters
    ----------
    old_lines : [string]
    patch_lines : [string]

    Returns
    -------
    new_lines : [string]
    """
    contents = ''.join(old_lines).encode('utf-8')
    hash = hashlib.sha256(contents).hexdigest()
    m = _diff_header_pat.match(patch_lines[0])
    if not m:
        print(patch_lines[0])
        raise Exception("Expected hash at first line of patch")
    if m.group(1) != hash:
        raise Exception("Hash of file does not match the hash in patch")
    return __apply_patch(old_lines, patch_lines[1:])

if __name__ == '__main__': 
    print("This library provides 4 useful functions:")
    print("1. get_verified_unix_diff(old_filename, new_filename)")
    print("2. apply_diff_unchecked(old_lines, patch_lines)")
    print("3. get_hashes(patch_filename)")
    print("4. check_hash_matches(lines, hash)")
