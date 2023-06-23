#################################################################################################
######################################### Main file GUI #########################################
#################################################################################################
#   Architecture requiered for the GUI to work properly :
#       Data
#           AAAA (ex: 2022)
#               MM (ex: 10)
#                   DD (ex: 18)
#                       SEQ (folders of the different sequences)
#                           .tiff files
#       Data_Analysis
#       Cicero
#           AAAA (ex: 2022)
#               MmmAAAA (ex: Oct2022)
#                   DDMmmAAAA (ex: 18Oct2022)
#                       RunLogs
#                           .clg files
#       GUI
#           GUIAtom
#               UI.py
#               analysis.py
#               Dy.py
#               frames.py
#               backend.py
#               config.py
#               config.ini
#               figure.py    
#               folder_explorer.py
#
# UI.py file must be 2 levels bellow Data, data_Analysis and Cicero. 
# If there are problems with the architecture, see get_root_path(), get_day_folder() and folder_explorer.py
#
#################################################################################################

############################################ Imports ############################################
import configparser
import tkinter as tk 
from scipy.constants import c
import matplotlib
import numpy as np



import scipy.constants as c
# from backend_tkagg2 import FigureCanvasTkAgg, NavigationToolbar2Tk

from matplotlib.figure import Figure
import datetime
from datetime import date
#local imports
from backend import Backend
import folder_explorer
from frames import FileFrame, PlotFrame, give_focus
import config
import analysis
import os
import time
from PIL import Image, ImageSequence
from tqdm import tqdm

############################################## GUI ##############################################

class MainApplication(tk.Frame, folder_explorer.FolderExplorer):
    
    def __init__(self, parent, day=None,*args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.backend=Backend(parent)
    
        ## Variables ##
        self.day=day
        self.root_path = self.get_root_path()
        """ self.day_path corresponds tyo the directory of the folder currently open on the GUI.
        It's the day date when the GUI is launched, and the chosen directory after ones browse """
        if self.day is None:
            self.day_path=self.get_day_folder()
        else :
            self.day_path = os.path.join(self.root_path,"Data")+ '\\' + self.day
        print(self.day_path)
        
        ## Frames ##
        self.fileFrame=FileFrame(self.parent,self)
        self.fileFrame.grid(column= 1, row=2)
        self.plotFrame= PlotFrame(self.parent,self)
        self.plotFrame.grid(row=1, column=1)
        self.parent.bind("<<RunsEvent>>", self.handle_runs_event)
        self.parent.bind("<<ImagesEvent>>", self.handle_images_event)
        self.parent.bind("<<CursorEvent>>", self.on_new_cursor)
        self.analysis=None
        self.C_sat=np.inf
        # self.C_sat=21570

        ##############################################
        self.start()
    #Callbacks

    def start(self):
        #Initial runs
        self.init_runs()
        #Start watchdog on folders
        self.backend.start_run_watchdog(self.day_path)
        
    def get_root_path(self):
        ''' Get the adress of the folder containning folders Data, Cicero and Data_Analysis 
        suposedly 2 stages before the adresse from which the app was launched
        See expected architecture above
        '''
        current_path = os.getcwd()
        try :
            root_path = os.path.dirname(os.path.dirname(current_path)) 
            if os.path.isdir(os.path.join(root_path,"Data")) and os.path.isdir(os.path.join(root_path,"Data_Analysis")) and os.path.isdir(os.path.join(root_path,"Cicero")):
                return root_path
            else:
                tk.messagebox.showerror(title="Error", message = "Your architecture is not valid; see expected architecture in UI.py file")
                
        except :
            tk.messagebox.showerror(title="Error",message="Your architecture is not valid; see expected architecture in UI.py file")
            return
        print(root_path)
        
            
    def get_day_folder(self):
        '''
        Gets current day folder in config file
        '''
        t = str(date.today()).replace("-", "\\")
        day_folder = os.path.join(self.root_path,"Data") + '\\' + t
        
        if not os.path.exists(day_folder):
            os.makedirs(day_folder)
            
        return day_folder
    
   
    def analysis_selected_data(self, path, folder, root):
        '''
        Creates one txt file for the folder selected (path)
        the txt file contained data analysis of the tiff files contained in the corresponding folder
        txt file is stored in the day folder of Data_Analyse folder
        '''
        analysis_path = path.replace("Data", "Data_Analysis")
             # Ouvre le fichier texte pour y ajouter du contenu, le crée s'il n'existe pas
        if not os.path.isfile(os.path.join(analysis_path,folder)+'.txt'):
            print('Starting analyzing ...')
            if not os.path.exists(analysis_path):
                os.makedirs(analysis_path)
            files = self.match_cicero(path,folder,root)
            n = len(files)
            if files != [] :
                fichier = open(os.path.join(analysis_path,folder)+'.txt','a')
                fichier.write("Name Frame \t Name Log \t A \t A2 \t center_x \t center_y \t sigma_x \t sigma_y \t offset \t sigma2_z \t sigma2_y \t Nombre d'atomes fit \t Nombre d'atomes fit2 \t Nombre d'atomes cam \n")
                print("Data analyzed with camera : {}".format(self.plotFrame.var_cam_name.get()))
                for tiff,clg in tqdm(files, total = n, desc='Analyzing data'):      # Barre de progression                   
                         analysis_frame = analysis.Analysis_data(os.path.join(path,folder,tiff),self.plotFrame.var_theta.get(),self.plotFrame.var_cam_name.get(),self.plotFrame.var_rotation_angle.get(),self.plotFrame.var_angle_12_PXF.get(), self.plotFrame.var_angle_ver_TC.get(),self.plotFrame.var_gauss_fit.get(), self.plotFrame.var_2_gauss_fit.get(),self.plotFrame.var_xmin.get(),self.plotFrame.var_xmax.get(),self.plotFrame.var_ymin.get(),self.plotFrame.var_ymax.get())
                         data = analysis_frame.process()
                         fichier.write(" {name} \t {cic} \t {A:.8f} \t {A2:.8f} \t {x:.8f} \t {y:.8f} \t {sx:.8f} \t {sy:.8f} \t {off:.8f} \t {sx2:.8f} \t {sy2:.8f} \t {atfit:.8f} \t {atfit2:.8f} \t {atcam:.8f} \n".format(name=tiff,cic=clg,A=data[0],A2=data[1],x=data[2],y=data[3],sx=data[4],sy=data[5],off=data[6],sx2=data[7],sy2=data[8],atfit=data[9],atfit2=data[10],atcam=data[11]))
                fichier.close()
                print('Data_Analysis up to date')
            else :
                print("Missing files")
        else :
            print('Data already analyzed')
  
        
    #handles events triggered when a run is deleted or created
    def handle_runs_event(self, event):
        new_event=self.backend.runs_queue.get()
        print('new_event {} '.format(new_event))
        if new_event.event_type=="created":
            self.add_new_run(new_event.src_path)
        elif new_event.event_type=="deleted":
            self.delete_run(new_event.src_path)
        else:
            print("Unknown run event type")
    
    #handles events triggered when an image is deleted or created
    def handle_images_event(self, event):
        new_event=self.backend.images_queue.get()
        print("new_event {}".format(new_event))
        selection=self.fileFrame.list_images.curselection() #image before modifying the list
        if not selection: #We check if an image is selected before adding or removing an image
            is_selection=False
        else:
            is_selection=True
            before_change=self.fileFrame.list_images.get(self.fileFrame.list_images.curselection()[0])
        if new_event.event_type=='created':
            self.add_new_image(new_event.src_path)#We add the new image to the list
            live_update=self.fileFrame.var_live_update.get() 
            if live_update: #If we want to live update we have to switch the selection to the most recent image
                self.fileFrame.list_images.select_clear(0,'end')
                self.fileFrame.list_images.selection_set(0) #we put the selection back on the first element
                self.analyze_image(self.fileFrame.list_images.get(self.fileFrame.list_images.curselection()[0]))
        elif new_event.event_type=='deleted':
            self.delete_image(new_event.src_path)
        
        else : 
            print("Unknown image event type")
        index_after_change=self.fileFrame.list_images.curselection()[0]
        after_change=self.fileFrame.list_images.get(index_after_change)
        if is_selection and before_change != after_change: #If selection changed we reanalyze the result
            self.analyze_image(after_change)


    def on_new_image_selected(self, event):
        self.analyze_image(self.fileFrame.list_images.get(self.fileFrame.list_images.curselection()[0]))


    def on_new_run_selected(self, event):
        index_new_run=self.fileFrame.list_runs.curselection()[0]
        new_run=self.fileFrame.list_runs.get(index_new_run)
        start_time=time.time()
        self.backend.stop_images_watchdog() #we stop the previous watch on previous run dir
        print(f"Time to stop watchdog: {time.time()-start_time:} s")
        start_time=time.time()
        self.init_images() #we initialize the images
        print(f"Time to init images: {time.time()-start_time:} s")
        self.fileFrame.list_images.selection_clear(0,'end')
        self.fileFrame.list_images.selection_set(0)
        start_time=time.time()
        self.analyze_image(self.fileFrame.list_images.get(0))
        print(f"Time to analyze first image: {time.time()-start_time:} s")
        start_time=time.time()
        self.backend.start_images_watchdog(self.day_path, new_run) #we start watching the new run dir
        print(f"Time to start watchdog: {time.time()-start_time:} s")
    
    #Put name of selected image in clipboard when right click
    def copy_image_selection(self, event):
        index_image_name=self.fileFrame.list_images.curselection()[0]
        image_name=self.fileFrame.list_images.get(index_image_name)
        print(image_name)
        self.parent.clipboard_clear()
        self.parent.clipboard_append(image_name)

    #Put name of selected run in clipboard when right click
    def copy_run_selection(self, event):
        index_image_name=self.fileFrame.list_runs.curselection()[0]
        image_name=self.fileFrame.list_runs.get(index_image_name)
        print(image_name)
        self.parent.clipboard_clear()
        self.parent.clipboard_append(image_name)

    def on_set_view_as_ROI(self):
        xlims, ylims=self.plotFrame.image_plot.get_lims()
        self.plotFrame.var_xmin.set(int(xlims[0]))
        self.plotFrame.var_xmax.set(int(xlims[1]))
        self.plotFrame.var_ymin.set(int(ylims[0]))
        self.plotFrame.var_ymax.set(int(ylims[1]))

    def on_new_cursor(self,event):
        self.plotFrame.var_vx.set(event.x)
        self.plotFrame.var_vy.set(event.y)
        self.plotFrame.image_plot.plot_new_cursor((event.x, event.y))

    def on_select_new_background(self):
        new_selection=self.plotFrame.image_plot.toggle_selector()
        if new_selection is not None:
            self.analysis.set_background(new_selection)
            if self.plotFrame.show_background["state"]=="disabled":
                self.plotFrame.show_background.configure(state=tk.NORMAL)
                self.plotFrame.check_background_correction.configure(state=tk.NORMAL)
                
    def on_camera_selected(self, event):
        ''' We update the values of camera_name and pixel_size  and then 
        we recalcul the atom number and update the plot
        '''
        cam_name = self.plotFrame.label_camera_name.get()
        self.plotFrame.var_cam_name.set(cam_name)
        pixel_size = "{:.2f}".format(float(config.config_parser[cam_name]["pixelsize"])/float(config.config_parser[cam_name]["magnification"]))
        self.plotFrame.var_pixel_size.set(pixel_size)
        print(cam_name, pixel_size)
        start_time=time.time()
        try:
            self.analyze_image(self.fileFrame.list_images.get(0))
            print(f"Time to analyze first image: {time.time()-start_time:} s")
        except Exception:
            print('Select an image')
            
        start_time=time.time()

    def on_show_background(self):
        self.plotFrame.image_plot.toggle_selector(show_only=True)
        
    def on_back_to_default(self):
        print("on back to default")
    
    def analyze_one_shot(self):
        print("analyze one shot")

    def on_last_image(self):
        print("on last image")

    def on_browse(self):
        selected_path=tk.filedialog.askdirectory(initialdir=os.path.join(self.root_path,"Data"), title="Select run", mustexist=True )
        selected_path=os.path.normpath(selected_path)
        splitted=selected_path.split(os.path.sep)
        print(splitted)
        try: 
            day = str(date(int(splitted[-3]),int(splitted[-2]), int(splitted[-1]))).replace("-", "\\")
        except:
            tk.messagebox.showerror(title="Error",message="{}\nis not a valid run path".format(selected_path))
            return
        self.close()
        self.parent.destroy()
        new_window(day)
        
    def on_analysis(self):
        ''' this function saves the analyzed data of the selected folder in Data_Analysis
        '''
        if len(self.fileFrame.list_runs.curselection()) == 0:
            print("Please select a folder to analyze")
        else :
            index_new_run=self.fileFrame.list_runs.curselection()[0]
            new_run=self.fileFrame.list_runs.get(index_new_run)
            self.analysis_selected_data(self.day_path, new_run, self.root_path)
        
        
    def analyze_image(self, image):
        run=self.fileFrame.list_runs.get(self.fileFrame.list_runs.curselection()[0])
        path_to_image=self.get_path_to_image(run, image)
        if self.analysis is None:
            self.analysis=analysis.Analysis(path_to_image, self.plotFrame)
        else: 
            self.analysis.update_analysis(path_to_image)
            self.analysis.plot_and_process(C_sat=self.C_sat)
        #If the camera changed we set the labels to the new value
        if self.analysis.camera_name!=self.plotFrame.var_cam_name.get():
            self.plotFrame.var_cam_name.set(self.analysis.camera_name)
            eff_pixel_size=float(config.config_parser[self.analysis.camera_name]["pixelsize"])/float(config.config_parser[self.analysis.camera_name]["magnification"])
            self.plotFrame.var_pixel_size.set("{:.2f}".format(eff_pixel_size))
        
        
    def close(self):
        #What to do when closing
        self.backend.stop_images_watchdog()
        self.backend.stop_runs_watchdog()
        print("close")



def new_window(day=None): 
    def close():
        main.close()
        root.destroy()
    root = tk.Tk()
    main=MainApplication(root, day)
    root.title("La puissance du GUI")
    #Close everything when window is closed
    root.protocol("WM_DELETE_WINDOW",close)
    root.mainloop()
if __name__ == "__main__":
    new_window()
        