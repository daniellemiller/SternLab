#! /usr/local/python_anaconda/bin/python3.4

import os
from os import path


def check_filename(filename, Truefile = True):
    """
    checks if filename is legit and returns its absolute path
    :param filename: input file path
    :param Truefile: is it an existing file (default: True)
    :return: absolute filename path
    """
    if filename == None:
        raise Exception("you must specify a file name")
    filename = path.abspath(filename)
    if Truefile and not path.isfile(filename):
        raise Exception("file %s is not a real file" % filename)
    return filename


def check_dirname(dirname):
    """
    checks if dirname is legit and returns its absolute path
    :param dirname: input directory path
    :return: absolute directory path
    """
    if dirname == None:
        raise Exception("you must specify a dir name")
    if not path.isabs(dirname):
        dirname = path.abspath(dirname)
    if not path.isdir(dirname):
        raise Exception("dir name %s does not exist" % dirname)
    return dirname


def make_dir(dir):
    """
    makes directory if does not exist
    :param dir:  directory to create
    """
    if not os.path.isdir(dir):
        os.mkdir(dir)