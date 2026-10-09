# GlassesSync

A custom "FeatherWing" daughterboard to provide 3.3V buffered logic
input and output over 3.5mm TRS (tip-ring-sleeve) barrel-style
connectors. Should be compatible with any [Adafruit Feather
microcontroller](https://learn.adafruit.com/adafruit-feather) but was
targeted for use with the [Adafruit RP2350
Feather](https://www.adafruit.com/product/6130). The Programmable IO
(PIO) of the RP2350 will be used to send a custom sync signal. The
older [RP2040](https://www.adafruit.com/product/4884) also has a PIO
peripheral and could possibly be used.

The Altium Designer v26 (AD26) schematic and layout tool was used to
design the board and the source files here can only be read through
Altium Designer. Most versions of AD should be able to view the
project files. You can also use the [Altium Designer
Viewer](https://www.altium.com/altium-designer-viewer) to view these
files.

In addition to the source files, there should be various output files
in PDF, Gerber and other formats. They are located under the folder,
`Project Outputs for GlassesSync`.

# Before cloning the GIT repository

Make sure that ...

1) The setup is ready for large filesystems on github

```
$ git lfs install
```

1) You have git version 2.13.0 (or later) installed

```
$ git version
git version 2.13.0
```

1) Verify that you have git-lfs version 2.1.1 (or later) installed

```
$ git-lfs version
git-lfs/2.1.1
```

# UVaND-Libraries submodule

The UVaND-Libraries submodule contains a Altium component database,
symbols and footprints library that were used in the design. This is
sourced from gitlab.cern.ch which is likely not accessible to the
majority of github users. However, it is not needed because Altium
copies over the symbol and footprints for any symbol added to the
schematic and embeds these parts within the SchDoc and PcbDoc files
available in this repo. So any git warnings about not being able to
access this submodule can be safely ignored.

# Usage

nothing yet ...


