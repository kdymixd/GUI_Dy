import numpy as np
from matplotlib.colors import ListedColormap
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

from matplotlib.figure import Figure
class Image_Plot: 
    def __init__(self, parent):
        self.parent= parent
        self.f1 = Figure(figsize=(5,5), dpi=100) 
        self.f2 = Figure(figsize=(4,5), dpi=100)
        self.a = self.f1.add_subplot(111)

        self.im_plot=self.a.imshow(np.zeros((20,20)), cmap=greiner, origin="lower")
        self.cb=self.f1.colorbar(self.im_plot, ax=self.a, shrink=1, orientation='horizontal')
        self.line_x=self.a.axvline(x=10, color='black', linestyle='-', linewidth=0.75)
        self.line_y=self.a.axhline(y=10, color='black', linestyle='-', linewidth=0.75)
        self.f1.tight_layout()
        self.a2 = self.f2.add_subplot(211)
        self.x_cut,=self.a2.plot([0], [0], color = 'MidnightBlue')
        self.x_cut_fit,=self.a2.plot([0], [0], color = 'firebrick')
        self.b2 = self.f2.add_subplot(212)
        self.y_cut,=self.b2.plot([0], [0], color = 'MidnightBlue')
        self.y_cut_fit,=self.b2.plot([0], [0], color = 'firebrick')
        self.f2.tight_layout()
        self.a.callbacks.connect('xlim_changed', self.on_xlims_change)
        self.a.callbacks.connect('ylim_changed', self.on_ylims_change)

    def plot_im(self,im, cursor, cbar_bounds, fitted_picture):
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
        self.a.relim()
        self.a2.relim()
        self.b2.relim()
        self.a.autoscale_view()
        self.a2.autoscale_view()
        self.b2.autoscale_view()
        self.parent.canvas1.draw()
        self.parent.canvas2.draw()


        
    def on_xlims_change(self, event_ax):
        self.a2.set_xlim(event_ax.get_xlim())
        self.parent.canvas2.draw()

    def on_ylims_change(self, event_ay):
        self.b2.set_xlim(event_ay.get_ylim())
        self.parent.canvas2.draw()

