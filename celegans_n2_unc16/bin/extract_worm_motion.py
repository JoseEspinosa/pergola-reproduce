#!/usr/bin/env python
#  Copyright (c) 2014-2017, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2017, Jose Espinosa-Carrasco and the respective authors.
#
#  This file is part of Pergola.
#
#  Pergola is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pergola is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################
### Jose Espinosa-Carrasco NPMMD/CB-CRG Group. May 2016                   ###
#############################################################################
### Reads mat lab files downloaded from the Wormbehavior DB               ###
### (http://wormbehavior.mrc-lmb.cam.ac.uk/). Each file contains several  ###
### features extracted from C.elegans video trackings.                    ### 
### Read intervals of direction followed by the worn in space             ###
#############################################################################

# Loading libraries
from argparse import ArgumentParser
from scipy.io  import loadmat
import h5py
from time import strptime
from calendar import timegm
from sys import stderr, exit
import numpy as np
from csv import writer
from os.path import basename

parser = ArgumentParser(description='File input arguments')
parser.add_argument('-i','--input', help='Worms data hdf5 format matlab file', required=True)

args = parser.parse_args()

print ("Input file: %s" % args.input)
print >> stderr, "Input file: %s" % args.input

# Input files
input_file =  args.input
file_name = basename(input_file).split('.')[0]
file_name = file_name.replace (" ", "_")

f = h5py.File(input_file)

### INFO
sex_r = f['info']['experiment']['worm']['sex']
sex = str(''.join(unichr(c) for c in sex_r))

habituation_r = f['info']['experiment']['worm']['habituation']
habituation = str(''.join(unichr(c) for c in habituation_r))

# annotations (empty)
annotations_r = f['info']['experiment']['environment']['annotations']
annotations = str(''.join(c.astype(str) for c in annotations_r))

# info/experiment/worm/genotype
genotype_r = f['info']['experiment']['worm']['genotype'] #type u2
genotype = str(''.join(unichr(c) for c in genotype_r))

# /info/experiment/worm/strain
strain_r = f['info']['experiment']['worm']['strain']
strain = str(''.join(unichr(c) for c in strain_r))

# age worm
# /info/experiment/worm/age
age_r = f['info']['experiment']['worm']['age'] #type u2
age = str(''.join(unichr(c) for c in age_r))

# /info/experiment/environment/food
food_r = f['info']['experiment']['environment']['food'] #type u2
food = str(''.join(unichr(c) for c in food_r))

# /info/experiment/environment/timestamp
timestamp_r = f['info']['experiment']['environment']['timestamp'] #type u2
timestamp = str(''.join(unichr(c) for c in timestamp_r))

# HH:MM:SS.mmmmmm
my_date_object = strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
unix_time = timegm(my_date_object) # utc based # correct!!!

# /info/video/length/time
time_recorded_r = f['info']['video']['length']['time']
time_recorded = time_recorded_r[0][0]

# /info/video/length/frames
frames_r = f['info']['video']['length']['frames']
frames = frames_r[0][0] 

fps_r = f['info']['video']['resolution']['fps']
fps = fps_r[0][0]

motion_keys = ['forward', 'backward', 'paused']

def list_from_ref (refs_obj):
    list_v = list()
    
    for r in refs_obj:
        list_v.append(f[r[0]][0][0])   

    return (list_v)

for motion_k in sorted(motion_keys):
    try:
        start_r = f['worm']['locomotion']['motion'][motion_k]['frames']['start']
        end_r = f['worm']['locomotion']['motion'][motion_k]['frames']['end']
    except KeyError:
        raise KeyError ("Motion field %s is corrupted and can not be retrieved from hdf5 file"
                        % (motion_k))
    
    start = list_from_ref (start_r)
    end = list_from_ref (end_r)

    fh = open(file_name + "." + motion_k + ".csv",'wb')

    fh.write("#genotype;%s\n" % genotype)
    fh.write("#strain;%s\n" % strain)
    fh.write("#age;%s\n" % age)
    fh.write("#habituation;%s\n" % habituation)
    fh.write("#food;%s\n" % food)
    fh.write("#unix_time;%s\n" % unix_time)
    fh.write("#time_recorded;%s\n" % time_recorded)
    fh.write("#frames;%s\n" % frames)
    fh.write("#fps;%s\n" % fps)
    fh.write("#annotations;%s\n" % annotations)

    writer_out = writer(fh, dialect = 'excel-tab')
    
    # header
    writer_out.writerow(['frame_start', 'frame_end', 'value', 'direction'])
    
    for i in range(0, len(start)):
        writer_out.writerows([[start[i], end[i], 1000, motion_k]])

    fh.close()
