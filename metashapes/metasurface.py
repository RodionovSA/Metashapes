# metashapes/metasurface.py

# This module provides a Metasurface class

import numpy as np
from uuid import uuid4
import gdstk
import pya
from typing import List, Dict, Tuple, Optional
from .shape import Shape
from .canvas import Canvas
from .utils import shp

class Metasurface:
    """
    A class representing a metasurface layer, homogeneous in the z-direction.
    It consists of multiple shapes (elements) arranged on a defined canvas in x-y plane.
    """
    def __init__(self, 
                 shapes: 'Shape', 
                 canvas: 'Canvas',
                 thickness: float,
                 *,
                 inverted:bool = False,
                 id: Optional[str] = None) -> None:
        """
        Initialize the Metasurface.

        Parameters:
            shapes: A Shape that define the metasurface pattern.
            canvas: Canvas instance that defines the spatial mapping for the metasurface.
            thickness: Thickness of the metasurface layer in the z-direction (same units as canvas)
            inverted: If True, the shapes define voids in a material background; if False, they define material inclusions in a void background.

        """
        
        # Validate inputs
        if not isinstance(shapes, Shape):
            raise TypeError("shapes must be an instance of Shape.")
        if not isinstance(canvas, Canvas):
            raise TypeError("canvas must be an instance of Canvas.")
        if not isinstance(inverted, bool):
            raise TypeError("inverted must be a boolean value.")
            
        self._shapes = shapes
        self._canvas = canvas
        self.inverted = bool(inverted)
        self.thickness = float(thickness)

        self.id: str = id or f"{uuid4().hex[:10]}"
        
        # Min width and gap
        self._min_width = shapes.min_width
        self._min_gap = shapes.min_gap
        
        if inverted:
            self._min_width, self._min_gap = self._min_gap, self._min_width

    # Main objects
    @property
    def shapes(self) -> 'Shape':
        """
        Get the shape in the metasurface.
        Returns:
            A Shape object.
        """
        return self._shapes
    
    @property
    def canvas(self) -> 'Canvas':
        """
        Get the canvas of the metasurface.
        Returns:
            A Canvas object.
        """
        return self._canvas
    
    @property
    def unit_cell(self) -> 'Shape':
        """
        Get the unit cell of the metasurface.
        Returns:
            A Shape object representing the unit cell.
        """
        unit_cell_base = self.canvas.unit_cell
        shapes = self.shapes
        
        if self.inverted:
            return unit_cell_base.difference(shapes)
        else:
            return unit_cell_base.intersection(shapes)
    
    # Properties for easy access to canvas attributes
    @property
    def spacing(self) -> float:
        """
        Get the spacing of the canvas.
        Returns:
            The spacing value from the canvas.
        """
        return self.canvas.spacing
    
    @spacing.setter
    def spacing(self, value: float) -> None:
        """
        Set the spacing of the canvas.
        Parameters:
            value: New spacing value to set.
        """
        self._canvas.spacing = float(value)
        
    @property
    def L(self) -> Tuple[float, float]:
        """
        Get the physical size of the unit cell.
        Returns:
            The (Lx, Ly) values from the canvas.
        """
        return (self.canvas.Lx, self.canvas.Ly)
    
    @L.setter
    def L(self, value: Tuple[float, float]) -> None:
        """
        Set the physical size of the unit cell.
        Parameters:
            value: New (Lx, Ly) values to set.
        """
        self._canvas.Lx = float(value[0])
        self._canvas.Ly = float(value[1])

    @property
    def pixel_size(self) -> Tuple[float, float]:
        """
        Get the pixel size of the canvas.
        Returns:
            The (dx, dy) values from the canvas.
        """
        return (self.canvas.dx, self.canvas.dy)
    
    @pixel_size.setter
    def pixel_size(self, value: Tuple[float, float]) -> None:
        """
        Set the pixel size of the canvas.
        Parameters:
            value: New (dx, dy) values to set.
        """
        self._canvas.set_pixel_size(float(value[0]), rounding="round")
        self._canvas.set_pixel_size(float(value[1]), rounding="round")
        
    @property
    def min_width(self) -> Optional[float]:
        """
        Get the minimum width among all shapes in the metasurface.
        Returns:
            The minimum width value or None if not defined.
        """
        return self._min_width
        
    @property
    def min_gap(self) -> Optional[float]:
        """
        Get the minimum gap among all shapes in the metasurface.
        Returns:
            The minimum gap value or None if not defined.
        """
        return self._min_gap
        
    def copy(self, id: str = None) -> 'Metasurface':
        """
        Create a copy of the metasurface.
        Returns:
            A new Metasurface object that is a copy of the current one.
        """
        return Metasurface(
            shapes=self.shapes,
            canvas=self.canvas,
            thickness=self.thickness,
            inverted=self.inverted,
            id=id or f"{uuid4().hex[:10]}"
        )
        
    def to_numpy(self) -> np.ndarray:
        """
        Rasterize the unit cell of the metasurface to a 2D numpy array.
        Returns:
            A 2D numpy array representing the rasterized unit cell.
        """
        return self.unit_cell.to_numpy(self.canvas)
    
    def to_gdstk(self) -> List[gdstk.Polygon]:
        """
        Convert the unit cell of the metasurface to gdstk polygons.
        Returns:
            A list of gdstk.Polygon objects representing the unit cell.
        """
        return self.unit_cell.to_gdstk()
    
    def to_klayout(self) -> List[pya.Polygon]:
        """
        Convert the unit cell of the metasurface to Klayout polygons.
        Returns:
            A list of pya.Polygon objects representing the unit cell.
        """
        return self.unit_cell.to_klayout()
        
    def to_parametric(self) -> Dict:
        """
        Serialize the metasurface to a parametric dictionary.
        Returns:
            A dictionary containing the parameters of the metasurface.
        """
        return {
            "shapes": shp.to_wkt(self.shapes),
            "canvas": self.canvas.to_parametric(),
            "thickness": self.thickness,
            "inverted": self.inverted,
            "id": self.id
        }
    
    @staticmethod
    def from_parametric(param: Dict) -> 'Metasurface':
        """
        Create a Metasurface instance from a parametric dictionary.
        Parameters:
            param: A dictionary containing the parameters of the metasurface.
        """
        shapes = shp.from_wkt(param.get("shapes", ))
        canvas = Canvas.from_parametric(param.get("canvas", {}))
        thickness = param.get("thickness", 0.0)
        inverted = param.get("inverted", False)
        id = param.get("id", None)

        return Metasurface(
            shapes=shapes,
            canvas=canvas,
            thickness=thickness,
            inverted=inverted,
            id=id
        )