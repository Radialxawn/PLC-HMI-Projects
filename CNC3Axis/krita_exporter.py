import os
import sys
from krita import *
from pathlib import Path
import re

doc = Krita.instance().activeDocument()
dirProject = os.path.dirname(os.path.dirname(doc.fileName()))
dirExport = r'C:\Users\X\Desktop\CNC3Axis'

def export_ignore(node):
    name = node.name().lower()
    return name in ['decorations-wrapper-layer', 'background', 'ref']
    
def export_rect(w, h):
    dw = doc.width() - w
    dh = doc.height() - h
    return QRect(int(dw / 2), int(dh / 2), w, h)
    
def export_name_size(node):
    name = node.name() + '.png'
    s = re.search('\[(\d+)x(\d+)\]', name)
    if s:
        g = s.group()
        k = g[1:-1].split('x')
        name = name.replace(g, '')
        return name, [int(k[0]), int(k[1])]
    return name, []

def export(topNodes):
    print('Export to %s' % (dirExport))
    Application.setBatchmode(True)
    for topNode in topNodes:
        if export_ignore(topNode) or not topNode.visible():
            continue
        print('/%s' % (topNode.name()))
        dirExportFolder = os.path.join(dirExport, topNode.name())
        if not os.path.isdir(dirExportFolder):
            os.makedirs(dirExportFolder)
        for node in topNode.childNodes():
            if export_ignore(node) or not node.visible():
                continue
            info = InfoObject()
            info.setProperty('alpha', True)
            info.setProperty('compression', 9)
            info.setProperty('forceSRGB', False)
            info.setProperty('indexed', False)
            info.setProperty('interlaced', False)
            info.setProperty('saveSRGBProfile', False)
            info.setProperty('transparencyFillcolor', [0,0,0])
            fileName, size = export_name_size(node)
            filePath = os.path.join(dirExportFolder, fileName)
            if len(size) > 0:
                node.save(filePath, doc.resolution(), doc.resolution(), info, export_rect(size[0], size[1]))
            else:
                node.save(filePath, doc.resolution(), doc.resolution(), info)
            print('  -> %s' % (fileName))
    Application.setBatchmode(False)
    print('Done')

export(doc.topLevelNodes())