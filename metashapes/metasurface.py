# metashapes/metasurface.py

# This module provides a Metasurface class

from typing import List, Dict, Tuple
from .shape import Shape
from .canvas import Canvas

class Metasurface:
    """
    A class representing a metasurface layer, homogeneous in the z-direction.
    It consists of multiple shapes (elements) arranged on a defined canvas in x-y plane.
    """
    def __init__(self, 
                 shapes: List['Shape'], 
                 canvas: 'Canvas',
                 *,
                 materials: List[str] = None) -> None:
        """
        Initialize the Metasurface.

        Parameters:
            shapes: Collection of Shape instances describing the metasurface elements.
            canvas: Canvas instance that defines the spatial mapping for the metasurface.
            materials: (**Not implemented**) List of material identifiers corresponding to each shape.

        Notes:
            If materials provided, a flag value is assigned to each material, where 0 is background.
        """
        # Normalize shapes into a list for consistent handling
        shapes = list(shapes) if shapes is not None else []
        
        # Validate inputs
        if not all(isinstance(s, Shape) for s in shapes):
            raise TypeError("All items in shapes must be instances of Shape.")
        if not isinstance(canvas, Canvas):
            raise TypeError("canvas must be an instance of Canvas.")

        #TODO: Define material mapping if materials are provided
        if materials is not None:
            raise NotImplementedError("Material handling is not implemented yet.")
        
            if len(materials) != len(shapes):
                raise ValueError("Length of materials must match length of shapes.")
            self._materials = {material: idx + 1 for idx, material in enumerate(set(materials))}
            self._materials['background'] = 0
        else:
            self._materials = None
            
        self._shapes = shapes
        self._canvas = canvas

    # Main objects
    @property
    def shapes(self) -> List['Shape']:
        """
        Get the list of shapes in the metasurface.
        Returns:
            A list of Shape objects.
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
        from .utils import unary_union
        unit_cell_base = self.canvas.unit_cell
        shapes = unary_union(self.shapes)
        return unit_cell_base.intersection(shapes)
    
    @property
    def materials(self) -> Dict[str, int] | None:
        """
        Get the list of materials corresponding to the shapes.
        Returns:
            A list of material identifiers or None if not provided.
        """
        return self._materials
    
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