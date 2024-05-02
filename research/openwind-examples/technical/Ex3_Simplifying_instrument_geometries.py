#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2023, INRIA
#
# This file is part of Openwind.
#
# Openwind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Openwind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openwind.  If not, see <https://www.gnu.org/licenses/>.
#
# For more informations about authors, see the CONTRIBUTORS file

"""
This example shows how to simplify a complicated instrument geometry
"""
import os

import matplotlib.pyplot as plt

from openwind import InstrumentGeometry
from openwind.technical import AdjustInstrumentGeometry, protogeometry_design

path = os.path.dirname(os.path.realpath(__file__))

# If you wish to import a real existing instrument to OpenWind, you probably
# have access to it's bore, either via measurements or directly from the
# maker's plan.
# If you measured a real instrument, you have noted the radius of the bore at
# different points of the instrument - the more precise the measurement, the
# smaller the distance between the measurement points and therefore the more
# data.

# In OpenWind, calculating the acoustic behaviour of an instrument with a large
# amount of parts can take a (very) long time.
# Moreover, these data points can be noisy (due to measurements errors).
# This is why it is interesting to simplify a complicated instrument
# geometry.


# we load a complex instrument with a lot of segments
complex_instr = InstrumentGeometry(os.path.join(path, 'Ex3_complex_instrument.txt'))


# The geometry simplification is done by an optimization process. We need to
# give OpenWind a starting shape and set the values we want to be optimized
# by writing them between '' and with a tilde ~ in front.

# %% Manual choice for the intial geometry

# This can be done by either entering the starting shape manually as follows :
# Here we try to simplify our instrument down to 8 linear segments, where the
# lengths of the segments are fixed, and the radii are to be optimized.
# It is important to ensure that the two instruments have similar length.

Ltot = complex_instr.get_main_bore_length()
simplified_bore = [[0.0, 0.2, '~0.005', '~0.005', 'linear'],
                   [0.2, 0.4, '~0.005', '~0.005', 'linear'],
                   [0.4, 0.6, '~0.005', '~0.005', 'linear'],
                   [0.6, 0.8, '~0.005', '~0.005', 'linear'],
                   [0.8, 1.0, '~0.005', '~0.005', 'linear'],
                   [1.0, 1.2, '~0.005', '~0.005', 'linear'],
                   [1.2, 1.4, '~0.005', '~0.005', 'linear'],
                   [1.4, Ltot, '~0.005', '~0.005', 'linear']]
simplified_instr = InstrumentGeometry(simplified_bore)


print("Simplified instrument with cones:")
# the AdjustInstrumentGeometry is instanciated from the two Instrument Geometries
adjustment = AdjustInstrumentGeometry(simplified_instr, complex_instr)
# the optimization process is carried out
adjusted_instr = adjustment.optimize_geometry(iter_detailed=False, max_iter=100)

fig2 = plt.figure(2)
complex_instr.plot_InstrumentGeometry(figure=fig2, linestyle=':')
adjusted_instr.plot_InstrumentGeometry(figure=fig2)
plt.title('A complex instrument (dotted line) and the simplification by\n'
          ' conical segments (solid line)')


# As you can see, the simplification works well for the conical parts in the
# original instrument, but the round parts are not well approximated by
# conical segments.

# We need to help OpenWind a bit more.

# -----------------------------------------------------------------------------
print("\n-------------\n")

# By looking at the bore of the instrument we can make better guesses for the
# simplification.

# Straight parts are well approximated by linear segments, curved parts can
# at least be simplified to splines (although exp or bessel may give better
# results)
better_simpl_bore = [[0.0, 0.015, '~0.005', '~0.005', 'spline', 0.005, 0.01, '~0.005', '~0.005'],
                     [0.015, 0.1, '~0.005', '~0.005', 'linear'],
                     [0.1, 0.3, '~0.005', '~0.005', 'spline', 0.2, '~0.005'],
                     [0.3, 0.5, '~0.005', '~0.005', 'linear'],
                     [0.5, 1.0, '~0.005', '~0.005', 'linear'],
                     [1.0, Ltot, '~0.005', '~0.005', 'spline', 1.2, 1.3, '~0.005', '~0.005']]

better_simpl_instr = InstrumentGeometry(better_simpl_bore)

print("Simplified instrument with complex shapes:")
# the AdjustInstrumentGeometry is instanciated from the two Instrument Geometries
better_adjust = AdjustInstrumentGeometry(better_simpl_instr, complex_instr)
# the optimization process is carried out
better_adjusted_instr = better_adjust.optimize_geometry(iter_detailed=False,
                                                   max_iter=100)


fig3 = plt.figure(3)
complex_instr.plot_InstrumentGeometry(figure=fig3, linestyle=':')
better_adjusted_instr.plot_InstrumentGeometry(figure=fig3)
plt.title('A complex instrument (dotted line) and the simplification by\n'
          ' well-chosen different shapes (solid line)')

# Much better ! Some errors remain, for instance at the end of the horn. This
# is a matter of tweaking and trying out different shapes and parameters.

# -----------------------------------------------------------------------------

# With this method a complex instrument described by 1500 sections is
# simplified to 6 parts, which greatly decreases computation time.


# The new simplified instrument can be saved in a file :
better_adjusted_instr.write_files(os.path.join(path, 'simplified_instrument'))

plt.show()

# %% Use of automatic generation proto-geometry


# The writting of the initial guest of the geometry can be tedious,
# all this is easier with the ProtoGeometry function. Similar tests as before
# will be repeated, but this time, the boundary position will also be optimized.

# Here the 8 conical segments case. This example sets 8 floating sub-segments
# for the whole instrument. They are initially equally spaced along the
# instrument.
no_fixed_point = protogeometry_design(0.0,  # starting x point
                               Ltot,  # ending x point
                               N_subsegments=[8])  # number of floating sub-segments for each segment

# the AdjustInstrumentGeometry is instanciated from the two Instrument Geometries
adjust_0 = AdjustInstrumentGeometry(no_fixed_point, complex_instr)
adjusted_0 = adjust_0.optimize_geometry(iter_detailed=False, max_iter=100)


fig1 = plt.figure(1)
complex_instr.plot_InstrumentGeometry(figure=fig1, linestyle=':')
adjusted_0.plot_InstrumentGeometry(figure=fig1)
plt.title('A complex instrument (dotted line) and the simplification by\n'
          ' 8 floating conical segments (solid line)')


# -----------------------------------------------------------------------------

print("Simplified instrument with cones:")
# The following example force two intial points around the round part of the
# instrument to force a change of segment there. For theses segments, we use
# respectively 3, 2 and 5 floating sub-segments. All sub-segments are linear for now.

two_fixed_points = protogeometry_design(0.0,  # starting x point
                                 Ltot,  # ending x point
                                 segments=[100e-3, 300e-3],  # fixed segment border
                                 N_subsegments=[3,2,5],  # number of floating sub-segments for each segment
                                 types=['linear', 'linear','linear'],  # type of floating sub-segments
                                 r_start=9e-3, r_end=5e-2, # it can be useful to impose the boundaries radius
                                 )
# In this case, by default, all geometric parameters will be optimized. It
# is possible to chose to activate/deactivate some parameters, here the forced,
# positions, this can be ckecked by printing the "optim_params"
two_fixed_points.optim_params.change_activation_by_label(['bore2_pos_plus', 'bore4_pos_plus', 'bore9_pos_plus'], False)
print(two_fixed_points.optim_params)

# the AdjustInstrumentGeometry is instanciated from the two Instrument Geometries
# then the optimization process is carried out
adjust_2 = AdjustInstrumentGeometry(two_fixed_points,
                                    complex_instr)
adjusted_2 = adjust_2.optimize_geometry(iter_detailed=False, max_iter=100)

fig2 = plt.figure(2)
complex_instr.plot_InstrumentGeometry(figure=fig2, linestyle=':')
adjusted_2.plot_InstrumentGeometry(figure=fig2)
plt.title('A complex instrument (dotted line) and the simplification by\n'
          ' conical segments (solid line), with 2 fixed points')


# As you can see, the simplification works well for the conical parts in the
# original instrument, but the round parts are not well approximated by
# conical segments.

# We can use other types of geometries for that.


# -----------------------------------------------------------------------------
print("Simplified instrument with complex shapes:")

# By looking at the bore of the instrument we can make better guesses for the
# simplification.

# Straight parts are well approximated by linear segments, curved parts can
# at least be simplified to splines (although exp or bessel may give better
# results)

# Let's use the fixed points to define five segments, and use splines to
# approximate the curved parts :

# The begin and end points are always fixed and are set to 0.0 and 1.5,
# respectively.
# We have five fixed segments : [[0.0, 0.02],
#                                [0.02, 0.1],
#                                [0.1, 0.3],
#                                [0.3, 1.0],
#                                [1.0, 1.5]]

# The first segment is a spline with 4 knots (only 1 sub-segment);
# The second segment is composed of two linear sub-segments ;
# The third is a spline with 3 knots (only 1 sub-segment);
# The fourth is composed of 3 linear sub-segments ;
# The fifth and last is a spline with 5 knots (only 1 sub-segment).

# If the complex geometry is given, its radius is used to initiate the radius
# boundaries of each segment/subsegment.

better_simplification = protogeometry_design(0.0,
                                      Ltot,
                                      segments=[0.02, 0.1, 0.3, 1.0],
                                      N_subsegments=[1, 2, 1, 3, 1],
                                      types=['spline4', 'linear', 'spline3', 'linear', 'spline5'],
                                      target_geom=complex_instr,
                                      )
better_simplification.optim_params.change_activation_by_label(['bore7_pos_plus'], False) # keep last pos unchanged


# the AdjustInstrumentGeometry is instanciated from the two Instrument Geometries
# then the optimization process is carried out
better_adjust = AdjustInstrumentGeometry(better_simplification, complex_instr)
better_adjusted_instr = better_adjust.optimize_geometry(iter_detailed=False,
                                                   max_iter=100)


fig3 = plt.figure(3)
complex_instr.plot_InstrumentGeometry(figure=fig3, linestyle=':')
better_adjusted_instr.plot_InstrumentGeometry(figure=fig3)
plt.title('A complex instrument (dotted line) and the simplification by\n'
          ' well-chosen different shapes (solid line)')

# Much better ! Some errors remain, for instance at the end of the horn. This
# is a matter of tweaking and trying out different shapes and parameters.



plt.show()
