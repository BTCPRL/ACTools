"""
Library of functions to handle maya files. Keeps other modules 'free' from maya
calls.
"""
import os
import pymel.core as pm
import maya.cmds as cmds

def new_file():
    return pm.newFile(force = True)

def import_file(file_path):
    try:
        return pm.importFile(file_path, returnNewNodes = True)
    except RuntimeError:
        raise RuntimeError('File {} does not exist'.format(file_path))

def save_file(file_path = None):
    return pm.saveFile()

def save_file_as(file_path):
    return pm.saveAs(file_path, f = True)