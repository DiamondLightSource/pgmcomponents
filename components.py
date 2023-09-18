"""
A python class for simple ray tracing optics.

Based heavily in parts on the work of Matthew Hand's dls-optics-core package
Author: Patrick Wang
Email: patrick.wang@diamond.ac.uk

Version: 0.1
Date: 2023-09-15

"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon
from matplotlib.collections import PatchCollection
import configparser
from geometry_elements import *

class Grating(object):
    """
    A class for a simple grating

    Based on the work of Matthew Hand

    Parameters
    ----------
    line_density : float
        The line density of the grating in lines per mm
    energy : float
        The energy of the incident beam in eV
    cff : float
        The fixed focus constant of the grating
    order : int
        The diffraction order of the grating
    dimensions : array_like
        The dimensions of the grating in mm [length, width, height]
    
    Attributes
    ----------
    line_density : float
        The line density of the grating in lines per mm
    energy : float
        The energy of the incident beam in eV
    cff : float
        The fixed focus constant of the grating
    order : int
        The diffraction order of the grating
    alpha : float
        The incident angle of the beam in degrees
    beta : float    
        The diffraction angle of the beam in degrees
    dimensions : array_like
        The dimensions of the grating in mm

    """
    def __init__(self, line_density=600, energy=250, cff=2, order=1, dimensions = np.array([1,1,1])):

        self._line_density=line_density
        self._energy=energy
        self._cff=cff
        self._order=order
        self._alpha = None
        self._beta = None
        self._dimensions = dimensions
    
    def __repr__(self):
        return "Grating(line_density={}, energy={}, cff={}, order={}, dimensions={})".format(self.line_density, 
                                                                                             self.energy, 
                                                                                             self.cff, 
                                                                                             self.order, 
                                                                                             self.dimensions)
    
    def read_file(self, filename):
        """
        Read grating parameters from a file. 
        See config_pgm.ini for an example.
        A config_file may contain more than one sections, but only the
        grating section will be read.

        Parameters
        ----------
        filename : str
            The name of the file to read from
        """
        config = configparser.ConfigParser()
        config.read(filename)
        
        if len(config['grating']) != 5:
            raise ValueError("Expected exactly five parameters in grating file")

        variables = ['line_density', 'energy', 'cff', 'order', 'dimensions']
        for var in variables:
            if var not in config['grating']:
                raise ValueError("Missing parameter {} in grating file".format(var))

        for key, value in list(config['grating'].items())[0:-1]:
            exec(f"self._{key} = float({value})")
            print(key)
            print(value)
        
        
        self._dimensions = np.array([float(x) for x in config['grating']['dimensions'].split(',')])


    @property
    def line_density(self):
        return self._line_density
    
    @line_density.setter
    def line_density(self, value):
        self._line_density = value

    @property
    def energy(self):
        return self._energy
    
    @energy.setter
    def energy(self, value):
        self._energy = value
        
    @property
    def cff(self):
        return self._cff
    
    @cff.setter
    def cff(self, value):
        self._cff = value
    
    @property
    def order(self):
        return self._order
    
    @order.setter
    def order(self, value):
        self._order = value
    
    @property
    def alpha(self):   
        return self._alpha
    
    @alpha.setter
    def alpha(self, value):
        self._alpha = value

    @property
    def beta(self):
        return self._beta
    
    @beta.setter
    def beta(self, value):
        self._beta = value
    
    @property
    def dimensions(self):
        return self._dimensions
    
    @dimensions.setter
    def dimensions(self, value):
        self._dimensions = value

    def set_angles(self, alpha, beta):
        wavelength = (np.sin(np.deg2rad(alpha)) + np.sin(np.deg2rad(beta))) / (self.line_density*1000*self._order)
        
        try:
            self._energy = 12398.42 / wavelength
        except ZeroDivisionError:
            raise ValueError("Unexpected divide by zero in grating.set_angles")
        
        self._alpha = alpha
        self._beta = beta
        self._cff = self.cff
    
    @staticmethod

    def calc_beta(alpha, line_density, order, energy):
        beta = 0 

        try:
            wavelength = wavelength(energy)
            u = order*line_density*1000*wavelength - np.sin(np.deg2rad(alpha))
            beta = np.rad2deg(np.arcsin(u))

        except ZeroDivisionError:
            raise ValueError("Unexpected divide by zero in grating.calc_beta")
        
        return beta
    
    def wavelength(self):
        return 12398.42 / self.energy
    
    def compute_corners(self):
        beta_g = np.deg2rad(self._beta + 90)
        l = self._dimensions[0]
        #Bottom left back
        blbz = -()

    
    @classmethod
    def grating_from_file(cls, filename):
        """
        Create a grating from a file. 
        See config_pgm.ini for an example.
        A config_file may contain more than one sections, but only the
        grating section will be read.

        Parameters
        ----------
        filename : str
            The name of the file to read from
        """
        grating = cls()
        grating.read_file(filename)
        return grating
    

class Plane_Mirror(object):
    """
    A class for a simple plane mirror.

    Parameters
    ----------
    dimensions : array_like
        The dimensions of the mirror in mm
    position : Point3D
        The position of the mirror
    normal : Vector3D
        The normal vector of the mirror
    orientation : Vector3D
    """

    def __init__(self, voffset=20, hoffset=0, axis_voffset=0, axis_hoffset=0, dimensions = np.array([450, 70, 50]),theta=45, plane=Plane()):
        self._voffset = voffset
        self._hoffset = hoffset
        self._axis_voffset = axis_voffset
        self._axis_hoffset = axis_hoffset
        self._dimensions = dimensions

        self._plane = plane
        self._theta = theta
        _ = self.compute_corners()
    def __repr__(self):
        return """Plane_Mirror(voffset={}, 
        hoffset={}, 
        axis_voffset={}, 
        axis_hoffset={}, 
        length={}, 
        width={}, 
        height={}, 
        plane={})""".format(self.voffset,
                            self.hoffset, 
                            self.axis_voffset, 
                            self.axis_hoffset, 
                            self.length, 
                            self.width, 
                            self.height, 
                            self.plane)
    
    def read_file(self, filename):
        """
        Read mirror parameters from a file. 
        See config_pgm.ini for an example.
        A config_file may contain more than one sections, but only the
        mirror section will be read.

        Parameters
        ----------
        filename : str
            The name of the file to read from
        """
        config = configparser.ConfigParser()
        config.read(filename)
        
        if len(config['mirror']) != 8:
            raise ValueError("Expected exactly eight parameters in mirror file")

        variables = ['voffset', 'hoffset', 'axis_voffset', 'axis_hoffset', 'length', 'width', 'height', 'theta']
        for var in variables:
            if var not in config['mirror']:
                raise ValueError("Missing parameter {} in mirror file".format(var))
            
        for key, value in list(config['mirror'].items())[0:-1]:
            exec(f"self._{key} = float({value})")
            print(key)
            print(value)
        
        
        self._dimensions = np.array([float(x) for x in config['mirror']['dimensions'].split(',')])

        

    @property
    def voffset(self):
        return self._voffset

    @voffset.setter
    def voffset(self, value):
        self._voffset = value  

    @property
    def hoffset(self):
        return self._hoffset

    @hoffset.setter
    def hoffset(self, value):
        self._hoffset = value

    @property
    def axis_voffset(self):
        return self._axis_voffset

    @axis_voffset.setter
    def axis_voffset(self, value):
        self._axis_voffset = value

    @property
    def axis_hoffset(self):
        return self._axis_hoffset

    @axis_hoffset.setter
    def axis_hoffset(self, value):
        self._axis_hoffset = value

    @property
    def dimensions(self):
        return self._dimensions
    
    @dimensions.setter
    def dimensions(self, value):
        self._dimensions = value

    @property
    def plane(self):
        return self._plane

    @plane.setter
    def plane(self, value):
        self._plane = value

    def set_position(self, position):
        self._plane.position = position

    def set_normal(self, normal):
        self._plane.normal = normal

    def set_orientation(self, orientation):
        self._plane.orientation = orientation

    def set_dimensions(self, *args):
        """
        Set the dimensions of the mirror.

        Parameters
        ----------
        *args : array_like
            Either one or three arguments for the dimensions

        Raises
        ------
        ValueError
            If the number of arguments is not one or three

        """
        if len(args) == 1:
            self._dimensions = args[0]
        elif len(args) == 3:
            self._dimensions = np.array(args)
        else:
            raise ValueError("Expected either one or three arguments for dimensions")

    def set_offsets(self, voffset, hoffset, axis_voffset, axis_hoffset):
        self._voffset = voffset
        self._hoffset = hoffset
        self._axis_voffset = axis_voffset
        self._axis_hoffset = axis_hoffset

    def compute_corners(self):
        """
        Compute the corners of the mirror in the global coordinate system,
        in addition to the plane and normal of the mirror.
    

        Returns
        -------
        corners : array_like
            The corners of the mirror in the global coordinate system
        """
        theta_g = 90 - self._theta
        theta_g = np.deg2rad(theta_g)
        a = self._hoffset
        c = self._voffset
        v = self._axis_voffset
        h = self._axis_hoffset
        w = self._width
        l = self._length
        d = self._height
        #Top left front

        tlfz = -((a - c * np.tan(theta_g)) * np.cos(theta_g)) + h
        tlfy = -(c / np.cos(theta_g) + 
                 (a - c*np.tan(theta_g)) * np.sin(theta_g)) + v
        tlfx = -w/2
        tlf = Point3D(tlfx, tlfy, tlfz)

        #Bottom left front
        blfz = tlfz + d*np.sin(theta_g)
        blfy = tlfy - d*np.cos(theta_g)        
        blfx = -w/2
        blf = Point3D(blfx, blfy, blfz)

        #Top right front
        trfz = tlfz
        trfy = tlfy
        trfx = w/2
        trf = Point3D(trfx, trfy, trfz)

        #Bottom right front
        brfz = blfz
        brfy = blfy
        brfx = w/2
        brf = Point3D(brfx, brfy, brfz)

        #Top left back
        tlbz = tlfz - l*np.cos(theta_g)
        tlby = tlfy - l*np.sin(theta_g)
        tlbx = -w/2
        tlb = Point3D(tlbx, tlby, tlbz)

        #Bottom left back
        blbz = tlbz + d*np.sin(theta_g)
        blby = tlby - d*np.cos(theta_g)
        blbx = -w/2
        blb = Point3D(blbx, blby, blbz)

        #Top right back
        trbz = tlbz
        trby = tlby
        trbx = w/2
        trb = Point3D(trbx, trby, trbz)

        #Bottom right back
        brbz = blbz
        brby = blby
        brbx = w/2
        brb = Point3D(brbx, brby, brbz)

        self._plane = Plane(tlf, trf, tlb)

        self._corners = np.array([
            tlf,
            trf,
            blf,
            brf,
            tlb,
            trb,
            blb,
            brb
        ])

        return self._corners

    def draw(self, ax):
        pass

    @classmethod

    def mirror_from_file(cls, filename):
        """
        Create a mirror from a file. 
        See config_pgm.ini for an example.
        A config_file may contain more than one sections, but only the
        mirror section will be read.

        Parameters
        ----------
        filename : str
            The name of the file to read from
        """
        mirror = cls()
        mirror.read_file(filename)
        return mirror

class PGM(object):
    """
    A class for a PGM setup.

    Parameters
    ----------
    grating : Grating
        The grating of the PGM
    mirror : Mirror
        The mirror of the PGM
    mirror_voffset : float
        The vertical offset of the mirror in mm
    mirror_hoffset : float
        The horizontal offset of the mirror in mm
    mirror_axis_voffset : float
        The vertical offset of the mirror axis in mm
    mirror_axis_hoffset : float
        The horizontal offset of the mirror axis in mm
    mirror_leng
    """

    def __init__(self, grating = Grating()):
        self._grating = grating
        self._mirror_voffset = 20
        self._mirror_hoffset = 0
        self._mirror_axis_voffset = 0
        self._mirror_axis_hoffset = 0
        self._mirror_length = 450
        self._mirror_width = 70
        self._mirror_height = 50
        