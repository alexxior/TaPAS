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
This file explore the relationship between pitch and the resonance frequency of the lips,
for the trumpet E0925 from the museum 'Cité de la musique musique-Philharmonie de Paris', and build by the Besson Company.
The project build around this trumpet is detailed in: https://inria.hal.science/hal-04352706
It has been presented in:
- CFA 2022: https://hal.science/hal-03848341
- Vienna Talks 2022: https://inria.hal.science/hal-03842072
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os


from openwind import InstrumentGeometry, InstrumentPhysics, TemporalSolver, Player, FrequentialSolver
from openwind.temporal import RecordingDevice
from openwind.technical.temporal_curves import ADSR
from openwind.temporal.utils import export_mono

import parselmouth

plt.close('all')

# %% Implementation of scaled lips model
simu_duration = 0.5
temperature = 25
losses = False#'diffrepr'#
mesh_options = dict(order = 6, l_ele = 2e-2)


gamma_amp = 0.5 # the amplitude of gamma, the dimensionless supply pressure
transition_time = 1e-2 # the characteristic time of the time eveolution of gamma
gate_duration = 1
gamma_time = ADSR(0, gate_duration, gamma_amp, transition_time, transition_time, 1,
                  transition_time) # the time evolution of gamma
zeta = 0.1 # the value of zeta, the "reed" opening dimensionless paramters
kappa = 1e-3
Q_factor = 33
dimless_lips = {"excitator_type" : "Reed1dof_scaled",
                "gamma" : gamma_time,
                "zeta": zeta,
                "kappa": kappa,
                "pulsation" : 2*np.pi*2700, #in rad/s
                "qfactor": Q_factor,
                "model" : "outwards",
                "contact_stifness": 0,#1e4,
                "contact_exponent": 4,
                "opening" : 5e-4, #in m
                "closing_pressure": 5e3 #in Pa
                }
brass_player = Player(dimless_lips)



# %% Instanciation of the simulation object


# We instanciate the other objects necessary to compute the sound
instrument = 'Actual_Copy_E0925.txt'
# instrument = 'Besson_E0925_actual_copy_cone_1cm.txt'
my_geom = InstrumentGeometry(instrument) # the geometry of the instrument
my_phy = InstrumentPhysics(my_geom, temperature, brass_player, losses)
my_temp_solver = TemporalSolver(my_phy, **mesh_options)


# %%
print('Freq. Domain Simulation')
fsimu=np.arange(20,2001,1)
my_phy_4_freq = InstrumentPhysics(my_geom, temperature, Player(), losses)
my_freq_domain = FrequentialSolver(my_phy_4_freq, fsimu, compute_method='modal',
                                   **mesh_options)
my_freq_domain.solve()
f_res = my_freq_domain.resonance_frequencies(30)

# my_freq_domain.plot_impedance(figure=fig)

# my_freq_domain.write_impedance(f'Impedance_actual_copy_besson_{temperature}degC_ZKlosses_FEM_cone1cm.txt')

# %% Change the value of lips frequency

lips_freq = [300]
# lips_freq = np.arange(20, 1220, 20)
pitch_tot = list()

# plt.figure()
# plt.grid()
# plt.xlabel('Time [s]')
# plt.ylabel('Bell flow [m/s]')

save_path = './sound_simu'
Path(save_path).mkdir(parents=True, exist_ok=True)
existing_files = [f for f in os.listdir(save_path) if os.path.isfile(os.path.join(save_path, f))]

for f_lips in lips_freq:
    print(f"\n *********\n Freq of lips: {f_lips}Hz")
    if losses:
        save_name = 'Lossy'
    else:
        save_name = 'Lossless'
    save_name += f'_Besson_Actual_Copy_flips_{f_lips:.0f}Hz_{simu_duration*1e3:.0f}ms.wav'
    if save_name in existing_files:
        snd = parselmouth.Sound(os.path.join(save_path, save_name))
    else:
        brass_player.update_curve('pulsation', 2*np.pi*f_lips)
        rec = RecordingDevice()
        my_temp_solver.reset()
        my_temp_solver.run_simulation(simu_duration, callback=rec.callback)
        flow_bell = rec.values['bell_radiation_flow']
        time = rec.ts
        export_mono(os.path.join(save_path, save_name), np.diff(flow_bell)/np.diff(time), np.array(time[:-1]))
        Sr = 1/my_temp_solver.get_dt()
        snd  = parselmouth.Sound(flow_bell, Sr)

    # plt.close('all')
    # plt.plot(snd.xs(), snd.values.T)
    snd_part = snd.extract_part(from_time=0.35, to_time=.5, preserve_times=True)

    pitch = snd_part.to_pitch(pitch_ceiling=2000)#pitch_floor=20, pitch_ceiling=8000)
    pitch_values = pitch.selected_array['frequency']
    pitch_values[pitch_values==0] = np.nan
    pitch_tot.append(np.nanmean(pitch_values))
# %%
plt.figure()
plt.hlines(f_res, 0, max(lips_freq), 'k', label='Resonance', linewidth=.2)
plt.plot(lips_freq, pitch_tot, '*-', label='Simulations', linewidth=1.5)
plt.plot(np.linspace(0,1.1*max(lips_freq),100), np.linspace(0,1.1*max(lips_freq),100), 'k--', label='x=y')
plt.xlim((0, max(lips_freq)))
plt.ylim((0, 1.1*max(lips_freq)))
# plt.grid()
plt.xlabel('Lips frequency [Hz]')
plt.ylabel('Sounding Frequency [Hz]')
plt.legend()
# plt.savefig('Lossy_Simulated-pitch_vs_flips_resonances.png')
# plt.savefig('Lossy_Simulated-pitch_vs_flips_resonances.pdf')


def draw_spectrogram(spectrogram, dynamic_range=100):
    X, Y = spectrogram.x_grid(), spectrogram.y_grid()
    sg_db = 10 * np.log10(spectrogram.values)
    plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
    plt.ylim([spectrogram.ymin, spectrogram.ymax])
    plt.xlabel("time [s]")
    plt.ylabel("frequency [Hz]")



spectrogram = snd.to_spectrogram(window_length=0.03, maximum_frequency=8000)
plt.figure()
draw_spectrogram(spectrogram)
