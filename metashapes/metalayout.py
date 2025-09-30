# metashapes/metalayout.py

# Module for fabrication layout control

import pya
import gdstk
import numpy as np
from typing import Tuple, List, Dict
import math
import warnings

from .metasurface import Metasurface

MODE_ = ['klayout', 'gdstk']

class Metalayout:
    """
    Class for the fabrication layout control.
    """
    def __init__(self, 
                 num_meta: Tuple[int, int],
                 meta_size: Tuple[float, float],
                 spacing: Tuple[float, float] = (0.0, 0.0),
                 *,
                 mode: str = 'gdstk',
                 unit: float = 1e-9,
                 resolution: float = 1e-10) -> None:
        """
        Initialize the Metalayout object.
        Parameters:
            num_meta: Number of metasurfaces in (ny, nx) directions.
            meta_size: Size of each metasurface in (Lx, Ly).
            spacing: Spacing between metasurfaces in (sx, sy).
            mode: Layout mode, either 'gdstk' or 'klayout'.
            unit: Layout unit in meters (default is 1e-9 for nm).
            resolution: Layout resolution in meters (default is 1e-10 for 0.1 nm).
        """
        # Initialize layout
        if mode == 'klayout':
            
            warnings.warn("KLayout mode does not properly render smoothed corners, which may affect geometry accuracy. "
                         "Consider using gdstk mode for designs with curved elements, or avoid smoothed corners in KLayout.",
                         UserWarning, stacklevel=1)

            self._layout = pya.Layout()
            self._layout.dbu = float(resolution)/1e-6
            self._scale = float(unit) / float(resolution)  # scale factor to convert to layout units
        elif mode == 'gdstk':
            self._layout = gdstk.Library(unit=float(unit), precision=float(resolution))
            self._scale = 1.0  # scale factor to convert to layout units
        else:
            raise ValueError('Mode must be either klayout or gdstk.')
        self._mode = mode
        
        # Add top cell
        self.create_cell('TOP')
        
        # Add default layer
        self._layers = []
        self.create_layer(1, 0)
        
        # Parameters
        if len(num_meta) != 2 or len(meta_size) != 2 or len(spacing) != 2:
            raise ValueError('num_meta, meta_size, and spacing must be tuples of length 2.')
        if any(n <= 0 for n in num_meta) or any(s < 0 for s in spacing) or any(m <= 0 for m in meta_size):
            raise ValueError('num_meta and meta_size must be positive, spacing must be non-negative.')
        
        self._num_meta = (int(num_meta[0]), int(num_meta[1]))
        self._meta_size = (self._scale*float(meta_size[0]), 
                           self._scale*float(meta_size[1]))
        self._spacing = (self._scale*float(spacing[0]), 
                         self._scale*float(spacing[1]))

        # Create array of metasurfaces
        self._metasurface_arr = np.empty(self._num_meta, dtype=object)
        
        # Create array of metasurfaces coordinates
        x_coords = np.linspace(0, (self._meta_size[0] + self._spacing[0]) * (self._num_meta[0] - 1), self._num_meta[0])
        y_coords = np.linspace(0, (self._meta_size[1] + self._spacing[1]) * (self._num_meta[1] - 1), self._num_meta[1])
        # Create a 2D array of coordinates where each element is [x, y]
        self._metasurface_coords = np.zeros((self._num_meta[0], self._num_meta[1], 2))
        for i in range(self._num_meta[0]):
            for j in range(self._num_meta[1]):
                self._metasurface_coords[i, j] = [y_coords[j], x_coords[i]]
         
    # --- Properties ---
    @property
    def mode(self):
        """
        Get the current mode of the layout.
        """
        return self._mode
    
    @property
    def layout(self):
        """
        Get the layout object.
        """
        return self._layout
    
    @property
    def cells(self):
        """
        Get the cell objects.
        """
        if self.mode == 'klayout':
            return {cell.name: cell for cell in self.layout.each_cell()}
        elif self.mode == 'gdstk':
            return {cell.name: cell for cell in self.layout.cells}
    
    @property
    def layers(self):
        """
        Get the layer objects.
        """
        return self._layers
    
    @property
    def num_meta(self) -> Tuple[int, int]:
        """
        Get the number of metasurfaces in (nx, ny) directions.
        """
        return self._num_meta
    
    @property
    def meta_size(self) -> Tuple[float, float]:
        """
        Get the size of each metasurface in (Lx, Ly).
        """
        return (self._meta_size[0]/self._scale, 
                self._meta_size[1]/self._scale)
    
    @property
    def spacing(self) -> Tuple[float, float]:
        """
        Get the spacing between metasurfaces in (sx, sy).
        """
        return (self._spacing[0]/self._scale, 
                self._spacing[1]/self._scale)
    
    @property
    def metasurface_arr(self) -> np.ndarray:
        """
        Get the array of metasurfaces (nx, ny).
        """
        return self._metasurface_arr
    
    @property
    def metasurface_coords(self) -> np.ndarray:
        """
        Get the array of metasurface coordinates (nx, ny, 2).
        """
        return self._metasurface_coords
    
    # --- Main methods ---
    def fill_with_meta(self, 
                        metasurfaces: List['Metasurface'],
                        top_cell_name: str = 'TOP',
                        layer_idx: int = 0):
        """
        Fill the layout grid with the provided metasurfaces. It finds available positions
        in the grid and places the metasurfaces in a row-major order.
        Parameters:
            metasurfaces: List of Metasurface objects to fill the grid.
            top_cell_name: Name of the top cell to add the metasurfaces to.
            layer_idx: Index of the layer to add the metasurfaces to.
        """
        # Validate inputs
        if not isinstance(metasurfaces, list) or not all(isinstance(m, Metasurface) for m in metasurfaces):
            raise ValueError('metasurfaces must be a list of Metasurface objects.')
        
        #Find available grid positions
        available_positions = [(i, j) for i in range(self.num_meta[0]) for j in range(self.num_meta[1]) 
                               if self.metasurface_arr[i, j] is None]
        if len(available_positions) == 0:
            raise ValueError('No available positions in the grid.')
        if len (metasurfaces) > len(available_positions):
            raise ValueError('Not enough available positions in the grid to fit all metasurfaces.')
        
        for idx, pos in enumerate(available_positions[:len(metasurfaces)]):
            meta = metasurfaces[idx]
            self.add_metasurface(meta, pos, top_cell_name, layer_idx)
                
    def heal(self):
        """
        Heal the layout by merging overlapping polygons and removing small features.
        """
        if self.mode == 'klayout':
            for cell in self.layout.each_cell():
                for layer in self.layers:
                    shapes = cell.shapes(layer)
                    if shapes.is_empty():
                        continue
                    region = pya.Region(shapes)
                    region = region.merge()
                    # Clean up small features by doing a small expansion and contraction
                    region = region.size(1).size(-1)
                    shapes.clear()
                    shapes.insert(region)
        elif self.mode == 'gdstk':
            for cell in self.layout.cells:
                for layer in self.layers:
                    layer_polys = [poly for poly in cell.polygons if (poly.layer, poly.datatype) == layer]
                    if not layer_polys:
                        continue
                    
                    # Perform boolean union operation
                    union_polys = gdstk.boolean(layer_polys, [], 'or')
                    
                    # Ensure new polygons have the same layer and datatype
                    for poly in union_polys:
                        poly.layer = layer[0]
                        poly.datatype = layer[1]
                    
                    # Remove original polygons and add merged ones
                    cell.remove(*layer_polys)
                    cell.add(*union_polys)
                    
    def center_layout(self):
        """
        Center everything so that the overall bounding-box center is at (0, 0).
        """
        if self.mode == "gdstk":
            # Get bbox over all top-level cells
            tops = getattr(self.layout, "top_level", lambda: self.layout.cells)()
            xmin = ymin = float("inf")
            xmax = ymax = float("-inf")

            for cell in tops:
                bb = cell.bounding_box()  # np.array([[x0,y0],[x1,y1]]) or None
                if bb is None:
                    continue
                (x0, y0), (x1, y1) = bb
                xmin = min(xmin, x0); ymin = min(ymin, y0)
                xmax = max(xmax, x1); ymax = max(ymax, y1)

            if not (xmin < xmax and ymin < ymax):
                return

            dx = -0.5 * (xmin + xmax)
            dy = -0.5 * (ymin + ymax)

            for cell in tops:
                # Shift direct geometry in the top cell
                for poly in getattr(cell, "polygons", []):
                    poly.translate(dx, dy)
                for fp in getattr(cell, "flexpaths", []):
                    fp.translate(dx, dy)
                for rp in getattr(cell, "robustpaths", []):
                    rp.translate(dx, dy)
                for lbl in getattr(cell, "labels", []):
                    ox, oy = lbl.origin
                    lbl.origin = (ox + dx, oy + dy)
                # Shift placements of child cells
                for ref in getattr(cell, "references", []):
                    ox, oy = ref.origin
                    ref.origin = (ox + dx, oy + dy)


        elif self.mode == "klayout":
            # Get the top cell
            top: pya.Cell = self.layout.top_cell()
            if top is None:
                return

            # Build recursive region across all layers to include child instances
            reg = pya.Region()
            for li in self.layout.layer_indexes():
                reg |= pya.Region(top.begin_shapes_rec(li))

            bbox: pya.Box = reg.bbox()
            def _empty_box(b: "pya.Box") -> bool:
                # Works regardless of API differences
                try:
                    return b.width() == 0 and b.height() == 0
                except Exception:
                    return not (b.left < b.right and b.bottom < b.top)

            if _empty_box(bbox):
                return

            # Center in DBU (integers)
            cx = (bbox.left + bbox.right) // 2
            cy = (bbox.bottom + bbox.top) // 2
            t = pya.Trans(-cx, -cy)

            # Move all shapes on all layers in the top cell
            for li in self.layout.layer_indexes():
                top.shapes(li).transform(t)

            # Move instances placed in the top cell
            for inst in top.each_inst():
                inst.transform(t)

    # --- Add/delete metasurface ---
    def add_metasurface(self,
                        meta: 'Metasurface',
                        position: Tuple[int, int],
                        top_cell_name: str = 'TOP',
                        layer_idx: int = 0):
        """
        Add a metasurface to the layout at the specified position.
        Parameters:
            meta: Metasurface object to add.
            position: Position in the array (ix, iy).
            top_cell_name: Name of the top cell to add the metasurface to.
            layer_idx: Index of the layer to add the metasurface to.
        """
        # Validate inputs
        if not (0 <= position[0] < self.num_meta[0]) or not (0 <= position[1] < self.num_meta[1]):
                raise ValueError('Position out of bounds.')

        # Check occupation
        if self.metasurface_arr[position[0], position[1]] is not None:
            raise ValueError('Position is already occupied.')
        
        # Check id uniqueness
        if any(m is not None and m.id == meta.id for m in self.metasurface_arr.flatten()):
            raise ValueError('A metasurface with the same ID already exists in the layout.')
        
        # Get number of periods
        Lx = meta.L[0]
        Ly = meta.L[1]
        num_periods = (int(math.floor(self.meta_size[0] / Lx)), 
                       int(math.floor(self.meta_size[1] / Ly)))
        if num_periods[0] == 0 or num_periods[1] == 0:
            raise ValueError('Metasurface is too large to fit in the specified meta_size.')
        
        # Metasurface center shift
        meta_size_center = (0.5 * (self.meta_size[0] + self.spacing[0]), 
                            0.5 * (self.meta_size[1] + self.spacing[1]))
        meta_center = (0.5 * Lx * num_periods[0], 0.5 * Ly * num_periods[1])
        center_shift = np.array([meta_size_center[0] - meta_center[0],
                                  meta_size_center[1] - meta_center[1]])
        
        # Get current position
        current_pos = 1/self._scale * self.metasurface_coords[position[0], position[1]] + center_shift
        
        # Create metasurface
        self._create_metasurface_array(meta,
                                       num_periods,
                                       top_cell_name,
                                       layer_idx,
                                       position=current_pos)

        self.metasurface_arr[position[0], position[1]] = meta
        
    def remove_metasurface(self, 
                            id: str,
                            position: Tuple[int, int]):
        """
        Remove a metasurface from the layout at the specified position.
        Parameters:
            id: ID of the metasurface to remove.
            position: Position in the array (ix, iy).
           
        """
        # Validate inputs
        if not (0 <= position[0] < self.num_meta[0]) or not (0 <= position[1] < self.num_meta[1]):
                raise ValueError('Position out of bounds.')
            
        if self.metasurface_arr[position[0], position[1]] is None or self.metasurface_arr[position[0], position[1]].id != id:
            raise ValueError('No metasurface with the specified ID at the given position.')

        # Remove metasurface
        self.metasurface_arr[position[0], position[1]] = None
        self.delete_cell(f'M_{id}')
     
    # --- Write GDS ---
    def write_gds(self, filename: str):
        """
        Write the layout to a GDS file.
        Parameters:
            filename: Name of the GDS file to write to.
        """
        if self.mode == 'klayout':
            self.layout.write(str(filename))
        elif self.mode == 'gdstk':
            self.layout.write_gds(str(filename))
     
     # --- Create/delete cell/layer ---
    def create_cell(self, name: str):
        """
        Create a new cell in the layout.
        Parameters:
            name: Name of the new cell.
        Returns:
            The created cell object.
        """
        if self.mode == 'klayout':
            cell = self.layout.create_cell(str(name))
        elif self.mode == 'gdstk':
            cell = self.layout.new_cell(str(name))

        return cell
    
    def delete_cell(self, name: str):
        """
        Delete a cell from the layout.
        Parameters:
            name: Name of the cell to delete.
        """
        cell = self.cells[str(name)]
        if cell is not None:
            if self.mode == 'klayout':
                self.layout.delete_cell(cell.cell_index())
            elif self.mode == 'gdstk':
                self.layout.remove(cell)

    def create_layer(self, num: int, datatype: int = 0):
        """
        Create a new layer in the layout.
        Parameters:
            num: Layer number.
            datatype: Layer datatype (default is 0).
        Returns:
            The created layer object.
        """
        if self.mode == 'klayout':
            self.layout.layer(num, datatype)
        elif self.mode == 'gdstk':
            pass
        
        layer = (int(num), int(datatype))
        if layer not in self._layers:
            self._layers.append(layer)

    # --- Helpers ---
    def _create_metasurface_array(self, 
                                  meta: 'Metasurface',
                                  num_periods: Tuple[int, int],
                                  top_cell_name: str = 'TOP',
                                  layer_idx: int = 0,
                                  position: Tuple[float, float] = (0.0,0.0)) -> None:
        """
        Create a 2D array of metasurface shapes.
        Parameters:
            meta: Metasurface object to create the array from.
            num_periods: Number of periods in (nx, ny) directions for the metasurface.
            top_cell_name: Name of the top cell to add the array to.
            layer_idx: Index of the layer to add the metasurfaces to.
            position: Position offset for the entire array in the layout units.
            It is the bottom-left corner of the array.
        """
        # Validate inputs
        if not isinstance(meta, Metasurface):
            raise ValueError('meta must be an instance of Metasurface.')

        if not isinstance(num_periods, tuple) or len(num_periods) != 2:
            raise ValueError('num_periods must be a tuple of (nx, ny).')

        if layer_idx < 0 or layer_idx >= len(self.layers):
            raise ValueError('Invalid layer index.')

        # Get metasurface polygons
        if self.mode == 'klayout':
            meta_polys = meta.to_klayout()
        elif self.mode == 'gdstk':
            meta_polys = meta.to_gdstk()
            
        # Create cell
        cell = self.create_cell(f'M_{meta.id}')
        
        # Add metasurface polygons to the cell
        layer = self.layers[layer_idx]
        if self.mode == 'klayout':
            for poly in meta_polys:
                trans = pya.ICplxTrans(self._scale, 0, False, 0, 0)
                scaled_poly = poly.transformed(trans)
                cell.shapes(layer).insert(scaled_poly)
        elif self.mode == 'gdstk':
            for poly in meta_polys:
                poly.layer = layer[0]
                poly.datatype = layer[1]
                cell.add(poly)
        
        # Add array of metasurfaces to the top cell
        scaled_Lx = self._scale * meta.L[0]
        scaled_Ly = self._scale * meta.L[1]
        scaled_position = (self._scale * float(position[0]), 
                           self._scale * float(position[1]))
        
        if self.mode == 'klayout':
            self.cells[top_cell_name].insert(pya.CellInstArray(cell.cell_index(),
                            pya.Trans(int(round(scaled_Lx/2 + scaled_position[0])), 
                                      int(round(scaled_Ly/2 + scaled_position[1]))),
                            pya.Vector(int(round(scaled_Lx)), 0), 
                            pya.Vector(0, int(round(scaled_Ly))),
                            num_periods[0], num_periods[1]))   
        elif self.mode == 'gdstk':
            inst = gdstk.Reference(cell, 
                                   origin=(scaled_Lx/2 + scaled_position[0], 
                                           scaled_Ly/2 + scaled_position[1]), 
                                   columns=num_periods[0], 
                                   rows=num_periods[1],
                                   spacing=(scaled_Lx, scaled_Ly))
            self.cells[top_cell_name].add(inst)
        
        
