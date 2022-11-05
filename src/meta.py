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

    # FS Meta Data (copying the folder will update the File data and selecting that directory will yield dates that are recent)
    
    # 1. Size (fsSize)
    # 2. Create Date (fsCreated)
    # 3. Last Modified Date (fsModified)
    # 4. Last Access Date (fsAccess)
    # 5. File Path (filePath)

    # __Origin Meta Data__
    # 6. Creator (Author field)
    # 7. Last modified by (Last saved by)
    # 8. Creation Date (Content created)
    # 9. Last Modified Date (Date last saved)

    # __Descript + Content Meta Data__
    # 10. Title
    # 11. Description
'''

def allMeta(imgPath):
    filesMeta = []
    for file in glob.iglob(imgPath+'/**/*.*',recursive = True):
        result = fileMeta(file)
        if result != None:
            filesMeta.append(result)

    # savetoCSV(filesMeta)
    return filesMeta

def fileMeta(filePath):

    data = {}

    # FS Meta Data
    try:
        fsMeta = os.stat(filePath)
    except:
        return {"Error": "Unable to read metadata."}
    try:
        data['fsSize'] = str(fsMeta.st_size) + " bytes"
    except:
        data['fsSize'] = "Error extracting file size"
    try:
        data['fsCreated'] = datetime.fromtimestamp(fsMeta.st_ctime, tz=tz.gettz("Asia/Singapore")).strftime("%d-%m-%Y %H:%M:%S")
    except:
        data['fsCreated'] = "Error extracting File System creation date"
    try:
        data['fsModified'] = datetime.fromtimestamp(fsMeta.st_mtime, tz=tz.gettz("Asia/Singapore")).strftime("%d-%m-%Y %H:%M:%S")
    except:
        data['fsModified'] = "Error extracting File System last modification date"
    try:
        data['fsAccess'] = datetime.fromtimestamp(fsMeta.st_atime, tz=tz.gettz("Asia/Singapore")).strftime("%d-%m-%Y %H:%M:%S")
    except:
        data['fsAccess'] = "Error extracting File System last access date"
    
    data['filePath'] = filePath
    
    # MS Office Application Meta Data
    ext = os.path.splitext(filePath)[1]
    if ext == ".docx" or ext == ".xlsx" or ext == ".pptx":   # Microsoft new file format (*.docx, *.xlsx, *.pptx*) (xml compatible)
        result = newMeta(filePath)
        data |= result
        return data
    elif ext == ".doc" or ext == ".xls" or ext == ".ppt":    # Microsoft old file format (*.doc, *.xls, *.ppt)
        result = oldMeta(filePath)
        data |= result
        return data
    else:
        return data

def newMeta(filePath):
    file = zipfile.ZipFile(filePath,'r')
    core = xml.dom.minidom.parseString(file.read('docProps/core.xml'))
    xml.dom.minidom.parseString(file.read('docProps/core.xml')).toprettyxml()
    
    info = {}

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
    try:
        info['creator'] =  getattr(meta, 'author').decode("utf-8") 
    except:
        info['creator'] =''
    try:
        info['lastModifiedBy'] = getattr(meta, 'last_saved_by').decode("utf-8") 
    except:
        info['lastModifiedBy'] =''
    try:
        info['creationDate'] = getattr(meta, 'create_time').strftime("%d-%m-%Y %H:%M:%S")
    except:
        info['creationDate'] =''
    try:
        info['dateModified'] = getattr(meta, 'last_saved_time').strftime("%d-%m-%Y %H:%M:%S") 
    except:
        info['dateModified'] =''
    try:
        info['title'] = getattr(meta, 'title').decode("utf-8")  
    except:
        info['title'] =''
    try:
        info['description'] = getattr(meta, 'comments').decode("utf-8") 
    except:
        info['description'] =''
    
    return info

# def savetoCSV(info): 

#     # specifying the fields for csv file 
#     fields = ['filePath', 'creator', 'lastModifiedBy', 'creationDate', 'dateModified', 'title', 'description'] 
  
#     i = 1
#     filename = "./result_" + str(i) + ".csv"
#     while True:
#         if os.path.exists(filename):
#             i += 1
#             filename = "./result_" + str(i) + ".csv"
#         else:
#             # writing to csv file 
#             with open(filename, 'w') as csvfile: 
        
#                 # creating a csv dict writer object 
#                 writer = csv.DictWriter(csvfile, fieldnames = fields) 
        
#                 # writing headers (field names) 
#                 writer.writeheader() 
        
#                 # writing data rows 
#                 writer.writerows(info)

#                 return

# if __name__ == "__main__":
#     result1 = allMeta("Templates")
#     print(result1)
#     # result2 = fileMeta("../../Test/presentation.pptx")
#     result2 = fileMeta("Templates/presentation.pptx")
#     print(result2)
 