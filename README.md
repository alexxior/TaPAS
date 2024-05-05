# TaPAS
# Theoretical acoustics Plugin -> Artificial Saxophones
## Pomysłodawca: dr hab. Tomasz Pruchnicki
## Autor:        inż. Alexander Stefani
## Konsultacja:  Kamil Kozak

<a target="_blank" href="https://colab.research.google.com/github/alexxior/TaPAS/blob/alex_dev/src/predicator.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a> (a DEV version of ML predicator)

<img src="/tapas_logo.jpg" width="400" height="400">

Idea is to develop an independent add-on (preferable VST plugin) for acoustical physical modelling of different shapes of saxophones to play as an virtual instrument in real-time through 4.x. MIDI controller. We will use open source tools and make a free closed product for artists.

The modelling will be calculated from OpenWinD library, JUCE VST creator and "popsicle" library for Python-JUCE integration.

The GUI can be assisted through Python FreeCADGui, JUCE Qt libraries and using language API for 3D modelling - CadQuery which is supported by FreeCAD.

The next milestone is to simulate all typical woodwind instruments through calculation many combinations of waveguides, throats and nozzles to learn a deep-learing algorithm to predict a physical synthesis of physics of woodwind acoustics, such as transmittance, nonlinearities, types of excitations, special sound production and articullations.

These machine learned results will be used for accelerate future add-on and create an AI predication of specifics of woodwinds.

The project will be used for next generation of physical modelling synths using AI prediction 4.x. Hammond organ nonlinear (AI assisted) synthesis.

Potencial far milestone of this plugin will evolve to independent C++ program, 4.x. full-writen VST, without any "Pythonish-like" libraries, only based on trained AI model, possibly run on some microcontroller or microcomputer (STM32, RaspPi, Google Coral, Nvidia Jetson).

Usage of this project will be also moved to KaRKAS - full trained AI morfing plugin for pipe organ simulation with evolving shapes.