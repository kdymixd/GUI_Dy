from matplotlib.pyplot import show
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import RectangleSelector
from matplotlib.figure import Figure

GREINER_CM = [
    [1.0000, 1.0000, 1.0000, 1.0000],
    [0.9474, 0.9474, 1.0000, 1.0000],
    [0.8947, 0.8947, 1.0000, 1.0000],
    [0.8421, 0.8421, 1.0000, 1.0000],
    [0.7895, 0.7895, 1.0000, 1.0000],
    [0.7368, 0.7368, 1.0000, 1.0000],
    [0.6842, 0.6842, 1.0000, 1.0000],
    [0.6316, 0.6316, 1.0000, 1.0000],
    [0.5789, 0.5789, 1.0000, 1.0000],
    [0.5263, 0.5263, 1.0000, 1.0000],
    [0.4737, 0.4737, 1.0000, 1.0000],
    [0.4211, 0.4211, 1.0000, 1.0000],
    [0.3684, 0.3684, 1.0000, 1.0000],
    [0.3158, 0.3158, 1.0000, 1.0000],
    [0.2632, 0.2632, 1.0000, 1.0000],
    [0.2105, 0.2105, 1.0000, 1.0000],
    [0.1579, 0.1579, 1.0000, 1.0000],
    [0.1053, 0.1053, 1.0000, 1.0000],
    [0.0526, 0.0526, 1.0000, 1.0000],
    [0.0000, 0.0000, 1.0000, 1.0000],
    [0.0000, 0.0769, 1.0000, 1.0000],
    [0.0000, 0.1538, 1.0000, 1.0000],
    [0.0000, 0.2308, 1.0000, 1.0000],
    [0.0000, 0.3077, 1.0000, 1.0000],
    [0.0000, 0.3846, 1.0000, 1.0000],
    [0.0000, 0.4615, 1.0000, 1.0000],
    [0.0000, 0.5385, 1.0000, 1.0000],
    [0.0000, 0.6154, 1.0000, 1.0000],
    [0.0000, 0.6923, 1.0000, 1.0000],
    [0.0000, 0.7692, 1.0000, 1.0000],
    [0.0000, 0.8462, 1.0000, 1.0000],
    [0.0000, 0.9231, 1.0000, 1.0000],
    [0.0000, 1.0000, 1.0000, 1.0000],
    [0.0769, 1.0000, 0.9231, 1.0000],
    [0.1538, 1.0000, 0.8462, 1.0000],
    [0.2308, 1.0000, 0.7692, 1.0000],
    [0.3077, 1.0000, 0.6923, 1.0000],
    [0.3846, 1.0000, 0.6154, 1.0000],
    [0.4615, 1.0000, 0.5385, 1.0000],
    [0.5385, 1.0000, 0.4615, 1.0000],
    [0.6154, 1.0000, 0.3846, 1.0000],
    [0.6923, 1.0000, 0.3077, 1.0000],
    [0.7692, 1.0000, 0.2308, 1.0000],
    [0.8462, 1.0000, 0.1538, 1.0000],
    [0.9231, 1.0000, 0.0769, 1.0000],
    [1.0000, 1.0000, 0.0000, 1.0000],
    [1.0000, 0.9231, 0.0000, 1.0000],
    [1.0000, 0.8462, 0.0000, 1.0000],
    [1.0000, 0.7692, 0.0000, 1.0000],
    [1.0000, 0.6923, 0.0000, 1.0000],
    [1.0000, 0.6154, 0.0000, 1.0000],
    [1.0000, 0.5385, 0.0000, 1.0000],
    [1.0000, 0.4615, 0.0000, 1.0000],
    [1.0000, 0.3846, 0.0000, 1.0000],
    [1.0000, 0.3077, 0.0000, 1.0000],
    [1.0000, 0.2308, 0.0000, 1.0000],
    [1.0000, 0.1538, 0.0000, 1.0000],
    [1.0000, 0.0769, 0.0000, 1.0000],
    [1.0000, 0.0000, 0.0000, 1.0000],
    [0.9000, 0.0000, 0.0000, 1.0000],
    [0.8000, 0.0000, 0.0000, 1.0000],
    [0.7000, 0.0000, 0.0000, 1.0000],
    [0.6000, 0.0000, 0.0000, 1.0000],
    [0.5000, 0.0000, 0.0000, 1.0000],
]

greiner=ListedColormap(GREINER_CM)

class BlittedCursor:
    """
    A cross hair cursor using blitting for faster redraw.
    """
    def __init__(self, ax, parent):
        self.parent=parent
        self.ax = ax
        self.background = None
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')
        # text location in axes coordinates
        self._creating_background = False
        parent.canvas1.mpl_connect('draw_event', self.on_draw)
        self.active=False

    def on_draw(self, event):
        self.create_new_background()

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        return need_redraw

    def create_new_background(self):
        if self._creating_background:
            # discard calls triggered from within this function
            return
        self._creating_background = True
        self.set_cross_hair_visible(False)
        self.ax.figure.canvas.draw()
        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)
        self.set_cross_hair_visible(True)
        self._creating_background = False

    def on_mouse_move_or_key_press(self, event):
        if self.background is None:
            self.create_new_background()
        if not event.inaxes or not self.active:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.restore_region(self.background)
                self.ax.figure.canvas.blit(self.ax.bbox)
        else:
            self.set_cross_hair_visible(True)
            # update the line positions
            x, y = event.xdata, event.ydata
            self.horizontal_line.set_ydata(y)
            self.vertical_line.set_xdata(x)
            self.ax.figure.canvas.restore_region(self.background)
            self.ax.draw_artist(self.horizontal_line)
            self.ax.draw_artist(self.vertical_line)
            self.ax.figure.canvas.blit(self.ax.bbox)

    def on_key_press(self, event):
        if event.inaxes != self.ax:
            return
        if event.x is None or event.y is None:
            return 
        if event.key == 't':
            self.active=not(self.active)
            self.on_mouse_move_or_key_press(event)
            
    def on_button_press(self, event):
        if event.inaxes != self.ax:
            return 
        if not self.active:
            return
        if event.button==1:
            x,y=int(event.xdata), int(event.ydata) #Left click
            self.active=False
            need_redraw=self.set_cross_hair_visible(self.active)
            if need_redraw:
                self.ax.figure.canvas.restore_region(self.background)
                self.ax.figure.canvas.blit(self.ax.bbox)
                self.parent.set_cursor(x,y)
                

class Image_Plot: 
    
    def __init__(self, parent):
        self.parent= parent
        self.f1 = Figure(figsize=(5.5,5), dpi=100) 
        self.f2 = Figure(figsize=(4,5), dpi=100)
        self.canvas1 = FigureCanvasTkAgg(self.f1, self.parent)
        self.a = self.f1.add_subplot(111)
        self.a.set_xlabel("X [pixels]")
        self.a.set_ylabel("Y [pixels]")
        self.canvas2 = FigureCanvasTkAgg(self.f2, self.parent)
        self.im_plot=self.a.imshow(np.random.rand(104,140), cmap=greiner, origin="lower")
        self.line_plot12, = self.a.plot([],[], color='k', linestyle='--', linewidth=0.75)
        self.line_plot34, = self.a.plot([],[], color='k', linestyle='--', linewidth=0.75)
        self.cb=self.f1.colorbar(self.im_plot, ax=self.a, shrink=0.9, orientation='horizontal')
        self.line_x=self.a.axvline(x=10, color='black', linestyle='-', linewidth=0.75)
        self.line_y=self.a.axhline(y=10, color='black', linestyle='-', linewidth=0.75)
        self.f1.tight_layout()
        self.a2 = self.f2.add_subplot(211)
        self.a2.set_xlabel("X [pixels]")
        self.x_cut,=self.a2.plot([0], [0], color = 'MidnightBlue')
        self.x_cut_fit,=self.a2.plot([0], [0], color = 'firebrick')
        self.x_cut_fit_thermal,=self.a2.plot([0], [0], 'k--')
        self.b2 = self.f2.add_subplot(212)
        self.b2.set_xlabel("Y [pixels]")
        self.y_cut,=self.b2.plot([0], [0], color = 'MidnightBlue')
        self.y_cut_fit,=self.b2.plot([0], [0], color = 'firebrick')
        self.y_cut_fit_thermal,=self.b2.plot([0], [0], 'k--')
        self.f2.tight_layout(pad=1.2)
        self.selector=RectangleSelector(self.a, self.selection_callback, useblit=True,
        button=[1, 3],  # disable middle button
        minspanx=5, minspany=5,
        spancoords='data',
        interactive=True)
        self.selector.set_active(False)
        self.selector.set_visible(False)
        self.current_selection=[0,0,0,0]
        self.blitted_cursor=BlittedCursor(self.a, self)
        self.canvas1.mpl_connect('motion_notify_event', self.blitted_cursor.on_mouse_move_or_key_press)
        self.canvas1.mpl_connect('key_press_event', self.blitted_cursor.on_key_press)
        self.canvas1.mpl_connect('button_press_event', self.blitted_cursor.on_button_press)
        self.a.callbacks.connect('xlim_changed', self.on_xlims_change)
        self.a.callbacks.connect('ylim_changed', self.on_ylims_change)
    

    def plot_im(self,im, cursor, cbar_bounds, fitted_picture, fitted_picture_thermal=None, cam=None):
        im_shape=im.shape
        self.im_plot.set_data(im)
        self.im_plot.set_extent([0,im_shape[1],0,im_shape[0]])
        if cbar_bounds is not None : 
            self.im_plot.set_clim(cbar_bounds[0], cbar_bounds[1])
        self.line_x.set_xdata(cursor[0])
        self.line_y.set_ydata(cursor[1])
        self.x_cut.set_xdata(range(im_shape[1]))
        self.x_cut.set_ydata(im[cursor[1], :])
        self.y_cut.set_xdata(range(im_shape[0]))
        self.y_cut.set_ydata(im[:,cursor[0]])
        # Axes 1&2 and 3&4 for vertical imaging
        self.line_plot12.set_data([],[])
        self.line_plot34.set_data([],[])
        if (cam == 'PixelFly' or cam == 'PixelFly_ODT') and fitted_picture is not None:
            ax = np.tan(np.pi*36/180)
            bx = cursor[1]-ax*cursor[0]
            x = np.linspace(max(0,int(-bx/ax)+1),min(int((im_shape[0]-bx)/ax),im_shape[1]),100)
            self.line_plot12.set_data(x,affine(x,ax,bx))
            ay = np.tan(np.pi*(-36)/180)
            by = cursor[1]-ay*cursor[0]
            y = np.linspace(max(int((im_shape[0]-by)/ay),0), min(im_shape[1],int(-by/ay)))
            self.line_plot34.set_data(y,affine(y,ay,by))
            
        if fitted_picture is not None:
            self.x_cut_fit.set_xdata(range(im_shape[1]))
            self.x_cut_fit.set_ydata(fitted_picture[cursor[1], :])
            self.y_cut_fit.set_xdata(range(im_shape[0]))
            self.y_cut_fit.set_ydata(fitted_picture[:,cursor[0]])
        else : 
            self.x_cut_fit.set_xdata([])
            self.x_cut_fit.set_ydata([])
            self.y_cut_fit.set_xdata([])
            self.y_cut_fit.set_ydata([])

        if fitted_picture_thermal is not None:
            self.x_cut_fit_thermal.set_xdata(range(im_shape[1]))
            self.x_cut_fit_thermal.set_ydata(fitted_picture_thermal[cursor[1], :])
            self.y_cut_fit_thermal.set_xdata(range(im_shape[0]))
            self.y_cut_fit_thermal.set_ydata(fitted_picture_thermal[:,cursor[0]])
        else : 
            self.x_cut_fit_thermal.set_xdata([])
            self.x_cut_fit_thermal.set_ydata([])
            self.y_cut_fit_thermal.set_xdata([])
            self.y_cut_fit_thermal.set_ydata([])

        self.a.relim()
        self.a2.relim()
        self.b2.relim()
        self.a.autoscale_view()
        self.a2.autoscale_view()
        self.b2.autoscale_view()
        self.canvas1.draw()
        self.canvas2.draw()
        
    def plot_new_cursor(self, cursor):
        im=self.im_plot.get_array()
        self.line_x.set_xdata(cursor[0])
        self.line_y.set_ydata(cursor[1])
        self.x_cut.set_ydata(im[cursor[1], :])
        self.y_cut.set_ydata(im[:,cursor[0]])
        self.canvas1.draw()
        self.canvas2.draw()
        
    def on_xlims_change(self, event_ax):
        self.a2.set_xlim(event_ax.get_xlim())
        self.canvas2.draw()

    def on_ylims_change(self, event_ay):
        self.b2.set_xlim(event_ay.get_ylim())
        self.canvas2.draw()

    def get_lims(self):
        xlims=self.a.get_xlim()
        ylims=self.a.get_ylim()
        return(xlims,ylims)
    
    def set_cursor(self,x,y):
        self.parent.master.event_generate("<<CursorEvent>>",x=x, y=y, when="tail")

    def selection_callback(self, eclick, erelease):
        """
        Callback for line selection.

        *eclick* and *erelease* are the press and release events.
        """
        for _ in range(4):
            self.current_selection[0]=eclick.ydata
            self.current_selection[1]=erelease.ydata
            self.current_selection[2]=eclick.xdata
            self.current_selection[3]=erelease.xdata

    def toggle_selector(self, show_only=False):
        if self.selector.visible:
            self.selector.set_visible(False)
            if show_only:
                self.selector.update()
                return None 
            self.selector.set_active(False)
            self.selector.update()
            return self.current_selection
        else:
            self.selector.set_visible(True)
            if show_only:
                self.selector.update()
                return None
            self.selector.set_active(True)
            return None

def affine(x,a,b):
    return a*x+b    