#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021, INRIA
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

import os

import numpy as np
import matplotlib.pyplot as plt

from openwind import ImpedanceComputation
from openwind.impedance_tools import read_impedance, plot_impedance, find_peaks_measured_impedance

"""
In this file the impedance of the geometries finally kept for the study are compared to
measurements.
The project build around this trumpet is detailed in: https://inria.hal.science/hal-04352706
It has been presented in:
- CFA 2022: https://hal.science/hal-03848341
- Vienna Talks 2022: https://inria.hal.science/hal-03842072
"""

plt.close('all')
temperature = 20

fold_geom = 'geometries'
fold_Z = 'Impedances'

# %% Load the measured data
freq_orig, Z_Orig = read_impedance(os.path.join('Impedances','MEAS_E0925_impedance_mean_20degC_11-03-22.txt'))
freq_facsim, Z_FacSim = read_impedance(os.path.join('Impedances','MEAS_FacSimile_impedance_mean_20degC_11-03-22.txt'))


# %% Simulate the impedances for retained geometries:



def get_data(geom_file, z_file):

    freq = np.arange(30,3001,1)
    files_simu = [f for f in os.listdir(fold_Z) if os.path.isfile(os.path.join(fold_Z, f))]

    if z_file in files_simu: # avoid to recompute the impedance if already computed
        freq, Z = read_impedance(os.path.join(fold_Z, z_file))
    else:
        tomo_res = ImpedanceComputation(freq, os.path.join(fold_geom, geom_file),
                                        temperature=temperature,
                                        # l_ele = 1e-2,
                                        enable_tracker_display=True,
                                        )
        tomo_res.write_impedance(os.path.join(fold_Z, z_file), normalize=True)
        freq = freq
        Z = tomo_res.impedance/tomo_res.Zc
    return freq, Z

f_tomo, Z_tomo = get_data('tomo_molding_combined_0925.txt', f'SIMU_tomo_molding_{temperature}degC.txt')
# f_copy, Z_copym = get_data('Manufactured_Copy_E0925.txt', f'SIMU_copy_{temperature}degC.txt')
f_optim, Z_optim = get_data('optimized_simplified.txt', f'SIMU_optim_{temperature}degC.txt')


# %% Impedance comparison

fig_mean = plt.figure()
plot_impedance(freq_orig, Z_Orig, figure=fig_mean, label='Meas. Originale', modulus_only=True)
plt.xlim([0,3e3])
plot_impedance(f_tomo, Z_tomo, color=[.5,.5,.5],  label='Simu Tomo + Molding', figure=fig_mean, linewidth=2, modulus_only=True)
fig_mean.savefig('Compare_impedance_tomo.png')


plot_impedance(f_optim, Z_optim, color='k', label='Simu Optim', figure=fig_mean, linewidth=2, modulus_only=True)
fig_mean.savefig('Compare_impedance_optim.png')
plot_impedance(freq_facsim, Z_FacSim, figure=fig_mean, label='Meas. Copy', modulus_only=True)
fig_mean.savefig('Compare_impedance_tot.png')



fig_zoom = plt.figure()
plot_impedance(freq_orig, Z_Orig, figure=fig_zoom, label='Meas. Originale', linewidth=3, modulus_only=True)
plt.xlim([125,410])
ax = fig_zoom.get_axes()
ax[0].set_ylim([27,33])
ax[0].legend(loc='best')
plot_impedance(f_tomo, Z_tomo, color=[.5,.5,.5],  label='Simu Tomo', figure=fig_zoom, linewidth=2, modulus_only=True)
ax[0].legend(loc='best')
fig_zoom.savefig('Zoom_Compare_impedance_tomo.png')
plot_impedance(f_optim, Z_optim, color='k', label='Simu Optim', figure=fig_zoom, linewidth=1, modulus_only=True)
ax[0].legend(loc='best')
fig_zoom.savefig('Zoom_Compare_impedance_optim.png')
plot_impedance(freq_facsim, Z_FacSim, figure=fig_zoom, label='Meas. Copy', modulus_only=True)
ax[0].legend(loc='best')
fig_zoom.savefig('Zoom_Compare_impedance_tot.png')


# %% Resonances characterics comparison

f_orig_new, a_orig_new, Q = find_peaks_measured_impedance(freq_orig, Z_Orig, fmin=45)
f_facSim, a_facSim, Q = find_peaks_measured_impedance(freq_facsim, Z_FacSim, fmin=45)

f_res_optim, a_res_optim,Q  = find_peaks_measured_impedance(f_optim, Z_optim, fmin=45)
f_res_tomo, a_res_tomo, Q = find_peaks_measured_impedance(f_tomo, Z_tomo, fmin=45)

fig_res, ax_res = plt.subplots(2,1)
ax_res[0].plot(f_orig_new, np.zeros_like(a_orig_new), 'x:', label='Meas. Originale', linewidth=2, markersize=10)
ax_res[0].plot(f_orig_new, 20*np.log10(a_res_tomo/a_orig_new), '<:', color=[.5,.5,.5], label='Simu Tomo', linewidth=2, markersize=10)
ax_res[0].grid('on')
ax_res[0].set_ylabel('$\Delta a_i$ [dB]')
ax_res[0].legend()


ax_res[1].plot(f_orig_new, np.zeros_like(f_orig_new), 'x:', label='Orig new', linewidth=2, markersize=10)
ax_res[1].plot(f_orig_new, 1200*np.log2(f_res_tomo/f_orig_new), '<:', color=[.5,.5,.5], label='Simu Tomo', linewidth=2, markersize=10)
ax_res[1].grid('on')
ax_res[1].set_ylabel('$\Delta f_i$ [cents]')
ax_res[1].set_xlabel('Frequence [Hz]')

fig_res.savefig('Compare_resonance_tomo.png')


ax_res[0].plot(f_orig_new, 20*np.log10(a_res_optim/a_orig_new), 'ko:', label='Simu Optim', linewidth=2, markersize=10)
ax_res[1].plot(f_orig_new, 1200*np.log2(f_res_optim/f_orig_new), 'ko:', label='Simu Optim', linewidth=2, markersize=10)
ax_res[0].legend()
fig_res.savefig('Compare_resonance_optim.png')

ax_res[0].plot(f_orig_new, 20*np.log10(a_facSim/a_orig_new), 'x:', label='Meas. Copy', linewidth=2, markersize=10)
ax_res[1].plot(f_orig_new, 1200*np.log2(f_facSim/f_orig_new), 'x:', label='Meas. Copy', linewidth=2, markersize=10)
ax_res[0].legend()
fig_res.savefig('Compare_resonance_tot.png')
