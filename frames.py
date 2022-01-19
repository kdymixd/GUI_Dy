import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from figure import Image_Plot


def give_focus(event):
    l = event.widget
    l.focus_set()    


def destroying(event):
    w = event.widget
    w.destroy()


###############Custom widgets###############


# Button highlighting when cursor on it
class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground
        
# Checkbutton highlighting when cursor on it        
class HoverCheckButton(tk.Checkbutton):
    def __init__(self, master, **kw):
        tk.Checkbutton.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground
class FileFrame(tk.Frame):
    def __init__(self, parent, mainapp,  *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.mainapp=mainapp
        ## Tkinter Vars ##
        self.var_day_in_list = tk.StringVar()
        self.var_watch_camera = tk.IntVar()  
        self.var_live_update = tk.IntVar()
        #Init TkVars
        self.init_tk_vars()
        ## Tkinter widgets ##
        # List runs and its scrollbars #
        self.label_list_runs = tk.Label(self, text = 'List run ', font = 'CMUBright')
        self.scrollbar_runs_y = tk.Scrollbar(self)
        self.list_runs = tk.Listbox(self ,yscrollcommand = self.scrollbar_runs_y.set, font = 'CMUBright', activestyle = 'dotbox', height = 15, width = 25, selectbackground = 'LightSkyblue1', selectforeground = 'black', exportselection=False, selectmode='single') 
        self.label_list_runs.grid(row = 1, column = 1, sticky='w')
        self.list_runs.grid(row = 2, column = 1, rowspan = 11, sticky = 'wn') 
        self.scrollbar_runs_y.config( command = self.list_runs.yview )
        self.scrollbar_runs_y.grid( row = 2, rowspan = 11, column = 2, sticky = 'nsw', padx=(0,20))
        self.list_runs.bind('<Enter>', give_focus)
        self.list_runs.bind("<Button-1>", give_focus)
        self.list_runs.bind('<<ListboxSelect>>', self.mainapp.on_new_run_selected)
        # List images and its scrollbars #
        self.label_list_images = tk.Label(self, text = 'List images', font = 'CMUBright')
        self.label_day_in_list = tk.Label(self, font = 'CMUBright',textvariable=self.var_day_in_list)
        self.scrollbar_images_x = tk.Scrollbar(self, orient = 'horizontal')
        self.scrollbar_images_y = tk.Scrollbar(self)
        self.list_images = tk.Listbox(self, xscrollcommand = self.scrollbar_images_x.set, yscrollcommand = self.scrollbar_images_y.set, font = 'CMUBright', activestyle = 'dotbox', height = 15, width = 75, selectbackground = 'LightSkyblue1', selectforeground = 'black', exportselection=False, selectmode='single') 
        self.label_list_images.grid(row = 1, column = 3, sticky='w')
        self.label_day_in_list.grid(row = 1, column = 4, sticky='w')
        self.list_images.grid(row = 2, column = 3, rowspan = 11,columnspan=2, sticky = 'wne') 
        self.scrollbar_images_y.config( command = self.list_images.yview )
        self.scrollbar_images_y.grid( row = 2, rowspan = 11, column = 5, sticky = 'nsw')
        self.scrollbar_images_x.config( command = self.list_images.xview )
        self.scrollbar_images_x.grid( row = 13, column = 3, columnspan=2, sticky = 'wne')
        self.list_images.bind('<Enter>', give_focus)
        self.list_images.bind("<Button-1>", give_focus)
        self.list_images.bind('<<ListboxSelect>>', self.mainapp.on_new_image_selected)
        # List options #
        check_live_update = HoverCheckButton(self, text='Display new', variable=self.var_live_update, font = 'CMUBright', activebackground = 'LightSkyblue1')
        check_live_update.grid(row=7, column = 6, columnspan=2, sticky= 'w')
        check_watch_camera = HoverCheckButton(self, text='Watch camera', variable=self.var_watch_camera, font = 'CMUBright', activebackground = 'LightSkyblue1')
        check_watch_camera.grid(row=8, column = 6, columnspan=2, sticky= 'w')
        button_refresh = HoverButton(self, text = 'Refresh', width = 11, activebackground = 'LightSkyblue1', command = self.mainapp.analyze_one_shot)
        button_refresh.grid(row=3, column = 6, columnspan=2, sticky= 'ne')
        button_last = HoverButton(self, text = 'Last', width = 11, activebackground = 'LightSkyblue1', command = self.mainapp.on_last_image)
        button_last.grid(row=4, column = 6, columnspan=2, sticky= 'ne')
        button_browselist = HoverButton(self, text = 'Browse list', width = 11, activebackground = 'LightSkyblue1', command = self.mainapp.on_browse)
        button_browselist.grid(row=5, column = 6, columnspan=2, sticky= 'ne')

    
    # initialization of tk_vars
    def init_tk_vars(self):
        #default value of variables
        LIVE_UPDATE = 1
        self.var_day_in_list.set(self.mainapp.today)
        self.var_live_update.set(LIVE_UPDATE)

class PlotFrame(tk.Frame):
    def __init__(self, parent, mainapp,*args, **kwargs):
        tk.Frame.__init__(self, parent,*args, **kwargs)
        self.mainapp=mainapp
        ## Tkinter Vars ##
        self.var_gauss_fit = tk.IntVar()
        self.var_fixed_cursors=tk.IntVar()
        self.var_vx=tk.IntVar()
        self.var_vy=tk.IntVar()
        self.var_xmin = tk.IntVar()
        self.var_xmax = tk.IntVar()
        self.var_ymin = tk.IntVar()
        self.var_ymax = tk.IntVar() 
        self.var_nat = tk.StringVar()
        self.var_fix_cbar = tk.IntVar()

        #Init TkVars
        self.init_tk_vars()
        #  Cursors  #
        check_fixed_cursor = HoverCheckButton(self, text='Fixed cursor', variable=self.var_fixed_cursors, font = 'CMUBright', activebackground = 'LightSkyblue1')
        check_fixed_cursor.grid(row=8, column = 12, sticky= 'w')
        label_x = tk.Label(self, text='Position x', font = 'CMUBright') 
        label_y = tk.Label(self, text='Position y', font = 'CMUBright') 
        entry_cut_x = tk.Entry(self, textvariable = self.var_vx, width = 6) 
        entry_cut_y = tk.Entry(self, textvariable = self.var_vy, width = 6)
        label_x.grid(row = 9, column = 10, sticky = 'e') 
        entry_cut_x.grid(row = 9, column = 11, sticky = 'e')
        label_y.grid(row = 9, column = 13, sticky = 'w')
        entry_cut_y.grid(row = 9, column = 14, sticky = 'w')

        #  ROI  #
        label_roi=tk.Label(self, text = 'ROI:', font = 'CMUBright')
        label_xmin = tk.Label(self, text='xmin', font = 'CMUBright')
        label_xmax = tk.Label(self, text='xmax', font = 'CMUBright') 
        label_ymin = tk.Label(self, text='ymin', font = 'CMUBright')
        label_ymax = tk.Label(self, text='ymax', font = 'CMUBright')  
        button_set_view_as_ROI = HoverButton(self, text="Set to current view", width=15, activebackground = 'LightSkyblue1', command = self.mainapp.on_set_view_as_ROI)
        entry_cut_xmin = tk.Entry(self, textvariable = self.var_xmin, width = 6)
        entry_cut_xmax= tk.Entry(self, textvariable = self.var_xmax, width = 6) 
        entry_cut_ymin = tk.Entry(self, textvariable = self.var_ymin, width = 6)
        entry_cut_ymax = tk.Entry(self, textvariable = self.var_ymax, width = 6)
        label_roi.grid(row = 0, column = 12, sticky = 'n')
        label_xmin.grid(row = 1, column = 10, sticky = 'e')  
        entry_cut_xmin.grid(row = 1, column = 11, sticky = 'e')
        label_ymin.grid(row = 1, column = 13, sticky = 'w')
        entry_cut_ymin.grid(row = 1, column = 14, sticky = 'w')
        label_xmax.grid(row = 2, column = 10, sticky = 'e')  
        entry_cut_xmax.grid(row = 2, column = 11, sticky = 'e')
        label_ymax.grid(row = 2, column = 13, sticky = 'w')
        entry_cut_ymax.grid(row = 2 , column = 14, sticky = 'w')
        button_set_view_as_ROI.grid(row=3, column=12, sticky='n')
        button_default = HoverButton(self, text = 'Back to\ndefault', width = 15, activebackground = 'LightSkyblue1', command = self.mainapp.on_back_to_default)
        button_default.grid(row=11, column = 12, columnspan=1, sticky= 'n')

        #  Atom number  - Display value #
        label_atom_number_txt= tk.Label(self, text = 'Atom  number:', font = 'CMUBright' )
        label_atom_number_txt.grid(row = 4, column = 12, columnspan = 1, sticky='n')#, sticky = 'w')
        label_atom_number= tk.Label(self, textvariable = self.var_nat, font = ('CMUBright',30), bg = 'white', height = 2, width = 10)
        label_atom_number.grid(row = 5, column = 11, columnspan = 3, sticky='n') 
        label_abs_image = tk.Label(self, text = 'Absorption image', font = 'CMUBright')
        label_abs_image.grid(row = 0, column = 1, columnspan = 5)
        label_abs_cuts = tk.Label(self, text = 'Cuts', font = 'CMUBright')
        label_abs_cuts.grid(row = 0, column = 6, columnspan = 4)
        # Atom number - Option #
        check_gauss_fit = HoverCheckButton(self, text='Gaussian fit', variable = self.var_gauss_fit, font = 'CMUBright', activebackground = 'LightSkyblue1')
        check_gauss_fit.grid(row=6, column = 12, sticky= 'w')


        # Colorbar - Option #
        check_fix_colorbar = HoverCheckButton(self, text= 'Fix colorbar', variable= self.var_fix_cbar, font = 'CMUBright', activebackground = 'LightSkyblue1')
        check_fix_colorbar.grid(row=7, column=12, sticky='w')


        # Image display #

        self.image_plot = Image_Plot(self)
        self.canvas1 = FigureCanvasTkAgg(self.image_plot.f1, self)
        self.canvas1.get_tk_widget().grid(row = 1, column =1, rowspan = 25, columnspan = 5, sticky ='w')
        self.canvas1.get_tk_widget().configure(takefocus=False)
        self.canvas1.draw()
        self.toolbarFrame = tk.Frame(master=self)
        self.toolbarFrame.grid(row=32,column=1, columnspan = 6, sticky ='w')
        self.toolbar = NavigationToolbar2Tk(self.canvas1, self.toolbarFrame)      
        self.canvas2 = FigureCanvasTkAgg(self.image_plot.f2, self)
        self.canvas2.get_tk_widget().grid(row = 1, column =6, rowspan = 25, columnspan = 4)#, sticky ='w')
        self.canvas2.get_tk_widget().configure(takefocus=False)
        self.canvas2.draw()

            # initialization of tk_vars
    def init_tk_vars(self):
        #default value of variables
        VALUE_NAT = 0
        GAUSS_FIT = 0
        FIXED_CURSOR = 0
        VALUE_X = 0
        VALUE_Y = 0
        VALUE_XMIN = 0
        VALUE_XMAX = 0 
        VALUE_YMIN = 0 
        VALUE_YMAX = 0
        FIX_COLORBAR = 0
        self.var_gauss_fit.set(GAUSS_FIT)
        self.var_fixed_cursors.set(FIXED_CURSOR)
        self.var_vx.set(str(VALUE_X))
        self.var_vy.set(str(VALUE_Y))
        self.var_xmin.set(str(VALUE_XMIN))
        self.var_ymin.set(str(VALUE_YMIN))
        self.var_xmax.set(str(VALUE_XMAX))
        self.var_ymax.set(str(VALUE_YMAX))
        self.var_nat.set(str(VALUE_NAT))
        self.var_fix_cbar.set(FIX_COLORBAR)