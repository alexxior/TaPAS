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
This file simulate the sound for specific lips frequency of the trumpet E0925
from the museum 'Cité de la musique musique-Philharmonie de Paris', and build by the Besson Company.
The project build around this trumpet is detailed in: https://inria.hal.science/hal-04352706
It has been presented in:
- CFA 2022: https://hal.science/hal-03848341
- Vienna Talks 2022: https://inria.hal.science/hal-03842072
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


from openwind import InstrumentGeometry, InstrumentPhysics, TemporalSolver, Player, FrequentialSolver
from openwind.temporal import RecordingDevice
from openwind.technical.temporal_curves import ADSR
from openwind.temporal.utils import export_mono

import parselmouth

plt.close('all')

# %% Implementation of scaled lips model

temperature = 25
mesh_options = dict(order = 6, l_ele = 2e-2)

gamma_amp = 0.5 # the amplitude of gamma, the dimensionless supply pressure
transition_time = 1e-2 # the characteristic time of the time eveolution of gamma
duration = 1.45
gamma_time = ADSR(0, duration, gamma_amp, transition_time, transition_time, 1,
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
my_geom = InstrumentGeometry(instrument) # the geometry of the instrument
my_phy = InstrumentPhysics(my_geom, temperature, brass_player, 'diffrepr')
my_temp_solver = TemporalSolver(my_phy, **mesh_options)



# %% Change the value of lips frequency

lips_freq =[60,150,230, 300, 350, 420, 500, 580, 660, 740, 840, 920, 980, 1060, 1160]


Path("./stable_sound_simu").mkdir(parents=True, exist_ok=True)

for f_lips in lips_freq:
    print(f"Freq of lips: {f_lips}Hz")
    brass_player.update_curve('pulsation', 2*np.pi*f_lips)
    rec = RecordingDevice()
    my_temp_solver.reset()
    print(my_temp_solver.get_dt())
    my_temp_solver.run_simulation(1.5, callback=rec.callback)
    flow_bell = rec.values['bell_radiation_flow']
    time = rec.ts
    export_mono(f'stable_sound_simu/Lossy_Stable_Sound_Besson_Actual_Copy_flips_{f_lips:.0f}Hz.wav',
                np.diff(flow_bell)/np.diff(time), np.array(time[:-1]))
