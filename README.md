# MetaShapes

**MetaShapes** is a Python library for working with 2D shapes in the context of metasurface design. It provides SDF-based (signed distance function) shape primitives, boolean composition, unit cell management, constraint-based random generation, and export to Shapely, NumPy, and GDS formats.

The library is designed to support both simulation workflows and fabrication-ready layout generation.

## Features

- **SDF primitives** — analytically defined 2D shapes with exact signed distance functions, differentiable via PyTorch:
  - Quadrilaterals: `Rectangle`, `ConvexQuad`, `IsoscelesTrapezoid`
  - Conics: `Ellipse`
  - Polygons: `RegularPolygon`
  - Junctions: `Cross`, `TShape`
  - Periodic: `Stripe`
- **Boolean operations** — `Union`, `Intersection`, `Difference` for composing complex shapes
- **Transforms** — `Translate`, `Rotate`, `Scale`
- **Unit cell** — `UnitCell` and `UniformCell` for managing periodic metasurface cells with multiple shapes
- **Analysis** — `UnitCellAnalyzer` for computing geometry metrics (fill factor, gap distances, feature sizes)
- **Random generator** — constraint-based random generation of unit cells with configurable shape counts, parameter ranges, minimum gap/feature size, and sampling weights
- **Adapters** — export to Shapely geometries, NumPy raster arrays, and YAML serialization/deserialization
- **Canvas** — raster grid definition for pixel-level rendering

## Installation

```bash
pip install metashapes
```

For GDS export support:

```bash
pip install metashapes[gds]
```

## Quick Start

```python
from metashapes import Canvas, Shape, UnitCell
from metashapes.shape.primitives import Rectangle, Ellipse, Cross

# Define a unit cell canvas (size in nm)
canvas = Canvas(x0=-150, y0=-150, Lx=300, Ly=300, H=300, W=300)

# Create shapes
rect = Rectangle(center=(0, 0), size=(100, 60), angle=0.0)
ell  = Ellipse(center=(0, 0), axes=(120, 80))

# Render to NumPy array
arr = rect.to_numpy(canvas)

# Build a unit cell
cell = UnitCell(canvas=canvas, shape=rect)
```

## Random Generation

```python
from metashapes.generators import RandomUnitCellGenerator
from metashapes.generators.config import GeneratorConfig

config = GeneratorConfig(
    target_count=100,
    allowed_shapes=("Rectangle", "Ellipse", "Cross"),
    min_num_shapes=1,
    max_num_shapes=2,
    min_gap=10.0,
    min_feature_size=30.0,
    seed=42,
)

generator = RandomUnitCellGenerator(config)
batch = generator.generate(canvas)
```

## YAML Serialization

```python
from metashapes.adapters.yaml import save_unit_cells, load_unit_cells

save_unit_cells("cells.yaml", batch.cells)
cells = load_unit_cells("cells.yaml")
```

## Requirements

- Python 3.9+
- NumPy >= 1.26
- PyTorch >= 2.0
- Shapely >= 2.0
- PyYAML >= 6.0
- gdstk *(optional, for GDS export)*
- KLayout Python API *(optional)*

## License

MIT License. See [LICENSE](LICENSE) for details.
