# MetaShapes
**MetaShapes** is a framework for metasurface geometry processing.
Built on top of **Shapely**, **scikit-image**, **gdstk**, and **KLayout**, it combines the strengths of both vector- and raster-based approaches. MetaShapes makes it seamless to switch between raster and vector representations, enabling smooth and accurate workflows for metasurface design.

The framework is designed to simplify metasurface generation for both simulation and fabrication, giving you full control over the geometry of metaatoms and unit cells.
A future extension (TODO) will include a random metasurface generator with user-defined constraints—ideal for generating AI training datasets or building large-scale metasurface databases. 

## Features
- Shape creation and management: build and combine complex geometries from simple primitives.
- Fabrication preview: realistic raster-to-vector workflows mimicking lithography processes.
- Smooth GDS export: high-quality exports for fabrication-ready layouts.
- Minimal Feature Size (MFS) control: enforce fabrication limits directly in geometry.
- Random metasurface generator (planned): create diverse structures under constraints for AI/data-driven applications.

## Usage 
    from metashapes.shape import Shape
    from metashapes.canvas import Canvas
    from metashapes.library import rectangle

    import matplotlib.pyplot as plt

    # Example: create a rectangle and export to GDS
    Lx = 300
    Ly = 300
    H = 300
    W = 300
    canvas = Canvas(-Lx/2, -Ly/2, Lx, Ly, H, W)  # grid definition
    rect = rectangle(center=(0, 0), size=(100, 50))

    plt.imshow(rect.to_numpy(canvas))

## Requirements
- Python 3.11+
- Numpy 1.26+
- Shapely 2.0+
- scikit-image
- gdstk 
- Klayout (Pyhton API)