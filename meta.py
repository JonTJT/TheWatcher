import sys
import os
import glob
import zipfile
import xml.dom.minidom
from datetime import datetime


import dateutil.parser # pip install python-dateutil
from dateutil import tz
import olefile #pip install oletools
import csv

'''
Usage:

allMeta(imgPath) = 
    return List(
        dict{filePath, creator, lastModifiedBy, creationDate, dateModified, title, description}
    )
    
fileMeta(filePath) = 
    return dict{filePath, creator, lastModifiedBy, creationDate, dateModified, title, description}
    OR 
    return None     - for extensions that isnt under MS Office

Description:
    Office product has a different meta data stored in the files that may differ from the system stored meta data of the file
    Most of these meta data are manually typed, thus this python module helps to automates it.
    Data is retrieved from properties -> details tab

    # __Origin Meta Data__
    # 1. Creator (Author field)
    # 2. Last modified by (Last saved by)
    # 3. Creation Date (Content created)
    # 4. Modified Date (Date last saved)

    # __Descript + Content Meta Data__
    # 5. Title
    # 6. Description
'''

def allMeta(imgPath):
    # get all files first
    files = []
    for file in glob.iglob(imgPath+'/**/*.*',recursive = True):
        files.append(file)
    
    filesMeta = []
    for filePath in files:
        result = fileMeta(filePath)
        if result != None:
            filesMeta.append(result)

    savetoCSV(filesMeta)
    return filesMeta

def fileMeta(filePath):
    ext = os.path.splitext(filePath)[1]
    if ext == ".docx" or ext == ".xlsx" or ext == ".pptx":   # Microsoft new file format (*.docx, *.xlsx, *.pptx*) (xml compatible)
        return newMeta(filePath)
    elif ext == ".doc" or ext == ".xls" or ext == ".ppt":    # Microsoft old file format (*.doc, *.xls, *.ppt)
        return oldMeta(filePath)
    else:
        return None

def newMeta(filePath):
    file = zipfile.ZipFile(filePath,'r')
    core = xml.dom.minidom.parseString(file.read('docProps/core.xml'))
    xml.dom.minidom.parseString(file.read('docProps/core.xml')).toprettyxml()
    
    info = {} 
    info['filePath'] = filePath

    try:
        info['creator'] = core.getElementsByTagName('dc:creator')[0].childNodes[0].data
    except:
        info['creator'] =''

    try:
        info['lastModifiedBy'] = core.getElementsByTagName('cp:lastModifiedBy')[0].childNodes[0].data
    except:
        info['lastModifiedBy'] =''

    try:
        d = dateutil.parser.isoparse(core.getElementsByTagName('dcterms:created')[0].childNodes[0].data).astimezone(tz.gettz("Asia/Singapore"))
        d.replace(tzinfo=tz.gettz("Asia/Singapore"))
        info['creationDate'] = d.strftime("%d-%m-%Y %H:%M:%S")
    except:
        info['creationDate'] =''

    try:
        # tzinfo=tz.gettz("Asia/Singapore")
        d = dateutil.parser.isoparse(core.getElementsByTagName('dcterms:modified')[0].childNodes[0].data).astimezone(tz.gettz("Asia/Singapore"))
        d = d.replace(tzinfo=tz.gettz("Asia/Singapore"))
        info['dateModified'] = d.strftime("%d-%m-%Y %H:%M:%S")
    except:
        info['dateModified'] =''

    try:
        info['title'] = core.getElementsByTagName('dc:title')[0].childNodes[0].data
    except:
        info['title'] =''

    try:
        info['description'] = core.getElementsByTagName('dc:description')[0].childNodes[0].data
    except:
        info['description'] =''

    return info

def oldMeta(filePath):
    info = {} 
    info['filePath'] = filePath

    ole = olefile.OleFileIO(filePath)
    meta = ole.get_metadata()

    # meta.SUMMARY_ATTRIBS =
    # ['codepage', 'title', 'subject', 'author', 'keywords', 'comments',
    # 'template', 'last_saved_by', 'revision_number', 'total_edit_time',
    # 'last_printed', 'create_time', 'last_saved_time', 'num_pages',
    # 'num_words', 'num_chars', 'thumbnail', 'creating_application', 'security']

    # meta.DOCSUM_ATTRIBS = 
    # ['codepage_doc', 'category', 'presentation_target', 'bytes', 'lines', 'paragraphs',
    # 'slides', 'notes', 'hidden_slides', 'mm_clips', 'scale_crop', 'heading_pairs', 
    # 'titles_of_parts', 'manager', 'company', 'links_dirty', 'chars_with_spaces', 
    # 'unused', 'shared_doc', 'link_base', 'hlinks', 'hlinks_changed', 'version', 
    # 'dig_sig', 'content_type', 'content_status', 'language', 'doc_version']

    info['creator'] = getattr(meta, 'author').decode("utf-8") 
    info['lastModifiedBy'] = getattr(meta, 'last_saved_by').decode("utf-8") 
    info['creationDate'] = getattr(meta, 'create_time').strftime("%d-%m-%Y %H:%M:%S")
    info['dateModified'] = getattr(meta, 'last_saved_time').strftime("%d-%m-%Y %H:%M:%S")
    info['title'] = getattr(meta, 'title').decode("utf-8") 
    info['description'] = getattr(meta, 'comments').decode("utf-8") 
    
    return info

def savetoCSV(info): 

    # specifying the fields for csv file 
    fields = ['filePath', 'creator', 'lastModifiedBy', 'creationDate', 'dateModified', 'title', 'description'] 
  
    i = 1
    filename = "./result_" + str(i) + ".csv"
    while True:
        if os.path.exists(filename):
            i += 1
            filename = "./result_" + str(i) + ".csv"
        else:
            # writing to csv file 
            with open(filename, 'w') as csvfile: 
        
                # creating a csv dict writer object 
                writer = csv.DictWriter(csvfile, fieldnames = fields) 
        
                # writing headers (field names) 
                writer.writeheader() 
        
                # writing data rows 
                writer.writerows(info)

                return

if __name__ == "__main__":
    result1 = allMeta("./sample mount img")
    print(result1)
    result2 = fileMeta("sample mount img/folder 1/test.docx")
    print(result2)
 