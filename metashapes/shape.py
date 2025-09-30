# metashapes/shape.py

# This module defines the Shape class, which wraps shapely geometries and provides
# methods for conversion to/from various formats, as well as delegation of shapely methods.

from shapely.geometry.base import BaseGeometry

import numpy as np
import gdstk
import pya

from typing import TYPE_CHECKING, Any, Mapping, Iterable, List
if TYPE_CHECKING:
    from .canvas import Canvas  # type-only

class Shape:
    """
    A class representing a geometric shape.
    """
    def __init__(self, geom: BaseGeometry, *, min_width: float = None, min_gap: float = None) -> None:
        if not isinstance(geom, BaseGeometry):
            raise TypeError("geom must be an instance of shapely.geometry.base.BaseGeometry")
        if geom.is_empty:
            raise ValueError("geom cannot be empty")
        
        self._geom = geom.simplify(0.0)  # Ensure valid geometry
        self._min_width = min_width
        self._min_gap = min_gap

    # --- Properties ---
    @property
    def geom(self) -> BaseGeometry:
        """
        Get the geometry of the shape.
        Returns:
            A shapely BaseGeometry object.
        """
        return self._geom
    
    @geom.setter
    def geom(self, value: BaseGeometry):
        """
        Set the geometry of the shape.
        Parameters:
            value: A shapely BaseGeometry object.
        """
        if not isinstance(value, BaseGeometry):
            raise TypeError("geom must be an instance of shapely.geometry.base.BaseGeometry")
        if value.is_empty:
            raise ValueError("geom cannot be empty")
        self._geom = value.simplify(0.0)  # Ensure valid geometry
    
    @property
    def min_width(self) -> float:
        """
        Get the minimum feature size for fabrication.
        Returns:
            The minimum width as a float, or None if not set.
        """
        return self._min_width
    
    @min_width.setter
    def min_width(self, value: float):
        """
        Set the minimum feature size for fabrication.
        Parameters:
            value: The minimum width as a float. Must be positive or None to unset.
        """
        if value is not None and value <= 0:
            raise ValueError("min_width must be positive or None.")
        self._min_width = float(value)

    @property
    def min_gap(self) -> float:
        """
        Get the minimum gap size for fabrication.
        Returns:
            The minimum gap as a float, or None if not set.
        """
        return self._min_gap
    
    @min_gap.setter
    def min_gap(self, value: float):
        """
        Set the minimum gap size for fabrication.
        Parameters:
            value: The minimum gap as a float. Must be positive or None to unset.
        """
        if value is not None and value <= 0:
            raise ValueError("min_gap must be positive or None.")
        self._min_gap = float(value)
    
    # Numpy
    def to_numpy(self, canvas: 'Canvas') -> np.ndarray:
        """
        Rasterize the shape onto a numpy array based on the provided canvas.
        Parameters:
            canvas: Canvas object defining the spatial mapping.
        Returns:
            A binary numpy array where True/1 indicates the shape.
        """
        from .transform import shapely_to_numpy  
        return shapely_to_numpy(self.geom, canvas)

    @staticmethod
    def from_numpy(img: np.ndarray, 
                   canvas: 'Canvas',
                   *,
                   simp_coeff: float = 0.5,
                   sfd: bool = False,
                   gaussian: bool = True,
                   gauss_sigma: float = 0.6,
                   verbose: bool = False) -> 'Shape':
        """
        Create a shape from a binary numpy array.
        Larger image resolution yield more accurate results.
        Parameters:
            img: 2D binary numpy array where True/1 indicates the shape.
            canvas: Canvas object defining the spatial mapping.
            simp_coeff: Simplification coefficient (scales with pixel size). Reduce number of vertices.
            sfd: If True, apply signed distance function before contouring.
            gaussian: If True, apply Gaussian smoothing before contouring.
            gauss_sigma: Standard deviation for Gaussian kernel if gaussian is True.
            verbose: If True, print image reconstruction error.
        Returns:
            A new Shape object.
        """
        from .transform import numpy_to_shapely  
        return Shape(numpy_to_shapely(img, 
                                      canvas, 
                                      simp_coeff=simp_coeff, 
                                      sfd=sfd, 
                                      gaussian=gaussian, 
                                      gauss_sigma=gauss_sigma,
                                      verbose=verbose))
    
    # gdstk
    def to_gdstk(self) -> List[gdstk.Polygon]:
        """
        Convert the shape to a gdstk polygon.
        Returns:
            A list of gdstk.Polygon objects.
        """
        from .transform import shapely_to_gdstk  
        return shapely_to_gdstk(self.geom)

    @staticmethod
    def from_gdstk(poly: List[gdstk.Polygon]) -> 'Shape':
        """
        Create a shape from a gdstk polygon.
        Parameters:
            poly: A gdstk.Polygon or list of gdstk.Polygon objects.
        Returns:
            A new Shape object.
        """
        from .transform import gdstk_to_shapely 
        return Shape(gdstk_to_shapely(poly))

    # KLayout
    def to_klayout(self) -> List[pya.Polygon]:
        """
        Convert the shape to a KLayout polygon.
        """
        from .transform import shapely_to_klayout  
        return shapely_to_klayout(self.geom)
    
    @staticmethod
    def from_klayout(poly) -> 'Shape':
        """
        Create a shape from a KLayout polygon.
        """
        from .transform import klayout_to_shapely  
        return Shape(klayout_to_shapely(poly))


    # Handle Shapely natively
    def __getattr__(self, name):
        """
        Delegate attribute access to the underlying shapely geometry.
        """
        target = getattr(self.geom, name)
        if not callable(target):
            return target
        
        def _method(*args, **kwargs):
            """Unwrap Shape arguments back to BaseGeometry so Shapely understands them."""
            a, kw = _unwrap(*args, **kwargs)
            return _wrap(target(*a, **kw))
        
        _method.__name__ = name
        _method.__doc__ = getattr(target, '__doc__', None)

        return _method


# --- Helpers ---
def _wrap(result: Any) -> Any:
    """
    Automatically wrap shapely geometries in Shape.
    """
    
    if isinstance(result, BaseGeometry):
        return Shape(result)
    
    # tuple/list -> preserve tuple/list
    if isinstance(result, (list, tuple)):
        wrapped = [_wrap(item) for item in result]
        return tuple(wrapped) if isinstance(result, tuple) else wrapped
    
    # mappings -> preserve mappings
    if isinstance(result, Mapping):
        return type(result)((k, _wrap(v)) for k, v in result.items())
    
    # iterables -> wrap lazily
    if isinstance(result, Iterable) and not isinstance(result, (str, bytes, bytearray)):
        return (_wrap(item) for item in result)
    
    return result

def _unwrap(*args, **kwargs):
    """
    Unwrap Shape arguments back to BaseGeometry so Shapely understands them.
    """
    unwrapped_args = [a.geom if isinstance(a, Shape) else a for a in args]
    unwrapped_kwargs = {k: v.geom if isinstance(v, Shape) else v for k, v in kwargs.items()}
    return unwrapped_args, unwrapped_kwargs

