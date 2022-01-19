import tkinter as tk 
from scipy.constants import c
import matplotlib


matplotlib.use('TkAgg')
import scipy.constants as c
# from backend_tkagg2 import FigureCanvasTkAgg, NavigationToolbar2Tk

from matplotlib.figure import Figure
import tkinter as tk
import datetime
import os
#local imports
from backend import Backend
import backend
import folder_explorer
from frames import FileFrame, PlotFrame, give_focus
import config
import analysis


class MainApplication(tk.Frame, folder_explorer.FolderExplorer):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.backend=Backend(parent)
        ## Variables ## 
        self.today = datetime.date.today()
        self.day_path=None
        self.set_day_path(config.config_parser["filesystem"]["passerelle_path"])
        ## Frames ##
        self.fileFrame=FileFrame(self.parent,self)
        self.fileFrame.grid(column= 1, row=2, sticky='ew')
        self.plotFrame= PlotFrame(self.parent,self)
        self.plotFrame.grid(row=1, column=1, sticky='ew')
        self.parent.bind("<<RunsEvent>>", self.handle_runs_event)
        self.parent.bind("<<ImagesEvent>>", self.handle_images_event)
        self.parent.bind("<<CursorEvent>>", self.on_new_cursor)

        ##############################################
        self.start()

    #Callbacks

    def start(self):
        #Initial runs
        self.init_runs()
        #Start watchdog on folders
        self.backend.start_run_watchdog(self.day_path)
    
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
        self.backend.stop_images_watchdog() #we stop the previous watch on previous run dir
        self.init_images() #we initialize the images
        self.fileFrame.list_images.selection_clear(0,'end')
        self.fileFrame.list_images.selection_set(0)
        self.analyze_image(self.fileFrame.list_images.get(0))
        self.backend.start_images_watchdog(self.day_path, new_run) #we start watching the new run dir
    
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
    def on_back_to_default(self):
        print("on back to default")
    
    def analyze_one_shot(self):
        print("analyze one shot")

    def on_last_image(self):
        print("on last image")

    def on_browse(self):
        #create a new window to enter date make sure the folder exists, close window and change self.today, reload everything
        print("on browse")

    def analyze_image(self, image):
        run=self.fileFrame.list_runs.get(self.fileFrame.list_runs.curselection()[0])
        path_to_image=self.get_path_to_image(run, image)
        self.analysis=analysis.Analysis(path_to_image, self.plotFrame)
        self.analysis.plot_and_process()
    def close(self):
        #What to do when closing
        print("close")

def close():
    main.close()
    root.destroy()
if __name__ == "__main__":
    root = tk.Tk()
    main=MainApplication(root)
    root.title("La puissance du GUI")
    #Close everything when window is closed
    root.protocol("WM_DELETE_WINDOW",close)
    root.mainloop()