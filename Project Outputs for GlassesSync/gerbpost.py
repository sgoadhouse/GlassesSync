#!/usr/bin/env python

## This is a post-processing step for the Gerber files output by
## Altium. Altium forces you to have a single filename for all layers
## and only an extension to differentiate. This script reads in the
## Altium Designer (AD) .EXTREP file, which is a listing of all Gerber
## output files, and automatically updates the file names with
## descriptor text.
##
## NOTE: Only Gerber files in EXTREP and not NC Drill files, which
## already have a descriptive name.
##
## Run this in the Gerber folder and give it the EXTREP file

# For future Python3 compatibility:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys  
import os
import re
import argparse
import random
import zipfile
import zlib

# Convert HSV scalar (0.0 to 1.0) to RGB (0.0 to 1.0)
# from: https://stackoverflow.com/questions/24852345/hsv-to-rgb-color-conversion
scalar = float # a scale value (0.0 to 1.0)
def hsv_to_rgb( h:scalar, s:scalar, v:scalar ) -> tuple:
    if s:
        if h == 1.0: h = 0.0
        i = int(h*6.0); f = h*6.0 - i
        
        w = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        if i==0: return (v, t, w)
        if i==1: return (q, v, w)
        if i==2: return (w, v, t)
        if i==3: return (w, q, v)
        if i==4: return (t, w, v)
        if i==5: return (v, w, q)
    else: return (v, v, v)


# Pick the next RGB color
def colorPickerRGB():
    # create the color by getting 3 random 16-bit numbers with the lower 8 bits set to 0
    #color = list(map(lambda x: random.randint(0,255)*256, [1]*3))
    #@@@#return list(map(lambda x: int(x*255)*256,hsv_to_rgb(((random.random()*0.75)+0.25), 1.0, 1.0)))

    # comparison color using XOR render mode of gerbv is best when
    # Saturation and Value are 100% (at least on 2023 macOS). So pick
    # a random Hue and convert to RGB. The random Hue value seems to
    # be best if it is near one of the 60/360 segments +/- 8
    # [0-7, 52-67, 112-127, ..., 352-359].
    
    hueA = random.randint(0,15)
    hueB = random.randint(0,5) * 60
    hue = (hueA + hueB - 8) % 360 # modulo so -8 becomes 352
    return list(map(lambda x: int(x*65535),hsv_to_rgb(hue/360.0, 1.0, 1.0)))

# Read the EXTREP Gerber file directory and output an array of its contents
def readExtRep(ExtRepFilepath):
    layers = []
    with open(ExtRepFilepath, 'r') as fp:
        pre = 0
        for line in fp:
            #@@@#m = re.search(r'^\.([A-Za-z0-9]+)\w+(.*)\w*$', line)
            m = re.search(r'^\.([A-Za-z0-9]+)\s+(.*)\s*$', line)
            if (m):
                #@@@#print(line)
                #@@@#print(m.group(2).strip())
                lext = m.group(1)

                # If a layer that should be at the top, insert it instead of append it
                toplayer = re.match(r'^(GM1|GG[0-9]+|GD[0-9]+)$', lext)

                # Pick a color
                color = colorPickerRGB()

                # Trim whitespace from layer name in case re picked up
                # some (it shouldn't)
                layerName = m.group(2).strip()

                if (toplayer):
                    layers.insert(pre, (lext, layerName, color))
                    pre += 1
                else:
                    layers.append((lext, layerName, color))
                                
    return layers

# Concatenate two text files
def concatText(inFileName1, inFileName2, outFileName):
    # Open the source text files
    file1 = open(inFileName1, 'r')
    file2 = open(inFileName2, 'r')

    # Read the contents of the text files
    content1 = file1.read()
    content2 = file2.read()

    # Close the source text files
    file1.close()
    file2.close()

    # Open the destination file
    destination_file = open(outFileName, 'w')

    # Write the concatenated content to the destination file
    destination_file.write(content1 + content2)
    # Close the destination file
    destination_file.close()
    

# Rename the Gerber files based on layers array read from EXTREP file.
#
# layers - array from EXTREP file
#
# commonFilename - filename, without extension of EXTREP file -
#                  expected to be same for all layer files
#
# oshpark - OSH Park wants the original extensions from Altium, so do not rename
#           if oshpark is True
#
def renameGerbers(layers, commonFilename, oshpark=False, debug=False):
    lcnt = len(layers)

    newLayers = []

    layerCount = 2 # count top and bottom
    for layer in layers:
        # Count the number of inner layers so know what layer number to add for the bottom layer
        m=re.search(r'^G([0-9]+)$', layer[0])
        if (m):
            layerCount+=1

    # See if just Keep-Out or Thieving Mask (GM16) and Keep-Out (GKO)
    tm = 0
    ko = 0
    for index, layer in enumerate(layers):
        if ('GM16' == layer[0]):
            tm = index
        if ('GKO' == layer[0]):
            ko = index

    # If just Keep-Out, rename .GKO file to Thieving Mask
    if (ko and not tm):
        for index, layer in enumerate(layers):
            if (layer[0] == 'GKO'):
                layers[index] = (layer[0], 'Thieving_Mask', layer[2])

    # If Thieving Mask and Keep-Out, combine them and remove GKO from layer list
    if (ko and tm):
        # Concatenate the text files into GM16 file
        if not debug: concatText(commonFilename + '.GM16', commonFilename + '.GKO', commonFilename + '.GM16')
        # Remove GKO from layers list
        layers.pop(ko)
        # Delete the GKO file
        if not debug: os.remove(commonFilename + '.GKO')

            
    for layer in layers:
        lcnt -= 1

        #@@@#print("{}: {}".format(lcnt, layer[0]))
        
        # target filename = common name + extension
        target = commonFilename + '.' + layer[0]

        if not oshpark:
            # Create new filename = common name + layer number (if electrical) + Layer Name + '.gbr'
            #
            # Adding layer number for electrical layers in filename for sorting purposes. If single digit number, add a 0
            m=re.search(r'^G([0-9]+)$', layer[0])
            if (m):
                # Inner electrical layer - need to add 1 to get proper layer number (with Top as 1)
                layerNum = int(m.group(1))+1
                sorttext = f"L{layerNum:02d}_"
            elif (layer[0] == 'GTL'):
                sorttext = "L01_"
            elif (layer[0] == 'GBL'):
                sorttext = f"L{layerCount:02d}_"
            elif (re.search(r'^GD([0-9]+)$', layer[0])):
                # Drill Drawings - add extension as a layner number in order to differentiate if have blind vias / multiple lam cycles
                sorttext = layer[0] + '_'            
            else:
                # Only add a layer number for the electrical layers (.GTL, .G1 .. .GXX, .GBL)
                sorttext = ""

            #newName = commonFilename + '_' + sorttext + layer[1] + '.' + layer[0]
            newName = commonFilename + '_' + sorttext + layer[1] + '.' + 'gbr'

        else:
            # Keep filename sthe same but setup newName so resulting code still works
            newName = commonFilename + '.' + layer[0]
            
        # Replace all white space in new layer name with '_' in case
        # Fab vendor can't handle spaces in filename (come-on! This is
        # 2020 but computers still do not handle spaces in filenames
        # too well)
        newName = re.sub(r'\s+', '_', newName)

        newLayers.append(layer + (newName,))

        print('Renaming {} to {}'.format(target, newName))

        #@@@# Need to make this more cross-OS portable
        #@@@# Windows may require changing to the directory first and then stripping out directory name from target & newName
        #@@@# Windows may also require checking if file exists first
        #@@@# Need to add error capture try/error
        if not debug:
            # set debug parameter to True if debugging and do not want the rename action
            os.rename(target,newName)

    return newLayers

# Add NC Drill Files to Layer list so can get added to the GVP project file
def addNCDrills(layers, ExtRepFilepath):

    (lead,filename) = os.path.split(ExtRepFilepath)

    if (lead == None or lead == ''):
        lead = '.'
    
    listOfFiles = os.listdir(lead)
    (prefix,bb) = filename.split(' Gerber.EXTREP')
    #@@@#print("'" + prefix + "'")
    pre = 1                           # insert NC Drill just after the Board Outline 
    for file in listOfFiles:
        #@@@#print(file)
        if(re.search(r'^{} NC Drill-[^.]+\.T'.format(prefix), file)):
            #@@@#print(file)

            # Pick a color
            color = colorPickerRGB()
            
            # Add to the layer list with extension of NCDRILL which will be used to recognize it as a NC Drill file
            layers.insert(pre, ('NCDRILL', 'NC Drill', color, file))
            pre += 1


# Output layers into the GVP file
def outputGVP(layers, outfile):

    # Output file for writing - overwrite if filename exists
    with open(outfile, 'w') as f:

        # Start with the preamble:
        f.write('(gerbv-file-version! "2.0A")\n')

        lcnt = len(layers)
    
        for layer in layers:
            lcnt -= 1
            (lead,filename) = os.path.split(layer[3])
            f.write('(define-layer! {} (cons \'filename "{}")\n'.format(lcnt,filename))
            f.write('\t(cons \'visible #{})\n'.format((lcnt > 0) and 'f' or 't'))
            f.write('\t(cons \'color #({} {} {}))\n'.format(*layer[2]))
            if (layer[0] == 'NCDRILL'):
                # NC Drill needs some extra parameters output to GVP
                f.write('\t(cons \'attribs (list (list \'autodetect \'Boolean 1) (list \'zero_supression \'Enum 1) (list \'units \'Enum 1) (list \'digits \'Integer 3)))\n')
            f.write(')\n')

        # output tail end
        f.write('(define-layer! -1 (cons \'filename "")\n')
        f.write('\t(cons \'color #(0 0 0))\n')    # background color
        f.write(')\n')
        f.write('(set-render-type! 0)\n')

# Output layers into the GVP file that can be easily changed to compare against a similar set of Gerber files in a different folder
def outputGVPdiff(layers, outfile):

    # Output file for writing - overwrite if filename exists
    with open(outfile, 'w') as f:

        # Start with the preamble:
        f.write(';; Global Replace ../OLD-DIR with the relative path to the folder with Gerber files to compare against\n')
        f.write('(gerbv-file-version! "2.0A")\n')

        lcnt = len(layers)*2
    
        for layer in layers:
            (lead,filename) = os.path.split(layer[3])
            for cnt in [0, 1]:
                lcnt -= 1
                if cnt > 0:
                    f.write('(define-layer! {} (cons \'filename "../OLD-DIR/{}")\n'.format(lcnt,filename))
                else:
                    f.write('(define-layer! {} (cons \'filename "{}")\n'.format(lcnt,filename))
                f.write('\t(cons \'visible #{})\n'.format((lcnt > 0) and 'f' or 't'))
                f.write('\t(cons \'color #({} {} {}))\n'.format(*layer[2]))
                if (layer[0] == 'NCDRILL'):
                    # NC Drill needs some extra parameters output to GVP
                    f.write('\t(cons \'attribs (list (list \'autodetect \'Boolean 1) (list \'zero_supression \'Enum 1) (list \'units \'Enum 1) (list \'digits \'Integer 3)))\n')
                f.write(')\n')

        # output tail end
        f.write('(define-layer! -1 (cons \'filename "")\n')
        f.write('\t(cons \'color #(0 0 0))\n')    # background color
        f.write(')\n')
        f.write('(set-render-type! 1)\n')

# Create a ZIP file
def createZIP(layers, additional, outZipfile):

    print('\nCreating ZIP Archive named: {}\n'.format(outZipfile))

    # Output ZIP file for writing - overwrite if filename exists
    # Use basic compression (ZIP_DEFLATED)
    with zipfile.ZipFile(outZipfile, mode='w', compression=zipfile.ZIP_DEFLATED) as f:

        for layer in layers:
            (lead,filename) = os.path.split(layer[3])
            f.write(filename)

        if additional is not None and len(additional) > 0:
            for file in additional:
                f.write(file)
        
def main(extrepfilepath, gvpoutpath, oshpark):  
    if not os.path.isfile(extrepfilepath):
        print("File path {} does not exist. Exiting...".format(extrepfilepath))
        sys.exit()

    filename, fileext = os.path.splitext(extrepfilepath)
    if (fileext.lower() != '.extrep'):
        print("Argument must be the .EXTREP file and not {}. Exiting...".format(extrepfilepath))
        sys.exit()

    # NOTE: filename should also be the filename of every Gerber layer
        
    layers = readExtRep(extrepfilepath)
    # renameGerbers() also combines Thieving Mask and Keep-Out, if they exist
    newLayers = renameGerbers(layers, filename, oshpark=oshpark, debug=False) 
    addNCDrills(newLayers, extrepfilepath)
    
    # Go through layers in reverse order
    newLayers.reverse()

    outputGVP(newLayers, gvpoutpath)

    gvpoutfile, gvpoutext = os.path.splitext(gvpoutpath)
    gvpDiffoutpath = gvpoutfile + "_DIFF" + gvpoutext
    outputGVPdiff(newLayers, gvpDiffoutpath)

    # Create a ZIP File and include the GVP files
    createZIP(newLayers, (gvpoutpath, gvpDiffoutpath), filename.replace(' ', '_') + ".zip")

if __name__ == '__main__':  
    parser = argparse.ArgumentParser(description='Rename Gerber files output by Altium Designer based on .EXTREP layer list file and create gerbv .gvp project file.')
    #@@@#parser.add_argument('--ziponly', '-z', help='only perform the zip of files - this only works if files have already been renamed')
    parser.add_argument('--oshpark', '-x', action='store_true', help='leave extensions as OSH Park uses the original extensions to determine layers', default=False)

    parser.add_argument('extrepfile', help='pathname to .EXTREP input file')
    parser.add_argument('gvpoutfile', help='pathname to output .gvp project file')
    
    # Print help if no options are given on the command line
    if (len(sys.argv) <= 2):
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    main(args.extrepfile, args.gvpoutfile, args.oshpark)
