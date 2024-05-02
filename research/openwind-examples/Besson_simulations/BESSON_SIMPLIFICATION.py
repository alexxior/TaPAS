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
Created on Fri Mar 20 16:19:11 2020

@author: Augustin Ernoult, Tobias Van Baarsel
"""

import numpy as np
import matplotlib.pyplot as plt

from openwind import InstrumentGeometry, FrequentialSolver, InstrumentPhysics, Player
from openwind.impedance_tools import plot_impedance, read_impedance, find_peaks_measured_impedance

from openwind.technical import protogeometry_design, AdjustInstrumentGeometry
from openwind.inversion import InverseFrequentialResponse


"""
This example presents how the geometry obtained by tomographie and
molding, have been simplified to reach acoustic and manufacturing objectives.
The project build around this trumpet is detailed in: https://inria.hal.science/hal-04352706
It has been presented in:
- CFA 2022: https://hal.science/hal-03848341
- Vienna Talks 2022: https://inria.hal.science/hal-03842072
"""


# %% TOMOGRAPHY DATA :

# Load the geometry obtained from post-treatment of the tomography data and
# the molding of the embouchure.

tomo_file = 'geometries/tomo_molding_combined_0925.txt'
tomo_data = InstrumentGeometry(tomo_file)
tomo_length = tomo_data.get_main_bore_length()

x = np.linspace(0, tomo_length, 10000)
fig1, ax1 = plt.subplots()
ax1.plot(x, tomo_data.get_main_bore_radius_at(x), label='Tomography + Molding')
# %% Initial rough geometries

# The composition (in term of shape) of the initial guess of the geometry is determined
# by hand, by looking at the tomography geometry (and some trial and error steps).
init_geom_optim = protogeometry_design(0.0,
                            tomo_length,
                            segments=[7.7e-3, 10.6e-3, 87.5e-3, 1.4, 1.7,2.04],
                            N_subsegments=[1,1,1,4,1,1,1],
                            types=['spline5','cone', 'spline5','cone','spline','bessel','bessel'],
                            r_start=9.5e-3,#tomo_data.get_main_bore_radius_at(0),
                            r_end=tomo_data.get_main_bore_radius_at(tomo_length),
                            target_geom=tomo_data,
                            )

# init_geom_optim = InstrumentGeometry(simple_geom)
init_geom_optim.constrain_parts_length() # constrain the length of each part to be positive
optim_params = init_geom_optim.optim_params

ax1.plot(x, init_geom_optim.get_main_bore_radius_at(x), '--', label='TEST')

# %% Simplification only based on geometrical aspect

# this initial guess is firstly optimized only on geometric considerations.
# this is done in two steps: 1) only the radii are adjsuted
N_design = len(optim_params.get_active_values())
n_pos = [k for k,s in enumerate(optim_params.labels) if 'pos' in s]
n_active = [n for n in range(N_design) if n not in n_pos]
optim_params.set_active_parameters(n_active) # active only parameters which are not positions.


AIG1 = AdjustInstrumentGeometry(init_geom_optim, tomo_data)
adjusted1 = AIG1.optimize_geometry(iter_detailed=False, max_iter = 100)

# 2) All the parameters (excepted boundaries positions) are adjusted.
n_active = [n for n in range(N_design) if n!=n_pos[-1]]# and n!=n_pos[0]]
optim_params.set_active_parameters(n_active)
adjusted2 = AIG1.optimize_geometry(iter_detailed=False, max_iter = 100)

adjusted2.write_files('geometries/AUTO_geom_adjusted', digit=6, disp_optim=True)

# We compare the obtained geom to the one from tomo
R_geom_adjust = adjusted2.get_main_bore_radius_at(x)
ax1.plot(x, R_geom_adjust, '--', label='Auto Simplified')
plt.legend()


fine_error = np.abs(adjusted2.get_main_bore_radius_at(x) -
                        tomo_data.get_main_bore_radius_at(x))*1e3
print("*"*20 + "\nGeometric deviation after adjustement:")
print(f"\tMaximal deviation: {max(fine_error):.2}mm")
print(f"\tMean deviation: {np.mean(fine_error):.2}mm\n" + "*"*20)

# %% Acoustic measurement

# The impedance simulated from this geometry is compared to the impedance measured
# on the original instrument from museum.
fmeas, Zmeas = read_impedance('Impedances/MEAS_E0925_impedance_mean_20degC_11-03-22.txt')

# crop data to avoid to compute impedance at too low/high frequency
fmin=30
fmax = 3000
nfmin = np.argmin(np.abs(fmeas - fmin))
nfmax = np.argmin(np.abs(fmeas - fmax))
fmeas = fmeas[nfmin:nfmax+1]
Zmeas = Zmeas[nfmin:nfmax+1]

# compute the impedance at the same frequencies.
temperature=20
instru_physics = InstrumentPhysics(adjusted2, temperature, Player(), losses=True)
res_init = FrequentialSolver(instru_physics, fmeas)
res_init.solve()
Zinit = res_init.impedance/res_init.get_ZC_adim()
fres_init, ares_init, qres_init = res_init.resonance_peaks(k=10, display_warning=False)

# We plot.
fig3 = plt.figure()
plot_impedance(fmeas, Zmeas, figure = fig3, label='Meas.')
plot_impedance(fmeas, Zinit, figure = fig3, label='Init geom')

# %% Acoustic optimization

# For the acoustic optimization of the main bore, we impose to keep the mouthpiece geometry
# (deactivate the corresponding (n<=13) design parameters).
# We also chose to modify only the position.
n_active = [n for n in range(N_design) if n in n_pos and n>=13]
optim_params.set_active_parameters(n_active)

# We chose to optimize the geometry to fit the frequency of resonances.
# In this purpose we find these frequency in the measurements and we focus the optimization
# to surrounding frequency ranges. The first peak is remove as it is never played.
fres_meas, ares_meas, qres_meas = find_peaks_measured_impedance(fmeas, Zmeas, Npeaks=10, fmin=30, display_warning=False)
fres_extended = np.sort(np.hstack([(1+coeff)*fres_meas[1:] for coeff in [-2e-3,-1e-3,-5e-4,0,5e-4,1e-3,2e-3]]))
foptim = np.hstack([fres_extended, np.linspace(1000, 3000,10)])
Ztarget = np.interp(foptim, fmeas, Zmeas)

optim = InverseFrequentialResponse(instru_physics, foptim, [Ztarget])
optim.optimize_freq_model(iter_detailed=True)

# The obtained geometry is saved and compared to th other in a plot. The major change
# is a slight elongation of the instrument.
adjusted2.write_files('geometries/AUTO_acoustic_adjusted', digit=4, disp_optim=False)

x_optim = np.linspace(0, adjusted2.get_main_bore_length(), 10000)
ax1.plot(x_optim, adjusted2.get_main_bore_radius_at(x_optim), label='Acoustic optim')
ax1.legend()

# %% Impedance comparison

# To compare the final impedances, we recompute the optimized impedance for
# finer frequency step.
optim.update_frequencies_and_mesh(fmeas)
optim.solve()
optim.plot_impedance(figure = fig3, label='Optim geom')

# The characteristics of the resonances (freq and mag.) from the different
# impedances are compared.
fres_optim, ares_optim, qres_optim = optim.resonance_peaks(k=10, display_warning=False)
fig_res, ax_res = plt.subplots(2,1, sharex=True)
for ax in ax_res:
    ax.set_xlabel('Frequency of Resonance [Hz]')
    ax.grid(True)
ax_res[0].plot(fres_meas, 20*np.log10(ares_init/ares_meas), 'o', label='Init.')
ax_res[0].plot(fres_meas, 20*np.log10(ares_optim/ares_meas), 'o', label='Init.')
ax_res[0].set_ylabel('Amplitude deviation [dB]')

ax_res[1].plot(fres_meas, 1200*np.log2(fres_init / fres_meas), 'o')
ax_res[1].plot(fres_meas, 1200*np.log2(fres_optim / fres_meas), 'o')
ax_res[1].set_ylabel('Frequency deviation [cents]')


plt.show()
