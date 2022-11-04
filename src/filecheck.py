import os
import subprocess
import sys
import shutil
import hashlib
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MonitorFolder(FileSystemEventHandler):
    def __init__(self, hash_dict):
        self.hash_dict = hash_dict
        print(self.hash_dict)

    FILE_SIZE=1000
    # def on_any_event(self, event):
    #     print(event.src_path, event.event_type)

    def save_file(self, file):
        shutil.copy2(file, "savedStates/")

    def hash_file(self,file):
        print("hash_file: ", file)
        result = subprocess.check_output(f'certutil -hashfile "{file}" MD5', shell=True)
        hash = result.splitlines()[1]
        return hash.decode('utf-8')

    def on_file_open(self, file):
        print("On file open: ", file)
        # Check if open or modified
        filehash = self.hash_file(file)
        print("FILE HASH ASDASDAKSJSHDASJKLDH" , filehash)
        print (f"COMPARISON {filehash} with {self.hash_dict[file]}. Types are {type(filehash)} and {type(self.hash_dict[file])}")
        if filehash == self.hash_dict[file]:
            print("Open file")
        else:
            self.hash_dict[file] = filehash
            print("Modified file")

    def on_created(self, event):
        print(event.src_path, event.event_type)

    def on_modified(self, event):
        if os.path.isfile(event.src_path):
            self.on_file_open(event.src_path)
        print(event.src_path, event.event_type)

    def on_deleted(self, event):
        print(event.src_path, event.event_type)

    # def checkFolderSize(self,src_path):
    #     if os.path.isdir(src_path):
    #         if os.path.getsize(src_path) >self.FILE_SIZE:
    #             print("Time to backup the dir")
    #     else:
    #         if os.path.getsize(src_path) >self.FILE_SIZE:
    #             print("very big file, needs to be backed up")

# Enumerates all the files in the folder specified
def folder_loader(src_path):
    no_of_files = 0
    file_array = []
    for root, d, files in os.walk(src_path):
        for file in files:
            file_array.append(os.path.join(root,file))
            no_of_files += 1
            sys.stdout.write(f"\r{no_of_files} files loaded.")
    print(file_array)
    return generate_hash(file_array)

# Generate hash of all files in the specified folder
def generate_hash(file_array):
    no_of_files = len(file_array)
    hash_dict = {}
    files_hashed = 0
    for file in file_array:
        with open(file,"rb") as f:
            data = f.read()
            md5hash = hashlib.md5(data).hexdigest()
            hash_dict[file] = md5hash
        files_hashed += 1
        sys.stdout.write(f"\r{files_hashed} out of {no_of_files} hashed.")
    print("hash dict is \n", hash_dict)
    return hash_dict

if __name__ == "__main__":
    src_path = "D:\SIT STUFF\Year 2\ICT 2202 - Digital Forensics/test3"
    start_time = time.time()
    hash_dict = folder_loader(src_path)
    print("--- %s seconds ---" % (time.time() - start_time))
    event_handler = MonitorFolder(hash_dict)
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    print("Monitoring started")
    observer.start()
    try:
        while(True):
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()