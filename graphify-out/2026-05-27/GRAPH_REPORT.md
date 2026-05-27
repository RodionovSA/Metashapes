# Graph Report - .  (2026-05-27)

## Corpus Check
- 11 files · ~31,896 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 778 nodes · 2538 edges · 40 communities (27 shown, 13 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 470 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Shape Primitives Core|Shape Primitives Core]]
- [[_COMMUNITY_Random Generator & Lattice|Random Generator & Lattice]]
- [[_COMMUNITY_Shape Analysis & SDF Concepts|Shape Analysis & SDF Concepts]]
- [[_COMMUNITY_Unit Cell Analyzer|Unit Cell Analyzer]]
- [[_COMMUNITY_Conic Shape Primitives|Conic Shape Primitives]]
- [[_COMMUNITY_YAML Serialization Tests|YAML Serialization Tests]]
- [[_COMMUNITY_Shapely Transform Tests|Shapely Transform Tests]]
- [[_COMMUNITY_Random Generator Logic|Random Generator Logic]]
- [[_COMMUNITY_Shapely Compound Shape Tests|Shapely Compound Shape Tests]]
- [[_COMMUNITY_Generator Integration Tests|Generator Integration Tests]]
- [[_COMMUNITY_Generator Base Classes|Generator Base Classes]]
- [[_COMMUNITY_Periodic Stripe Shape|Periodic Stripe Shape]]
- [[_COMMUNITY_Shapely Adapter Modules|Shapely Adapter Modules]]
- [[_COMMUNITY_YAML & Unit Cell Serialization|YAML & Unit Cell Serialization]]
- [[_COMMUNITY_Unit Cell Tests|Unit Cell Tests]]
- [[_COMMUNITY_Shapely Adapter Layer|Shapely Adapter Layer]]
- [[_COMMUNITY_PyTorch Differentiability|PyTorch Differentiability]]
- [[_COMMUNITY_Lattice SDF Tests|Lattice SDF Tests]]
- [[_COMMUNITY_Coordinate Transform Bridge|Coordinate Transform Bridge]]
- [[_COMMUNITY_Boolean Shape Tests|Boolean Shape Tests]]
- [[_COMMUNITY_Periodic Unit Cell Ops|Periodic Unit Cell Ops]]
- [[_COMMUNITY_Mask Tests|Mask Tests]]
- [[_COMMUNITY_Generator Validation|Generator Validation]]
- [[_COMMUNITY_UnitCell Shapely Tests|UnitCell Shapely Tests]]
- [[_COMMUNITY_Boundary Tests|Boundary Tests]]
- [[_COMMUNITY_Serialization Tests|Serialization Tests]]
- [[_COMMUNITY_Lattice Basis Rationale|Lattice Basis Rationale]]
- [[_COMMUNITY_Lattice Basis Rationale B|Lattice Basis Rationale B]]
- [[_COMMUNITY_Lattice Basis Rationale C|Lattice Basis Rationale C]]
- [[_COMMUNITY_Validator Rationale|Validator Rationale]]
- [[_COMMUNITY_Generator Base Rationale|Generator Base Rationale]]
- [[_COMMUNITY_Analysis Test Suite|Analysis Test Suite]]
- [[_COMMUNITY_Primitives Init|Primitives Init]]
- [[_COMMUNITY_Sampler Utils|Sampler Utils]]

## God Nodes (most connected - your core abstractions)
1. `UnitCell` - 82 edges
2. `Rectangle` - 81 edges
3. `Lattice` - 80 edges
4. `shape_to_shapely()` - 77 edges
5. `UnitCellAnalyzer` - 65 edges
6. `Shape` - 64 edges
7. `Stripe` - 57 edges
8. `Ellipse` - 54 edges
9. `RegularPolygon` - 52 edges
10. `Union` - 50 edges

## Surprising Connections (you probably didn't know these)
- `SDF-based differentiable shapes concept` --conceptually_related_to--> `Ellipse`  [INFERRED]
  README.md → metashapes/shape/primitives/conics.py
- `sdf_at()` --references--> `SDF Convention: Negative Inside, Positive Outside`  [INFERRED]
  tests/shape/conftest.py → metashapes/shape/base.py
- `TestLeafShapes` --uses--> `Lattice`  [INFERRED]
  tests/test_analysis.py → metashapes/lattice/basis.py
- `TestLeafShapes` --uses--> `UnitCell`  [INFERRED]
  tests/test_analysis.py → metashapes/lattice/unit_cell.py
- `TestLeafShapes` --uses--> `Rectangle`  [INFERRED]
  tests/test_analysis.py → metashapes/shape/primitives/quads.py

## Communities (40 total, 13 thin omitted)

### Community 0 - "Shape Primitives Core"
Cohesion: 0.06
Nodes (28): Cross, Symbolic T-shape.      Parameters:         center: (cx, cy)         length: full, Symbolic symmetric cross.      Parameters:         center: (cx, cy)         leng, TShape, min_feature_size(), General triangle defined by two base angles and the base length (ASA).      Para, Symbolic regular polygon.      Parameters:         center: (cx, cy)         n: N, (A, B, C) as (x, y) tensor pairs, CCW, centroid at origin. (+20 more)

### Community 1 - "Random Generator & Lattice"
Cohesion: 0.06
Nodes (45): Constraint-Based Unit Cell Generation, RandomUnitCellGenerator._sample_shape, register_shape_sampler(), SHAPE_SAMPLER_REGISTRY, Lattice, Cartesian translation for lattice cell (i, j)., In-plane periodicity of the unit cell. Fixed (non-optimizable).     Defined by t, Cartesian (x, y) -> fractional (f1, f2). (+37 more)

### Community 2 - "Shape Analysis & SDF Concepts"
Cohesion: 0.06
Nodes (44): CellMetrics, _compute_min_gap, Rotation Guard for Infinite-Extent Shapes, Parametric Serialization (to_parametric / from_parametric), SDF Convention: Negative Inside, Positive Outside, Smooth Boolean Operations via Polynomial Blending, _bbox_size(), Compute all metrics for a single cell. (+36 more)

### Community 3 - "Unit Cell Analyzer"
Cohesion: 0.09
Nodes (14): _leaf_shapes, UnitCellAnalyzer, UnitCellAnalyzer.validate, Return a list of constraint violation descriptions.         An empty list means, Generator-compatible interface.          Returns the first constraint violation, Find groups of cells that have identical SDFs (within tolerance).          Each, Yield leaf (primitive) shapes from a composed shape tree.      Union nodes are d, Computes metrics for :class:`~metashapes.unit_cell.UnitCell` objects and     val (+6 more)

### Community 4 - "Conic Shape Primitives"
Cohesion: 0.11
Nodes (15): Egg, Ellipse, Ellipse.min_feature_size, Egg shape: two half-ellipses joined at the x-axis.      Parameters:         cent, Symbolic ellipse.      Parameters:         center: (cx, cy)         axes: full s, Stadium (discorectangle/capsule): a rectangle with semicircular caps.      Param, Stadium, Inverse Design for Metasurfaces (+7 more)

### Community 5 - "YAML Serialization Tests"
Cohesion: 0.12
Nodes (21): _make_batch_result(), _rect_cell(), _sdf_grid(), TestSaveBatchResult, TestSaveLoadUnitCells, _check_version(), load_batch_result(), _load_cell() (+13 more)

### Community 6 - "Shapely Transform Tests"
Cohesion: 0.14
Nodes (11): TestTransformsToShapely, ConvexQuad, IsoscelesTrapezoid, Symbolic rectangle.      Parameters:         center: (cx, cy)         size: (wid, Symbolic isosceles trapezoid.      Parameters:         center: (cx, cy), Symbolic convex quadrilateral with optional rounded corners.      The quad is bu, Rectangle, TestConvexQuad (+3 more)

### Community 7 - "Random Generator Logic"
Cohesion: 0.12
Nodes (11): RandomUnitCellGenerator._generate_one, _has_infinite_bounds(), RandomGeneratorConfig, Return True if the shape has infinite spatial extent (e.g. Stripe)., First concrete generator config.      For now it only adds one flag:     - requi, Random unit-cell generator.      Current responsibilities:     1. choose number, _AlwaysFailValidator, TestLatticeVariants (+3 more)

### Community 8 - "Shapely Compound Shape Tests"
Cohesion: 0.12
Nodes (5): _centroid(), TestCompoundShapesToShapely, TestPrimitivesToShapely, Shapely Adapter Pattern, shape_to_shapely()

### Community 9 - "Generator Integration Tests"
Cohesion: 0.12
Nodes (8): _gen(), test_each_shape_type_generates(), TestBasicGeneration, TestConstraints, TestReport, TestShapeCount, TestShapeTypes, Test Random Generator

### Community 10 - "Generator Base Classes"
Cohesion: 0.18
Nodes (12): ABC, _generate_one(), Build metadata dict attached to every GenerationReport., Base API for periodic unit-cell generators.      Generation pipeline for each ca, Return a (possibly rescaled) lattice for a single cell.          Uniform scaling, UnitCellGenerator, GeneratorConfig, GenerationBatchResult (+4 more)

### Community 11 - "Periodic Stripe Shape"
Cohesion: 0.16
Nodes (3): An infinite stripe spanning the full unit cell along one axis.      The stripe i, Stripe, TestStripe

### Community 12 - "Shapely Adapter Modules"
Cohesion: 0.17
Nodes (14): difference_to_shapely(), intersection_to_shapely(), union_to_shapely(), egg_to_shapely(), ellipse_to_shapely(), stadium_to_shapely(), cross_to_shapely(), _rounded_box() (+6 more)

### Community 13 - "YAML & Unit Cell Serialization"
Cohesion: 0.14
Nodes (10): _Dumper, YAML Dumper that puts 'type' first, then sorts remaining keys., Rasterize the periodic structure into a mask. Shape [ny·n2, nx·n1].          sof, Return world-coordinate points on the material boundary (zero-level-set)., A periodic structure: one Lattice + one Shape (the scene).      The lattice owns, Axis-aligned Cartesian bounding box of the supercell.          Returns ``(xmin,, Number of periodic copies to search per lattice direction.          A finite sha, Periodic signed distance of the scene at Cartesian (x, y).          Minimum over (+2 more)

### Community 14 - "Unit Cell Tests"
Cohesion: 0.21
Nodes (4): Rectangular unit cell with a small square at the origin., _square_cell(), TestExtent, TestUnitCellRasterize

### Community 15 - "Shapely Adapter Layer"
Cohesion: 0.21
Nodes (9): round_corners(), Shapely Adapter __init__, regular_polygon_to_shapely(), star_to_shapely(), triangle_to_shapely(), convex_quad_to_shapely(), rectangle_to_shapely(), Rasterize a Shapely geometry onto a coordinate grid.      Parameters     ------- (+1 more)

### Community 16 - "PyTorch Differentiability"
Cohesion: 0.22
Nodes (7): nn.Module Subclassing for Differentiability, make_learnable_polygon(), Return (UnitCell, side_length param, center param) with nn.Parameters., Gradient flows from a point displaced by one lattice vector., At least some pixels must have non-trivial gradient contribution., TestUnitCellGradients, TestUnitCellGradients Test Class

### Community 17 - "Lattice SDF Tests"
Cohesion: 0.20
Nodes (3): square_in_rect(), _sdf_at(), TestUnitCellSDF

### Community 18 - "Coordinate Transform Bridge"
Cohesion: 0.18
Nodes (10): SDF to Shapely Geometry Bridge, Convert a shapely geometry to a gdstk polygon or a list of polygons., Convert a gdstk polygon to a shapely geometry., Convert a shapely geometry to a KLayout polygon or a list of polygons., Create a shapely geometry from a binary numpy array.     Parameters:         img, gdstk_to_shapely, numpy_to_shapely, shapely_to_gdstk (+2 more)

### Community 20 - "Periodic Unit Cell Ops"
Cohesion: 0.29
Nodes (8): UnitCellAnalyzer.find_duplicates, Periodic SDF via Lattice Copies, UnitCell.boundary_points, UnitCell.extent, UnitCell.mask, UnitCell.rasterize, UnitCell._ring_for, UnitCell.sdf

### Community 22 - "Generator Validation"
Cohesion: 0.40
Nodes (4): Summarise key parameter ranges across generated cells., DefaultUnitCellValidator, validate(), UnitCell.to_shapely

## Knowledge Gaps
- **13 isolated node(s):** `TestAnalyze Test Class`, `TestUnitCellGradients Test Class`, `UnitCell.boundary_points`, `UnitCell._ring_for`, `UnitCellAnalyzer.find_duplicates` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lattice` connect `Random Generator & Lattice` to `Shape Analysis & SDF Concepts`, `Unit Cell Analyzer`, `YAML Serialization Tests`, `Shapely Transform Tests`, `Random Generator Logic`, `Generator Integration Tests`, `Generator Base Classes`, `YAML & Unit Cell Serialization`, `Unit Cell Tests`, `PyTorch Differentiability`, `Lattice SDF Tests`, `Mask Tests`, `UnitCell Shapely Tests`, `Boundary Tests`, `Serialization Tests`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Why does `Shape` connect `Shape Analysis & SDF Concepts` to `Shape Primitives Core`, `Random Generator & Lattice`, `Unit Cell Analyzer`, `Conic Shape Primitives`, `Shapely Transform Tests`, `Random Generator Logic`, `Shapely Compound Shape Tests`, `Generator Base Classes`, `Periodic Stripe Shape`, `Shapely Adapter Modules`, `PyTorch Differentiability`, `Boolean Shape Tests`?**
  _High betweenness centrality (0.143) - this node is a cross-community bridge._
- **Why does `UnitCell` connect `YAML & Unit Cell Serialization` to `Random Generator & Lattice`, `Shape Analysis & SDF Concepts`, `Unit Cell Analyzer`, `YAML Serialization Tests`, `Random Generator Logic`, `Shapely Compound Shape Tests`, `Generator Integration Tests`, `Generator Base Classes`, `Unit Cell Tests`, `PyTorch Differentiability`, `Lattice SDF Tests`, `Mask Tests`, `Generator Validation`, `UnitCell Shapely Tests`, `Boundary Tests`, `Serialization Tests`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `UnitCell` (e.g. with `TestLeafShapes` and `TestCellMetrics`) actually correct?**
  _`UnitCell` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `Rectangle` (e.g. with `TestLeafShapes` and `TestCellMetrics`) actually correct?**
  _`Rectangle` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Lattice` (e.g. with `TestLeafShapes` and `TestCellMetrics`) actually correct?**
  _`Lattice` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `UnitCellAnalyzer` (e.g. with `TestLeafShapes` and `TestCellMetrics`) actually correct?**
  _`UnitCellAnalyzer` has 18 INFERRED edges - model-reasoned connections that need verification._