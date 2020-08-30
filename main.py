#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 22:09:41 2020
@author: aguemes
"""


import time
from merlin import MERLIN


def main():

    postprocesser = MERLIN()
    
    postprocesser.generate_readable_files(
        delete_files=False, 
        directory_input=directory_input, 
        directory_output=directory_output, 
        geometry='3D', 
        method='nearest',
        resolution_x=0.1, 
        resolution_y=0.1, 
        resolution_z=0.1,
        save_mesh=True, 
        save_data=True, 
        save_data_type='matlab'
    )

    postprocesser.compute_statistics()

    return


if __name__ == '__main__':

    directory_input = '/home/goku/Documents/PALABOS/2-Re5000_OutflowNeuVel_SpongeZone_ConeGrid/tmp7'
    directory_output = '/storage1/palabos_simulations/jets/2-Re5000_OutflowNeuVel_SpongeZone_ConeGrid/data3d/'

    main()

        