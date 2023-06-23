from config import config_parser
import numpy as np
import cv2 as cv
import os 
import scipy.signal
from scipy.optimize import curve_fit
import Dy
#import tifffile as tiff
from PIL import Image, ImageSequence


def read_image(path):
    try:  
        img=cv.imread(path, cv.IMREAD_UNCHANGED) #we load the images
    except cv.error as e:
        # inspect error object
        print(e)
        for k in dir(e):
            if k[0:2] != "__":
                print("e.%s = %s" % (k, getattr(e, k)))
    return img

class Analysis:
    
    def __init__(self, path, plotFrame):
        self.plotFrame=plotFrame
        vx=self.plotFrame.var_vx.get()
        vy=self.plotFrame.var_vy.get()
        xmin=self.plotFrame.var_xmin.get()
        ymin=self.plotFrame.var_ymin.get()
        xmax=self.plotFrame.var_xmax.get()
        ymax=self.plotFrame.var_ymax.get()
        self.angle_vert_TC = self.plotFrame.var_angle_ver_TC.get()
        self.angle_12_PXF = self.plotFrame.var_angle_12_PXF.get()
        self.fixed_cursor = self.plotFrame.var_fixed_cursors.get()
        self.fix_colorbar=self.plotFrame.var_fix_cbar.get()
        self.folder_path=path
        self.absorption_picture=None
        self.camera_name="PixelFly"
        self.ROI=np.s_[ymin: ymax, xmin: xmax] if (ymax > ymin and xmax>xmin) else np.s_[:,:]
        self.background=None #Background to normalize images for pixel count
        self.background_correction=self.plotFrame.var_background_correction.get() # Wether we should do background correction
        self.fit_params=None
        self.gauss_fit=self.plotFrame.var_gauss_fit.get()
        self.theta_rot=self.plotFrame.var_theta.get()
        self.rotation_angle = self.plotFrame.var_rotation_angle.get()
        self.gauss_2_fit=self.plotFrame.var_2_gauss_fit.get()
        self.cursor= [vx, vy] if self.fixed_cursor else None
        self.cbar_bounds= None
        
    def update_analysis(self, path):
        vx=self.plotFrame.var_vx.get()
        vy=self.plotFrame.var_vy.get()
        xmin=self.plotFrame.var_xmin.get()
        ymin=self.plotFrame.var_ymin.get()
        xmax=self.plotFrame.var_xmax.get()
        ymax=self.plotFrame.var_ymax.get()
        self.angle_ver_TC = self.plotFrame.var_angle_ver_TC.get()
        self.angle_12_PXF = self.plotFrame.var_angle_12_PXF.get()
        self.fixed_cursor = self.plotFrame.var_fixed_cursors.get()
        self.fix_colorbar=self.plotFrame.var_fix_cbar.get()
        self.folder_path=path
        self.ROI=np.s_[ymin: ymax, xmin: xmax] if (ymax > ymin and xmax>xmin) else np.s_[:,:]
        self.gauss_fit=self.plotFrame.var_gauss_fit.get()
        self.theta_rot=self.plotFrame.var_theta.get()
        self.rotation_angle = self.plotFrame.var_rotation_angle.get()
        self.gauss_2_fit=self.plotFrame.var_2_gauss_fit.get()
        self.cursor= [vx, vy] if self.fixed_cursor else None
        self.background_correction=self.plotFrame.var_background_correction.get()

    def set_background(self, new_selection):
        new_selection=list(map(int, new_selection))
        self.background=np.s_[new_selection[0]:new_selection[1], new_selection[2]:new_selection[3]]
        
    def calculate_atom_number_count(self, pixel_size):
        return np.nansum(self.absorption_picture[self.ROI])*pixel_size**2/Dy.sigma0

    def set_camera_and_absorption_picure(self, C_sat=np.inf):
        threshold=0.02
        dict_pictures=self.open_picture()

        #dict_pictures["atoms"] -= dict_pictures["background"]
        #dict_pictures["no atoms"] -= dict_pictures["background"]

        x, y = np.indices(dict_pictures["no atoms"].shape)
        seuil = 100
        bg_roi_with = np.where((x < seuil) | (y < seuil) | (x > (np.max(x)-seuil)) | (y > (np.max(y)-seuil)), dict_pictures["atoms"], 0)
        bg_roi_noat = np.where((x < seuil) | (y < seuil) | (x > (np.max(x)-seuil)) | (y > (np.max(y)-seuil)), dict_pictures["no atoms"], 0)
        dict_pictures["no atoms"] = dict_pictures["no atoms"] * np.nanmean(bg_roi_with)/np.nanmean(bg_roi_noat)

        transmission=(dict_pictures["atoms"])/(dict_pictures["no atoms"]+1e-3)
        burned_pixels=transmission <=0
        transmission[burned_pixels] = float("nan")
        bad_pixels=dict_pictures["no atoms"]<np.nanmax(dict_pictures["no atoms"])*threshold
        transmission[bad_pixels] = float("nan")
        od = np.nan_to_num(-np.log(transmission) + (dict_pictures['no atoms']-dict_pictures['atoms'])/C_sat, nan=np.nan, posinf=np.nan, neginf=np.nan)
        self.absorption_picture=rotation_image(od)
        return rotation_image(od)


    def open_picture(self):
        anglepxf = 72
        im = Image.open(self.folder_path)
        # Le fichier .tiff contient 3 images
        # La verticale est tournée de 55.44 degrés par rapport à l'horizontale sur la cam TL, on tourne donc l'image pour que la verticale soit selon y
        if self.camera_name == 'Thorlabs 1':
            img_with_atoms = np.array(ImageSequence.Iterator(im)[0].rotate(self.angle_vert_TC-90))
            img_no_atoms = np.array(ImageSequence.Iterator(im)[1].rotate(self.angle_vert_TC-90))
            img_background = np.array(ImageSequence.Iterator(im)[2].rotate(self.angle_vert_TC-90))
        elif self.camera_name == 'PixelFly' or self.camera_name == 'PixelFly_ODT':
            img_with_atoms = np.array(ImageSequence.Iterator(im)[0].rotate(anglepxf-self.angle_12_PXF))
            img_no_atoms = np.array(ImageSequence.Iterator(im)[1].rotate(anglepxf-self.angle_12_PXF))
            img_background = np.array(ImageSequence.Iterator(im)[2].rotate(anglepxf-self.angle_12_PXF))
        elif self.camera_name == 'Thorlabs 2':
            img_with_atoms = np.array(ImageSequence.Iterator(im)[0].rotate(180))
            img_no_atoms = np.array(ImageSequence.Iterator(im)[1].rotate(180))
            img_background = np.array(ImageSequence.Iterator(im)[2].rotate(180))
         ## Remove the offest
        if  (not self.gauss_fit) and (not self.gauss_2_fit) and (self.background is not None) and (self.background_correction):
            ratio = np.nanmean(img_no_atoms[self.background]
                                         /img_with_atoms[self.background])
            img_no_atoms = img_no_atoms/ratio
            print("Correction ratio is {}".format(ratio))
        # We retrieve the name of the camera selected
        self.camera_name = self.plotFrame.var_cam_name.get()
        return {"atoms": img_with_atoms, 'no atoms': img_no_atoms, 'background': img_background}


    def set_cursor_and_cbar(self, center=None, offset=0):
        square = (1/16)*np.ones((4,4))
        if not self.fix_colorbar or not self.fixed_cursor:
            if center is None: 
                coarse_img = scipy.signal.convolve2d(self.absorption_picture[self.ROI], square, mode = 'same')
                max_od = np.nanmax(coarse_img)
                min_od = np.nanmin(coarse_img)
                ymax2, xmax2 = np.unravel_index(coarse_img.argmax(), coarse_img.shape)
                if self.ROI[0].start is not None :
                    ymax2 = ymax2 + self.ROI[0].start
                if self.ROI[1].start is not None :
                    xmax2 = xmax2 + self.ROI[1].start
            else:
                ymax2, xmax2 = center[1], center[0]
                max_od=self.absorption_picture[center[1], center[0]]
                min_od=offset

            if not self.fixed_cursor: 
                self.cursor = [xmax2, ymax2]
                self.plotFrame.var_vx.set(xmax2)
                self.plotFrame.var_vy.set(ymax2)
            if not self.fix_colorbar:
                self.cbar_bounds= [min_od, max_od]

    def plot_and_process(self, C_sat=np.inf):
        abs_picture=self.set_camera_and_absorption_picure(C_sat=C_sat)
        if (not self.gauss_fit) and (not self.gauss_2_fit):
            self.set_cursor_and_cbar()
        pixel_size = float(config_parser[self.camera_name]["pixelsize"])/float(config_parser[self.camera_name]["magnification"])*1e-6
        
        if self.gauss_fit:
            fitted_picture, A, center_x, center_y, sigma_x, sigma_y, offset =self.fit_picture()

            fitted_picture_thermal=None
            if fitted_picture is None:
                fitted_picture_thermal=None
                atom_number = self.calculate_atom_number_count(pixel_size)
                atom_number2 = 0
                self.set_cursor_and_cbar()
            else: 
                atom_number= calculate_atom_number_fit(A, sigma_x, sigma_y, pixel_size)
                atom_number2 = 0
                self.set_cursor_and_cbar(center=[int(center_x),int(center_y)], offset=offset)
                self.plotFrame.var_sig_x.set("{:.2f}".format(sigma_x))
                self.plotFrame.var_sig_y.set("{:.2f}".format(sigma_y))
        
        elif self.gauss_2_fit:
            fitted_picture, fitted_picture_thermal, A, A2, center_x, center_y, sigma_x, sigma_y, sigma2_x, sigma2_y, offset =self.fit_picture_2_gauss()
            atom_number2= calculate_atom_number_fit(A2, sigma2_x, sigma2_y, pixel_size)
            atom_number= calculate_atom_number_fit(A, sigma_x, sigma_y, pixel_size)
            self.set_cursor_and_cbar(center=[int(center_x),int(center_y)], offset=offset)

        else:
            fitted_picture=None
            fitted_picture_thermal=None
            atom_number = self.calculate_atom_number_count(pixel_size)
            atom_number2 = 0
        
        self.plotFrame.var_nat.set("{:.2e}".format(atom_number))
        self.plotFrame.var_nat2.set("{:.2e}".format(atom_number2))
        self.plotFrame.image_plot.plot_im(abs_picture, cursor=self.cursor, cbar_bounds=self.cbar_bounds, fitted_picture=fitted_picture, fitted_picture_thermal=fitted_picture_thermal,cam = self.camera_name)
    
    def fit_picture(self):
        y,x=np.indices(self.absorption_picture.shape)
        if self.theta_rot:
            try:
                popt=fit_gaussian_2D(x[self.ROI], y[self.ROI], self.absorption_picture[self.ROI], bin=5, angle = self.rotation_angle)
                return rot_gaussian(x, y, *popt), popt[0], popt[1], popt[2], popt[3], popt[4], popt[5] #we return the image and A, sigma_x, sigma_y
            except Exception:
                print("Could not fit image")
                return [None,0,0,0,0,0,0]   #If we couldn't match the image, parameters are set to 0 in analyze and we raise an exception
        else:
            popt=fit_gaussian_2D(x[self.ROI], y[self.ROI], self.absorption_picture[self.ROI], bin=5)
            return rot_gaussian(x, y, *popt), popt[0], popt[1], popt[2], popt[3], popt[4], popt[5] #we return the image and A, sigma_x, sigma_y

    def fit_picture_2_gauss(self):
        y, x=np.indices(self.absorption_picture.shape)
        popt=fit_gaussian2_2D(x[self.ROI], y[self.ROI], self.absorption_picture[self.ROI], bin=2, angle=0)
        A, A2, center_x, center_y, sigma_x, sigma_y, sigma2_x, sigma2_y, offset, angle = popt
        
        # verify that the condensed / thermal fraction were not inverted during curve_fit (sigma_thermal should be > sigma_condensed)
        if sigma2_x > sigma_x:
            sigma_x, sigma2_x = sigma2_x, sigma_x
            sigma_y, sigma2_y = sigma2_y, sigma_y
            A, A2 = A2, A

        return rot_gaussian2(x, y, *popt), rot_gaussian(x, y, A, center_x, center_y, sigma_x, sigma_y, offset, angle), A, A2, center_x, center_y, sigma_x, sigma_y, sigma2_x, sigma2_y, offset

class Analysis_data:
    '''
    This class only serve for the analysis of data and the storage of the results in the folder Data_analysis
    '''
    def __init__(self, path, thet, cam, rotation_angle, angle_12_PXF, angle_ver_TC,gaussfitflag,gaussfitflag2,xminval,xmaxval,yminval,ymaxval):
        xmin=xminval
        ymin=yminval
        xmax=xmaxval
        ymax=ymaxval
        self.ROI=np.s_[ymin: ymax, xmin: xmax] if (ymax > ymin and xmax>xmin) else np.s_[:,:]
        self.file_path=path
        self.camera_name = cam
        self.theta_rot = thet
        self.rotation_angle = rotation_angle
        self.absorption_picture=None
        self.background=None #Background to normalize images for pixel count
        self.angle_12_PXF = angle_12_PXF
        self.angle_ver_TC = angle_ver_TC
        self.gauss_fit= gaussfitflag
        self.gauss_2_fit= gaussfitflag2

    def calculate_atom_number_count(self, pixel_size):
        return np.nansum(self.absorption_picture)*pixel_size**2/Dy.sigma0

    def set_absorption_picure(self, C_sat=np.inf):
        threshold=0.02
        dict_pictures=self.open_picture()

        #dict_pictures["atoms"] -= dict_pictures["background"]
        #dict_pictures["no atoms"] -= dict_pictures["background"]

        x, y = np.indices(dict_pictures["no atoms"].shape)
        seuil = 100
        bg_roi_with = np.where((x < seuil) | (y < seuil) | (x > (np.max(x)-seuil)) | (y > (np.max(y)-seuil)), dict_pictures["atoms"], 0)
        bg_roi_noat = np.where((x < seuil) | (y < seuil) | (x > (np.max(x)-seuil)) | (y > (np.max(y)-seuil)), dict_pictures["no atoms"], 0)
        dict_pictures["no atoms"] = dict_pictures["no atoms"] * np.nanmean(bg_roi_with)/np.nanmean(bg_roi_noat)

        transmission=(dict_pictures["atoms"])/(dict_pictures["no atoms"]+1e-3)
        burned_pixels=transmission <=0
        transmission[burned_pixels] = float("nan")
        bad_pixels=dict_pictures["no atoms"]<np.nanmax(dict_pictures["no atoms"])*threshold
        transmission[bad_pixels] = float("nan")
        od = np.nan_to_num(-np.log(transmission) + (dict_pictures['no atoms']-dict_pictures['atoms'])/C_sat, nan=np.nan, posinf=np.nan, neginf=np.nan)
        self.absorption_picture=rotation_image(od)
        return rotation_image(od)

    def open_picture(self):
        '''
        get the 3 images stored in the tiff file
        '''
        anglepxf = 72
        im = Image.open(self.file_path)
        # Le fichier .tiff contient 3 images
        # La verticale est tournée de 55.44 degrés par rapport à l'horizontale sur la cam TL, on tourne donc l'image pour que la verticale soit selon y
        
        if self.camera_name == 'Thorlabs 1':
            img_with_atoms = np.array(ImageSequence.Iterator(im)[0].rotate(self.angle_ver_TC-90))
            img_no_atoms = np.array(ImageSequence.Iterator(im)[1].rotate(self.angle_ver_TC-90))
            img_background = np.array(ImageSequence.Iterator(im)[2].rotate(self.angle_ver_TC-90))
        elif self.camera_name == 'PixelFly' or self.camera_name == 'PixelFly_ODT':
            img_with_atoms = np.array(ImageSequence.Iterator(im)[0].rotate(anglepxf-self.angle_12_PXF))
            img_no_atoms = np.array(ImageSequence.Iterator(im)[1].rotate(anglepxf-self.angle_12_PXF))
            img_background = np.array(ImageSequence.Iterator(im)[2].rotate(anglepxf-self.angle_12_PXF))
        elif self.camera_name == 'Thorlabs 2':
            img_with_atoms = np.array(ImageSequence.Iterator(im)[0].rotate(180))
            img_no_atoms = np.array(ImageSequence.Iterator(im)[1].rotate(180))
            img_background = np.array(ImageSequence.Iterator(im)[2].rotate(180))
        return {"atoms": img_with_atoms, 'no atoms': img_no_atoms, 'background': img_background}
    
    def process(self, C_sat=np.inf):
        self.absorption_picture = self.set_absorption_picure(C_sat=C_sat)
        pixel_size = float(config_parser[self.camera_name]["pixelsize"])/float(config_parser[self.camera_name]["magnification"])*1e-6
        fitted_picture, A, center_x, center_y, sigma_x, sigma_y, offset, A2, sigma2_x, sigma2_y =self.fit_picture()

        if fitted_picture is None:
            return [0,0,0,0,0,0,0,0,0]
        else:
            atom_number_fit, atom_number_fit2, atom_number_cam = calculate_atom_number_fit(A, sigma_x, sigma_y, pixel_size), calculate_atom_number_fit(A2, sigma2_x, sigma2_y, pixel_size),self.calculate_atom_number_count(pixel_size)
            return [A, A2, center_x, center_y, sigma_x, sigma_y, offset, sigma2_x, sigma2_y, atom_number_fit, atom_number_fit2, atom_number_cam]
       
    def fit_picture(self):
        y,x=np.indices(self.absorption_picture.shape)
        if self.theta_rot & self.gauss_fit:
            try:
                popt=fit_gaussian_2D(x[self.ROI], y[self.ROI], self.absorption_picture[self.ROI], bin=5, angle = self.rotation_angle)
                return rot_gaussian(x, y, *popt), popt[0], popt[1], popt[2], popt[3], popt[4], popt[5], 0, 0, 0 #we return the image and A, center_x, center_y, sigma_x, sigma_y, A2, sigma2_x, sigma2_y
            except Exception:
                print("Could not fit image")
                return [None,0,0,0,0,0,0,0,0,0]   #If we couldn't match the image, parameters are set to 0 in analyze and we raise an exception
        elif self.theta_rot & self.gauss_2_fit:
            try:
                popt=fit_gaussian2_2D(x[self.ROI], y[self.ROI], self.absorption_picture[self.ROI], bin=5, angle = self.rotation_angle)
                return rot_gaussian2(x, y, *popt), popt[0],popt[2], popt[3], popt[4], popt[5], popt[8], popt[1], popt[6], popt[7] #we return the image and A, sigma_x, sigma_y
            except Exception:
                print("Could not fit image")
                return [None,0,0,0,0,0,0,0,0,0]   #If we couldn't match the image, parameters are set to 0 in analyze and we raise an exception
        elif self.gauss_2_fit:
            popt=fit_gaussian2_2D(x[self.ROI], y[self.ROI], self.absorption_picture[self.ROI], bin=5)
            return rot_gaussian2(x, y, *popt), popt[0],popt[2], popt[3], popt[4], popt[5], popt[8], popt[1], popt[6], popt[7] #we return the image and A, sigma_x, sigma_y
        else:
            popt=fit_gaussian_2D(x[self.ROI], y[self.ROI], self.absorption_picture[self.ROI], bin=5)
            return rot_gaussian(x, y, *popt), popt[0], popt[1], popt[2], popt[3], popt[4], popt[5], 0, 0, 0 #we return the image and A, sigma_x, sigma_y

# Fit functions

def rebin(a, bin):
    a=a[0: (a.shape[0]//bin)*bin, 0: (a.shape[1]//bin)*bin]
    return np.nanmean(np.nanmean(a.reshape(a.shape[0]//bin, bin, a.shape[1]//bin,bin),axis=-1), axis=-2)

def rotation(x, y, theta):
    angle=np.deg2rad(theta)
    return (np.cos(angle)*x+np.sin(angle)*y, -np.sin(angle)*x + np.cos(angle)*y)

#Simple 2d gaussian
def gaussian(x, y ,A, sigma_x, sigma_y, offset):
    return A*np.exp(-((x)**2/(2*sigma_x**2) + (y)**2/(2*sigma_y**2))) +offset

#2d gaussian with rotation
def rot_gaussian(x,y,A,x_0,y_0, sigma_x, sigma_y, offset, theta):
    x_rot, y_rot=rotation(x-x_0, y-y_0,theta)
    return gaussian(x_rot,y_rot,A,sigma_x, sigma_y, offset)

#Two 2d gaussian (thermal + BEC)
def gaussian2(x, y, A, A2, sigma_x, sigma_y, sigma2_x, sigma2_y, offset):
    return A*np.exp(-(x**2/(2*sigma_x**2) + y**2/(2*sigma_y**2))) + A2*np.exp(-(x**2/(2*sigma2_x**2) + y**2/(2*sigma2_y**2))) + offset

#2d gaussian with rotation
def rot_gaussian2(x, y, A, A2, x_0, y_0, sigma_x, sigma_y, sigma2_x, sigma2_y, offset, theta):
    x_rot, y_rot=rotation(x-x_0, y-y_0, theta)
    return gaussian2(x_rot, y_rot, A, A2, sigma_x, sigma_y, sigma2_x, sigma2_y, offset)


#finds an initial guess for a 2d gaussian fit
def find_initial_guess(x,y,z):
    offset=np.min(z)
    z=z-offset
    A=np.max(z)
    #calculate the centroid
    centroid_x, centroid_y=np.average(x, weights=z),np.average(y, weights=z)
    cov=np.zeros((2,2))
    #calculate the covariance matrix to find the sigma_x, sigma_y and the angle
    cov[0,0]=np.average((x)**2, weights=z)-centroid_x**2
    cov[1,1]=np.average((y)**2, weights=z) - centroid_y**2
    cov[0,1]=np.average(x*y, weights=z) - centroid_x*centroid_y
    cov[1,0]=cov[0,1]
    #We diagonalize the covariance matrix
    eig=np.linalg.eigh(cov)
    sigma_x, sigma_y=np.sqrt(eig[0])
    ##The index tells us the eigenvector that has 2 values of the same sign i.e (cos, sin)
    index=0
    if eig[1][0,0]*eig[1][0,1]>0:
        index=0
    else:
        index=1
    #We take the arctan of the ratio of the compenents of the eigenvector (cos, sin) to get the angle
    theta=np.rad2deg(np.arctan(eig[1][index, 1]/eig[1][index,0]))
    return (A,centroid_x,centroid_y,sigma_x, sigma_y, offset, theta)

def fit_gaussian_2D(x,y,z,bin=1, angle=None):
    #Get initial guess
    x_min, x_max=np.min(x), np.max(x)
    y_min, y_max=np.min(y), np.max(y)
    if not bin==1:
        x=rebin(x, bin)
        y=rebin(y, bin)
        z=rebin(z,bin) 
    #We clean the images by removing the NAN 
    cleaning=np.isfinite(z)
    x=x[cleaning]
    y=y[cleaning]
    z=z[cleaning]
    initial_guess=find_initial_guess(x,y,z)
    if angle is None:
        func_to_fit = lambda x, A,x_0,y_0, sigma_x, sigma_y, offset, theta : rot_gaussian(*x, A,x_0,y_0, sigma_x, sigma_y, offset,theta)
    else:
        func_to_fit = lambda x, A,x_0,y_0, sigma_x, sigma_y, offset : rot_gaussian(*x, A,x_0,y_0, sigma_x, sigma_y, offset, angle)
    min_z,max_z=np.min(z), np.max(z)
    try :
        if angle is None:
            popt,_ =curve_fit(func_to_fit, [x.ravel(),y.ravel()], z.ravel(), p0=initial_guess, bounds=([0,x_min,y_min,0,0,min_z,0],[2*(max_z-min_z), x_max,y_max, x_max, y_max, max_z,89.99]), maxfev=50)
            return popt
        else: 
            initial_guess=initial_guess[:-1]
            popt,_ =curve_fit(func_to_fit, [x.ravel(),y.ravel()], z.ravel(), p0=initial_guess, bounds=([0,x_min,y_min,0,0,min_z],[2*(max_z-min_z), x_max,y_max, x_max, y_max, max_z]), maxfev=50)
            return np.append(popt, angle)
    except Exception as e:
        print("Could not fit : {}".format(e))
        empty_array=np.empty(len(initial_guess))
        empty_array[:]=np.NAN
        return empty_array
    

###2D gaussian2 fit###

def fit_gaussian2_2D(x, y, z,  bin=1, angle=None, initial_guess=None):
    print("Max z {}".format(np.nanmax(z)))

    #Get initial guess
    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)
    if not bin==1:
        x=rebin(x, bin)
        y=rebin(y, bin)
        z=rebin(z, bin) 

    #We clean the images by removing the NAN 
    cleaning = np.isfinite(z)
    x = x[cleaning]
    y = y[cleaning]
    z = z[cleaning]

    if initial_guess is None:
        initial_guess=find_initial_guess(x,y,z)
    initial_guess = np.concatenate((initial_guess[:1], initial_guess[:3], np.array(initial_guess[3:5])*np.sqrt(2), np.array(initial_guess[3:5])/np.sqrt(2), initial_guess[5:]))
    print("Initial guess: {}".format(initial_guess))

    if angle is None:
        func_to_fit = lambda x, A, A2, x_0, y_0, sigma_x, sigma_y, sigma2_x, sigma2_y, offset, theta : rot_gaussian2(*x, A, A2, x_0, y_0, sigma_x, sigma_y, sigma2_x, sigma2_y, offset,theta)
    else:
        func_to_fit = lambda x, A, A2, x_0, y_0, sigma_x, sigma_y, sigma2_x, sigma2_y, offset : rot_gaussian2(*x, A, A2, x_0, y_0, sigma_x, sigma_y, sigma2_x, sigma2_y, offset, angle)
    min_z, max_z = np.min(z), np.max(z)

    try :
        if angle is None:
            popt, _ = curve_fit(func_to_fit, [x.ravel(), y.ravel()], z.ravel(), p0=initial_guess, bounds=([0, 0, x_min, y_min, 0, 0, 0, 0, min_z, 0], [2*(max_z-min_z), 2*(max_z-min_z), x_max, y_max, x_max, y_max, x_max, y_max, max_z, 89.99]), maxfev=200)
            return popt
        else: 
            popt, _ = curve_fit(func_to_fit, [x.ravel(), y.ravel()], z.ravel(), p0=initial_guess[:-1], bounds=([0, 0, x_min, y_min, 0, 0, 0, 0, min_z], [2*(max_z-min_z), 2*(max_z-min_z), x_max, y_max, x_max, y_max, x_max, y_max, max_z]), maxfev=200)
            return np.append(popt, angle)

    except Exception as e:
        print("Could not fit : {}".format(e))
        empty_array = np.empty(len(initial_guess))
        empty_array[:] = np.NAN
        return empty_array



def calculate_atom_number_fit(A, sigma_x, sigma_y, pixel_size):
    return A*2*np.pi*sigma_x*sigma_y*pixel_size**2/Dy.sigma0

def rotation_image(l):
    n,m = l.shape
    res = []
    for i in range(1,1+m):
        a = []
        for j in range(n):
            a.append(l[j][-i])
        res.append(a)
    return np.array(res)

    