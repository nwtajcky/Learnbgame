'''
Copyright (C) 2018 CG Cookie
http://cgcookie.com
hello@cgcookie.com

Created by Jonathan Denning, Jonathan Williamson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from .options import retopoflow_version


# sync help texts with https://github.com/CGCookie/retopoflow-docs (http://docs.retopoflow.com/)

# https://wincent.com/wiki/Unicode_representations_of_modifier_keys

help_firsttime = '''
# Welcome to RetopoFlow {version}!

RetopoFlow is an add-on for Blender that brings together a set of retopology tools within a custom Blender mode to enable you to work more quickly, efficiently, and in a more artist-friendly manner.
The RF tools, which are specifically designed for retopology, create a complete workflow in Blender without the need for additional software.

The RetopoFlow tools automatically generate geometry by drawing on an existing surface, snapping the new mesh to the source surface at all times, meaning you never have to worry about your mesh conforming to the original model---no Shrinkwrap modifier required!
Additionally, all mesh generation is quad-based (except for PolyPen).


## Changelog

Below is a summary of the changes made.
A full summary is available on [Blender Market](https://blendermarket.com/products/retopoflow).

### Changes in 2.0.3

- Hiding RF buttons in 3D View panel to improve overall performance when Region Overlap is disabled
- Visualizing target geometry counts in bottom right corner
- Improved target rendering by constraining normal offset
- Only showing "small clip start" alert once per Blender run rather than once per RetopoFlow run
- By default, the options for unselected tools are hidden (can disable Options > General > Tool Options > Auto Hide Options).
- Overall stability improvements

### Minor Changes from Version 2.0.0

- Can navigate to all help documents through help system.
  (Click [All Help Documents](All Help Documents) button below or press `Shift+F1`)
- Fixed bug where navigation broke with internationalization settings
- Improved many UX/UI issues.
  For example, now the RetopoFlow panel will explicitly state whether a new target will be created and what meshes are acting as sources.
  For another example, RetopoFlow will now gracefully handle registration failures (usually happening when Blender is installed through package manager).
- Squashed many hard-to-find bugs in Loops, PolyPen, Patches, Strokes, Contours
- Better error handling with shader compilation.
- Fixed critical bug with framework.

### Major Changes from Version 1.x

What you see behind this message window is a complete rewrite of the code base.
RetopoFlow 2.x now works like any other Blender mode, like Edit Mode or Sculpt Mode, but it will also feel distinct.
We focused our 2.x development on two main items: stability and user experience.
With an established and solid framework, we will focus more on features in future releases.

- Everything runs within the RF Mode; no more separation of tools!
  In fact, the shortcut keys `Q`, `W`, `E`, `R`, `T`, `Y`, `U`, and `I` will switch quickly between the tools.
- Each tool has been simplified to perform its job well.
- All tools use the current selection for their context.
  For example, PolyStrips can edit any strip of quads by simply selecting them.
- The selected and active mesh is the Target Mesh, and any other visible meshes are Source Meshes.
- Many options and configurations are sticky, which means that some settings will remain even if you leave RF Mode or quit Blender.
- All tools have similar and consistent visualization, although they each will have their own custom widget (ex: circle cursor in Tweak) and annotations (ex: edge count in Contours).
- Mirroring (X, Y, and/or Z) is now visualized by overlaying a color on all the source meshes.
- Every change automatically commits to the target mesh; geometry is created in real-time!
  No more lost work from crashing.
- Auto saves will trigger!
- Undo and redo are universally available within RF Mode.
  Press `Ctrl+Z` roll back any change, or `Ctrl+Shift+Z` to redo.
- The new Strokes tool extends your target mesh with a simple selection and stroke.


## Feedback

We want to know how RetopoFlow has benefited you in your work.
Please consider doing the following:

- Give us a rating with comments on the Blender Market.
  (requires purchasing a copy through Blender Market)
- Purchase a copy of RetopoFlow on the Blender Market to help fund future developments.
- Consider donating to our drink funds :)

We have worked hard to make this as production-ready as possible.
We focused on stability and bug handling in addition to new features, improving overall speed, and making RetopoFlow easier to use.
However, if you find a bug or a missing feature, please let us know so that we can fix them!
Be sure to submit screenshots, .blend files, and/or instructions on reproducing the bug to our bug tracker by clicking the "Report Issue" button or visiting [https://github.com/CGCookie/retopoflow/issues](https://github.com/CGCookie/retopoflow/issues).
We have added buttons to open the issue tracker in your default browser and to save screenshots of Blender.

![](help_exception.png)


## Known Issues / Future Work

Below is a list of known issues that are currently being addressed.

- Source meshes with very high poly count can cause a delay and stutter at start-up time.
- A target mesh with high poly count target mesh can cause slowness in some tools.
- RF runs _very_ slowly (<1.0 FPS) on a few rare machines.
- Patches supports only rudimentary fills.
- RetopoFlow does not work with Blender 2.80 (beta).



## Final Words

We thank you for using RetopoFlow, and we look forward to hearing back from you!

Cheers!

<br>
---The CG Cookie Tool Development Team
'''.format(version=retopoflow_version)


help_quickstart = '''
RetopoFlow 2.x Quick Start Guide
================================

We wrote this guide to help you get started as quickly a possible with the new RetopoFlow 2.x.
More detailed help is available by pressing `F1` after you start RetopoFlow.


TL;DR
-----

==> When you are retopologizing for the first time, deselect all objects and click one of the RetopoFlow tools.

==> When continuing work on a previous retopology session, select the target object, and click one of the RetopoFlow tools.


Terminology
-----------

Source Object(s)

: The original object(s) that you are re-creating.  These meshes typically have a high polygon count with poor topology and edge flow (ex: result of Dyntopo in Sculpt Mode).

Target Object

: The new object that stores the retopologized surface.  This mesh typically has a low polygon count with good topology and edge flow.


Target and Source Objects
-------------------------

In RetopoFlow 1.x you were required to select the source and target objects explicitly, but in RetopoFlow 2.x the source and target objects are determined by RetopoFlow based on which mesh objects are selected, active, and visible.

The target object is either:

- the active mesh object if it is also selected and visible (Object Mode)
- the mesh object currently being edited (Edit Mode)
- otherwise, a newly created mesh object

Any mesh object that is visible and not the target object is considered a source object.
This means that you can hide or move objects to hidden layers to change which source objects will be retopologized.
Note: only newly created or edited target geometry will snap to the source.


RetopoFlow Mode
---------------

Notes about earlier version: the tools in RetopoFlow 1.x were set of disjointed tools, where you would need to quit one tool in order to start another.
Also, because we wrote RF 1.x tools separately, the visualizations and settings were not consistent.
Furthermore, the only indication that a tool was running in RetopoFlow 1.x was a small "Click for Help" button in the top-right corner, which is easily missed.

In RetopoFlow 2.x, we completely rewrote the framework so that RF acts like any other Blender Mode (like Edit Mode, Sculpt Mode, Vertex Paint Mode).
Choosing one of the tools from the RetopoFlow panel will start RetopoFlow Mode with the chosen tool selected.

When RetopoFlow Mode is enabled, all parts of Blender outside the 3D view will be darkened (and disabled) and windows will be added to the 3D view.
These windows allow you to switch between RF tools, set tool options, and get more information.
Also, a one-time Welcome message will greet you.

'''


help_all = '''
# All Help Documents

Below are links to all of the help documents built into RetopoFlow.

More detailed online documentation coming soon!

## Help Documents

'''
help_all_updated = False


help_general = '''
# General Help

When RetopoFlow Mode is enabled, certain shortcuts are available regardless of the tool selected.
For tool-specific help, select the tool from the Tools panel, and either press `F2` or click Tool Help.

Click the [All Help Documents](All Help Documents) button below or press `Shift+F1` to see all of the built-in documentation.

Below is a brief description of some of the features in RetopoFlow.
For more details, see the tooltips when hovering or the product documentation page.


## RetopoFlow Shortcuts

|  |  |  |
| --- | --- | --- |
| `Esc` <br> `Tab` | : | quit RetopoFlow |
| `Shift+F1` | : | view all help documents |
| `F1` | : | view general help |
| `F2` | : | view tool help |
| `F9` | : | toggle on/off main RF windows |

## Tool Shortcuts

Pressing the tool's shortcut will automatically switch to that tool.
Note: selection and the undo stack is maintained between tools.

|  |  |  |
| --- | --- | --- |
| `Q` | : | Contours |
| `W` | : | PolyStrips |
| `E` | : | PolyPen |
| `R` | : | Relax |
| `T` | : | Tweak |
| `Y` | : | Loops |
| `U` | : | Patches |
| `I` | : | Strokes |


## Universal Shortcuts

The following shortcuts work across all the tools, although each tool may have a distinct way of performing the action.
For example, pressing `G` in Contours will slide the selected loop.

|  |  |  |
| --- | --- | --- |
| `A` | : | deselect / select all |
| `Action` drag | : | transform selection |
| `Shift+Select` click | : | toggle selection |
| `Select` drag <br> `Shift+Select` drag | : | selection painting |
| `Ctrl+Select` <br> `Ctrl+Shift+Select` | : | smart selection |
| `G` | : | grab and move selected geometry |
| `X` | : | delete / dissolve selection |
| `Ctrl+Z` | : | undo |
| `Ctrl+Shift+Z` | : | redo |


## Defaults

The `Action` command is set to the left mouse button.

The `Select` command is set to the right mouse button.


## General Options

The Maximize Area button will make the 3D view take up the entire Blender window, similar to pressing `Ctrl+Up` / `Shift+Space` / `Alt+F10`.

The Snap Verts button will snap either All vertices or only Selected vertices to the nearest point on the source meshes.

The Theme option changes the color of selected geometry.

![](help_themes.png)

When the Auto Collapse Options is checked, tool options will automatically collapse in the options panel when the current tool changes.


## Symmetry Options

The X, Y, Z checkboxes turn on/off symmetry or mirroring along the X, Y, Z axes.
Note: symmetry utilizes the mirror modifier.

When symmetry is turned on, the mirroring planes can be visualized on the sources choosing either the Edge or Face option.
The Effect setting controls the strength of the visualization.
'''


help_contours = '''
# Contours Help

The Contours tool gives you a quick and easy way to retopologize cylindrical forms.
For example, it's ideal for organic forms, such as arms, legs, tentacles, tails, horns, etc.

The tool works by drawing strokes perpendicular to the form to define the contour of the shape.
Each additional stroke drawn will either extrude the current selection or cut a new loop into the edges drawn over.

You may draw strokes in any order, from any direction.

![](help_contours.png)


## Drawing

|  |  |  |
| --- | --- | --- |
| `Action` | : | select and slide loop |
| `Select` <br> `Shift+Select` | : | select edge |
| `Ctrl+Select` <br> `Ctrl+Shift+Select` | : | select loop |
| `Ctrl+Action` | : | draw contour stroke perpendicular to form. newly created contour extends selection if applicable. |
| `A` | : | deselect / select all |
| `F` | : | Bridge selected edge loops |

## Transform

|  |  |  |
| --- | --- | --- |
| `G` | : | slide |
| `S` | : | shift |
| `Shift+S` | : | rotate |

## Other

|  |  |  |
| --- | --- | --- |
| `X` | : | delete/dissolve selected |
| `Shift+Up` <br> `Shift+Down` | : | increase / decrease segment counts |
| `Equals` <br> `Minus` | : | increase / decrease segment counts |

## Tips

- Extrude Contours from an existing edge loop by selecting it first.
- Contours works with symmetry, enabling you to contour torsos and other symmetrical objects!
'''


help_polystrips = '''
# PolyStrips Help

The PolyStrips tool provides quick and easy ways to map out key face loops for complex models.
For example, if you need to retopologize a human face, creature, or any other complex organic or hard-surface object.

PolyStrips works by hand drawing strokes on to the high-resolution source object.
The strokes are instantly converted into spline-based strips of polygons.

Any continuous quad strip may be manipulated with PolyStrips via the auto-generated spline handles.

![](help_polystrips.png)

## Drawing

|  |  |  |
| --- | --- | --- |
| `Action` | : | select quad then grab and move |
| `Select` <br> `Shift+Select` | : | select quads |
| `Ctrl+Select` <br> `Ctrl+Shift+Select` | : | select quad strip |
| `Ctrl+Action` | : | draw strip of quads |
| `F` | : | adjust brush size |
| `A` | : | deselect / select all |

## Control Points

|  |  |  |
| --- | --- | --- |
| `Action` | : | translate control point under mouse |
| `Shift+Action` | : | translate all inner control points around neighboring outer control point |
| `Ctrl+Shift+Action` | : | scale strip width by click+dragging on inner control point |

## Other

|  |  |  |
| --- | --- | --- |
| `X` | : | delete/dissolve selected |
| `Shift+Up` <br> `Shift+Down` | : | increase / decrease segment count of selected strip(s) |
| `Equals` <br> `Minus` | : | increase / decrease segment count of selected strip(s) |
'''


help_polypen = '''
# PolyPen Help

The PolyPen tool provides absolute control for creating complex topology on a vertex-by-vertex basis (e.g., low-poly game models).
This tool lets you insert vertices, extrude edges, fill faces, and transform the subsequent geometry all within one tool and in just a few clicks.

![](help_polypen.png)

## Drawing

|  |  |  |
| --- | --- | --- |
| `Select` <br> `Shift+Select` | : | select geometry |
| `Ctrl+Action` | : | insert geometry connected to selected geometry |
| `Shift+Action` | : | insert edges only |
| `A` | : | deselect / select all |

## Other

|  |  |  |
| --- | --- | --- |
| `X` | : | delete/dissolve selected |

## Tips

Creating vertices/edges/faces is dependent on your selection:

- When nothing is selected, a new vertex is added.
- When a single vertex is selected, an edge is added between mouse and selected vertex.
- When an edge is selected, a triangle is added between mouse and selected edge.
- When a triangle is selected, a vertex is added to the triangle, turning the triangle into a quad

Selecting an edge and clicking onto another edge will create a quad in one step.

The PolyPen tool can be used like a knife, cutting vertices into existing edges for creating new topology routes.
'''

help_tweak = '''
# Tweak Help

The Tweak tool allows you to easily adjust vertex positions with a brush.

![](help_tweak.png)

## Actions

|  |  |  |
| --- | --- | --- |
| `Action` | : | move all vertices within brush radius |
| `Shift+Action` | : | move only selected vertices within brush radius |
| `F` | : | adjust brush size |
| `Shift+F` | : | adjust brush strength |
| `Ctrl+F` | : | adjust brush falloff |

## Options

Tweak has several options to control which vertices are or are not moved.

- Boundary: allow boundary vertices to be moved.
- Hidden: allow vertices that are behind geometry to be moved.
- Selected: limit transformation to selection
'''

help_relax = '''
# Relax Help

The Relax tool allows you to easily relax the vertex positions using a brush.

![](help_relax.png)

## Actions

|  |  |  |
| --- | --- | --- |
| `Action` | : | relax all vertices within brush radius |
| `Shift+Action` | : | relax only selected vertices within brush radius |
| `F` | : | adjust brush size |
| `Shift+F` | : | adjust brush strength |
| `Ctrl+F` | : | adjust brush falloff |

## Options

Relax has several options to control which vertices are or are not moved.

- Boundary: allow boundary vertices to be moved.
- Hidden: allow vertices that are behind geometry to be moved.
- Selected: limit transformation to selection
'''

help_loops = '''
# Loops Help

The Loops tool allows you to insert new edge loops along a face loop and slide any edge loop along the source mesh.
The Loops tool also works on any strip of edges.

![](help_loops.png)

## Actions

|  |  |  |
| --- | --- | --- |
| `Ctrl+Action` | : | insert edge loop |
| `Select` <br> `Shift+Select` | : | select edge(s) |
| `Ctrl+Select` <br> `Ctrl+Shift+Select` | : | select edge loop |
| `S` | : | slide edge loop |
'''

help_patches = '''
# Patches Help

The Patches tool helps fill in holes in your topology.
Select the strip of boundary edges that you wish to fill.

## Actions

|  |  |  |
| --- | --- | --- |
| `Select` <br> `Shift+Select` | : | select edge |
| `Ctrl+Select` <br> `Ctrl+Shift+Select` | : | select edge loop |
| `Shift+Up` <br> `Shift+Down` | : | adjust segment count |
| `Ctrl+Shift+Action` | : | toggle vertex as corner |
| `F` | : | fill visualized patch |

## Notes

The Patches tool currently only handles a limited number of selected regions.
More support coming soon!

- 2 connected strips in an L-shape
- 2 parallel strips: the two strips must contain the same number of edges
- 3 connected strips in a C-shape: first and last strips must contain the same number of edges
- 4 strips in a rectangular loop: opposite strips must contain the same number of edges

![](help_patches_2sides_beforeafter.png)

If no pre-visualized regions show after selection, no geometry will be created after pressing F.

Adjust the Angle parameter to help Patches determine which connected edges should be in the same strip.
Alternatively, you can manually toggle vertex corners using `Ctrl+Shift+Action`.
'''

help_strokes = '''
# Strokes Help

The Strokes tool helps fill in holes in your topology.
This tool lets you insert edge strips and extruding edges by brushing a stroke on the source.

![](help_strokes.png)

## Drawing

|  |  |  |
| --- | --- | --- |
| `Select` <br> `Shift+Select` | : | select geometry |
| `Ctrl+Select` <br> `Ctrl+Shift+Select` | : | select edge loop |
| `Ctrl+Action` | : | insert edge strip / extrude selected geometry |
| `A` | : | deselect / select all |
| `Shift+Up` <br> `Shift+Down` | : | adjust segment count |

## Other

|  |  |  |
| --- | --- | --- |
| `X` | : | delete/dissolve selected |

## Tips

Creating geometry is dependent on your selection:

- When nothing is selected, a new edge strip is added
- When an edge strip is selected and stroke is not a loop, the selected edge strip is extruded to the stroke
- When an edge loop is selected and stroke is a loop, the selected edge loop is extruded to the stroke

Note: only edges on boundary of target are considered in selection.

If stroke starts or ends on existing vertex, the Strokes tool will try to bridge the extruded geometry.
'''

help_stretch = '''
# Stretch Help

This is an experimental tool.
More details will come as the tool matures.
'''

help_greasepencil = '''
# Grease Pencil Help

This is an experimental tool.
More details will come as the tool matures.
'''

