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

## Design Output Files

In addition to the source files, there should be various output files
in PDF, Gerber and other formats. They are located under the folder,
[Project Outputs for GlassesSync](./Project%20Outputs%20for%20GlassesSync).

## Before cloning the GIT repository

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

## UVaND-Libraries submodule

The UVaND-Libraries submodule contains a Altium component database,
symbols and footprints library that were used in the design. This is
sourced from gitlab.cern.ch which is likely not accessible to the
majority of github users. However, it is not needed because Altium
copies over the symbol and footprints for any symbol added to the
schematic and embeds these parts within the SchDoc and PcbDoc files
available in this repo. So any git warnings about not being able to
access this submodule can be safely ignored.

## Software

### Preparation of the RP2350

#### Install CircuitPython

Purchase a [Adafruit Feather RP2350 with HSTX Port and 8MB PSRAM](https://www.adafruit.com/product/6130). They can often be
found at Digi-Key at [Adafruit RP2350 Feather
6130](https://www.digikey.com/short/nft7f7z4). Install a stable
version of [CircuitPython for Feather RP2350 by
Adafruit](https://circuitpython.org/board/adafruit_feather_rp2350/). As
of this writing, the stable version is
[v10.3.2](https://downloads.circuitpython.org/bin/adafruit_feather_rp2350/en_US/adafruit-circuitpython-adafruit_feather_rp2350-en_US-10.3.2.uf2). Full
instructions on how to update the microcontroller board can be found
[here](https://learn.adafruit.com/adafruit-feather-rp2350/install-circuitpython-2). The basic notes are:
- Hold the `Boot` button on the board
- While continuing to hold the button, plug a USB cable between your computer and the board
- Release the button and look for a new USB Drive named `RP2350`
- drag and drop the downloaded CircuitPython `.uf2` file into this USB Drive
- the board will update, disconnect itself from USB and reconnect as a USB Drive named `CIRCUITPY`

#### Install CircuitPython Libraries

The code requires some libraries from Adafruit. Download the
[CircuitPython Library Bundle](https://circuitpython.org/libraries)
that corresponds to the major version of CircuitPython that was
installed. As of this writing, that is
[adafruit-circuitpython-bundle-10.x-mpy-20261112.zip](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20261112/adafruit-circuitpython-bundle-10.x-mpy-20261112.zip). After
downloading, uncompress it / Extract All.

From within the extracted folder, navigate to the `lib` folder and
copy `adafruit_pioasm.mpy` and `neopixel.mpy` files into the `lib` folder on
the `CIRCUITPY` USB Drive.

#### Install the code

Once all of the above steps are performed successfully, copy the file
`code.py` under `Software/Main` to the `CIRCUITPY` USB Drive. Once the
write is complete, the code should start running.

## Usage

If the code is running correctly, the RED LED beside the USB-C
connector on the RP2350 microcontroller board will flash when a sync
pulse is sent out. At the same time, the RGB Neopixel with slowly
pulse Green. This will start automatically when power is applied to
the board.

If the RED LED does not light and the Neopixel flashes Red, then there
is an error. Connect to the USB Serial port to see any available error
codes. Will likely need to restart after connecting to the serial port
by pressing and releasing the `Reset` button on the microcontroller
board.


