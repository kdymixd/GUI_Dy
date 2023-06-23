import datetime
import os
from stat import ST_CTIME
from tkinter.constants import S
import re
import time 

# dict to math a mounth and its number in order to 
dict_mounths = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}

regex_runs=re.compile('(.*tiff$)')
#regex_runs=re.compile("^\d{6}#") #Regex to identify run folders

#returns list of names of sub-folders of "path" ordered by modification date
def list_folders(path):
    list_of_folders=[]
    for folder in os.listdir(path):
        if os.path.isdir(os.path.join(path, folder )):
            list_of_folders.append(os.path.join(path, folder))
    list_of_folders.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return [os.path.basename(os.path.normpath(x)) for x in list_of_folders] #Get last directory of path

#returns list of names of .tiff files of "path" 
def list_images(path):
    list_of_folders=[]
    start_time=time.time()
    if os.listdir(path) == []:
        return []
    else:
        for folder in os.scandir(path):
            extention = folder.name.split('.')[-1]
            if extention == 'tiff':
                list_of_folders.append(folder.name)
        print(f"Time to run through folders: {time.time()-start_time:} s")
        list_of_folders=list_of_folders[::-1]
        return list_of_folders #Get last directory of path

class FolderExplorer:
    
    #find last day where a run is present and returns the path
    def find_last_day(self, path, depth=0):
        if depth==3:
            #We set the day
            normalized_path=os.path.normpath(path)
            day=map(int, normalized_path.split(os.path.sep)[-3:])
            self.day=datetime.date(*list(day))
            return path
        try :
            os.path.isdir(path)
        except FileNotFoundError :
            print("Wrong passerelle path")
        following=max([folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path,folder))])
        return self.find_last_day(os.path.join(path, following), depth=depth+1)
    
    def get_path_to_image(self, run, image):
        return os.path.join(self.day_path, run, image)
    
    #Poll day directory get list of runs and put it in the runs listbox
    def init_runs(self):
        list_of_runs=list_folders(self.day_path)
        self.fileFrame.list_runs.insert(0, *list_of_runs)
    
    def init_images(self):
        index_of_run=self.fileFrame.list_runs.curselection()[0]
        list_of_images=list_images(os.path.join(self.day_path, self.fileFrame.list_runs.get(index_of_run))) #get the list of images
        self.fileFrame.list_images.delete(0, 'end') #delete the previous list if there were any images inside
        self.fileFrame.list_images.insert(0, *list_of_images) #insert the new images sorted by timestamp

    #Deletes a run
    def delete_run(self, run_path):
        run=os.path.basename(os.path.normpath(run_path))
        runs_array=self.fileFrame.list_runs.get(0,'end') # get list of runs
        if run in runs_array:
            index_of_run=runs_array.index(run) #get index of run
        self.fileFrame.list_runs.delete(index_of_run)
    
    #Deletes an image
    def delete_image(self, image_path):
        image=os.path.basename(os.path.normcase(image_path))
        images_array=self.fileFrame.list_images.get(0,'end')
        if image in images_array:
            index_of_image=images_array.index(image)
        self.fileFrame.list_images.delete(index_of_image)

    def add_new_run(self,path):
        self.fileFrame.list_runs.insert(0, os.path.basename(os.path.normpath(path)))

    def add_new_image(self, path):
        image=os.path.basename(os.path.normpath(path))
        images_array=list(self.fileFrame.list_images.get(0, 'end'))
        images_array.append(image)
        images_array.sort(key=lambda x: int((x.split("_")[-1]).split(".")[0]), reverse=True)#we get the sorted array
        index_of_new_image=images_array.index(image) #we get the index of the new image
        self.fileFrame.list_images.insert(index_of_new_image, image) #we instert it in the ListBox
    
    # Get a list of files ordered by time of creation
    def order_by_date(self, path, folder):
        files = [(os.stat(os.path.join(path,folder,f))[ST_CTIME],f) for f in os .listdir(os.path.join(path,folder))]
        files.sort()
        return files
  
    # Get the list of the .clg files (cicero) corresponding to the .tiff files in folder at path adress
    def match_cicero(self, path, folder,root):
        split_path = path.split('\\')
        cic_path = os.path.join(root, "Cicero",split_path[-3],dict_mounths[split_path[-2]]+split_path[-3],split_path[-1]+dict_mounths[split_path[-2]]+split_path[-3],'RunLogs')
        list_clg = [(os.stat(os.path.join(cic_path,f))[ST_CTIME],f) for f in os .listdir(cic_path)]
        list_tiff = self.order_by_date(path,folder)
        res = []
        for s,f in list_clg:
            for t,x in list_tiff:
                if t <= s <=  t+2:
                    res.append((x,f))    
        return res
        
            
            
        

