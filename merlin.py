#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 22:09:41 2020
@author: aguemes
"""


import os
import re
import sys
import vtk
import numpy as np
import multiprocessing
import scipy.io as sio
import dask.array as da
from dask import delayed
import matplotlib.pyplot as plt
from scipy.interpolate import griddata, Rbf
import vtk.util.numpy_support as numpy_support


class MERLIN():

    def __init__(self, flow_type='jet'):

        self.flow_type = flow_type

        print('Initializing Palabos postprocesser')

        return


    def compute_statistics(self):

        print('Starting computation of statistics')

        filenames = [os.path.join(self.directory_output, 'mat', filename) for filename in os.listdir(os.path.join(self.directory_output, 'mat'))]

        for filename in filenames:

            data = sio.loadmat(filename)

            print(data['u'].shape)

            print(filename)

            plt.contourf(np.squeeze(data['u'][:,:,90]))
            plt.axis('equal')
            plt.savefig('test.png', dpi=600)
            kjbk

        return


    def dask_interpolation(self, X, Y, Z, U, xv, yv, zv, method='linear'):
        
        # make dask arrays
        dask_xyzu = da.from_array((X, Y, Z, U), chunks=(4, "auto"), name="dask_in")
        
        dask_in_xx = dask_xyzu[0,:]
        dask_in_yy = dask_xyzu[1,:]
        dask_in_zz = dask_xyzu[2,:]
        dask_in_uu = dask_xyzu[3,:]
        # make dask arrays
        dask_xyz = da.from_array((xv, yv, zv), chunks=(3, xv.shape[0], xv.shape[1], xv.shape[2]), name="dask_all")
  
        dask_xx = dask_xyz[0,:,:,:]
        dask_yy = dask_xyz[1,:,:,:]
        dask_zz = dask_xyz[2,:,:,:]

        def gd_wrapped(x1, y1, z1, newarr, xx, yy, zz):
            # note: linear and cubic griddata impl do not extrapolate
            # and therefore fail near the boundaries... see RBF interp instead
           
            gd_zz = griddata((x1, y1, z1), newarr.ravel(),
                                    (xx, yy, zz),
                                    method='nearest')
            return gd_zz
            # gd_zz = Rbf(x1, y1, z1, newarr.ravel(),function='linear')
            # return gd_zz(xx, yy, zz)

        gd_chunked = [delayed(gd_wrapped)(x1, y1, z1, newarr, xx, yy, zz) for \
                    x1, y1, z1, newarr, xx, yy, zz \
                    in \
                    zip(dask_in_xx.to_delayed().flatten(),
                        dask_in_yy.to_delayed().flatten(),
                        dask_in_zz.to_delayed().flatten(),
                        dask_in_uu.to_delayed().flatten(),
                        dask_xx.to_delayed().flatten(),
                        dask_yy.to_delayed().flatten(),
                        dask_zz.to_delayed().flatten())]

        gd_out = delayed(da.concatenate)(gd_chunked, axis=0)
        
        gd1 = gd_out.compute()

        assert gd1.shape == xv.shape

        return gd1


    def generate_readable_files(self, delete_files=False, directory_input='input', directory_output='output', geometry='3D', method='nearest', resolution_x=0.1, resolution_y=0.1, resolution_z=0.1, save_mesh=True, save_data=True, save_data_type='matlab'):

        print('Starting processing of LBM files')

        self.delete_files = delete_files
        self.directory_input = directory_input
        self.directory_output = directory_output
        self.dx = resolution_x
        self.dy = resolution_y
        self.dz = resolution_z
        self.geometry = geometry
        self.method = method
        self.save_data = save_data
        self.save_data_type = save_data_type
        self.save_mesh = save_mesh

        filenames = os.listdir(self.directory_input)

        timestamps = sorted(
            [
                list(
                    filter(re.compile(da).search, filenames)) for da in sorted(list(set([d.split('/')[-1].split('-')[0] for d in filenames if d.__contains__('.vti')]))
                )
            ]
        )

        if len(timestamps) == 0:

            print('There is not any file to be precessed. Program exiting.')
            sys.exit(0)

        self.grid_levels = sorted(
            list(
                set(
                    [
                        int(filename.split('/')[-1].split('-')[1][-3:]) for filename in timestamps[0] if filename.__contains__('.vti')
                    ]
                )
            )
        )

        if self.geometry == '2D':

            self.read_2D()

        if self.geometry == '3D':

            for timestamp in timestamps:

                self.read_3D(timestamp)

        return


    def read_2D(self, filenames_input):

        print('This function is pending to be built.')
        print('Contact guemes.turb@gmail.com for development status.')

        return


    def read_3D(self, filenames_input):

        timestamp = filenames_input[0].split('-')[0]

        if len(filenames_input) == 22849:

            print(f'The timestamp {timestamp} is ready to post-process')

            filename_output = os.path.join(
                '/'.join(self.directory_output.split('/')[:-1]), 
                'mat', 
                timestamp + '.mat'
            )
            
            mesh_output = os.path.join(
                '/'.join(self.directory_output.split('/')[:-1]), 
                'mat', 
                'mesh.mat'
            )

            if not os.path.exists(filename_output):

                print(f'Generating file {filename_output:s}')

                X = []
                Y = []
                Z = []
                U = []
                V = []
                W = []
                P = []

                for level in self.grid_levels:

                    print(f'Reading level {level:03d} for file {filename_output:s}')

                    regex = re.compile(f'{timestamp}-g{level:03}')

                    blocks = sorted(
                        [
                            os.path.join(
                                self.directory_input, 
                                filename_input
                            ) for filename_input in filenames_input if re.search(regex, filename_input)
                        ]
                    )

                    pool = multiprocessing.Pool(processes=64)
                    result = pool.map(self.read_blocks, blocks)
                    result = np.array(result, dtype=object)
                    pool.close()
                    pool.join()

                    X = np.concatenate((X, np.concatenate(result[:,0], axis=0)), axis=0)
                    Y = np.concatenate((Y, np.concatenate(result[:,1], axis=0)), axis=0)
                    Z = np.concatenate((Z, np.concatenate(result[:,2], axis=0)), axis=0)
                    U = np.concatenate((U, np.concatenate(result[:,3], axis=0)), axis=0)
                    V = np.concatenate((V, np.concatenate(result[:,4], axis=0)), axis=0)
                    W = np.concatenate((W, np.concatenate(result[:,5], axis=0)), axis=0)
                    P = np.concatenate((P, np.concatenate(result[:,6], axis=0)), axis=0)


                print(f'Files read for {filename_output:s}')

                x = np.linspace(
                    X.min(), 
                    X.max(), 
                    int(
                        np.floor(
                            (
                                X.max() - X.min()
                            ) / self.dx
                        )
                    )
                )
                
                y = np.linspace(
                    Y.min(), 
                    Y.max(), 
                    int(
                        np.floor(
                            (
                                Y.max() - Y.min()
                            ) / self.dy
                        )
                    )
                )
                
                z = np.linspace(
                    Z.min(), 
                    Z.max(), 
                    int(
                        np.floor(
                            (
                                Z.max() - Z.min()
                            ) / self.dz
                        )
                    )
                )

                xv, yv, zv = np.meshgrid(x, y, z)

                points = np.concatenate(
                    (
                        np.expand_dims(X, axis=1), 
                        np.expand_dims(Y, axis=1), 
                        np.expand_dims(Z, axis=1)
                    ), 
                    axis=1
                )

                u = griddata(points, U, (xv, yv, zv), method=self.method)
                v = griddata(points, V, (xv, yv, zv), method=self.method)
                w = griddata(points, W, (xv, yv, zv), method=self.method)
                p = griddata(points, P, (xv, yv, zv), method=self.method)
        
                if self.save_data:

                    if self.save_data_type == 'matlab':

                        self.save_data_matlab_3D(u,v,w,p,filename_output)
                    
                    elif self.save_data_type == 'tfrecords':

                        self.save_data_tfrecords_3D(u,v,w,p,filename_output)

                    else:

                        print('The requested format is not available. \n Contact support service for implementation. Program exiting.')

                        sys.exit(0)
                
                if (self.save_mesh) and (not os.path.exists(mesh_output)):

                    if self.save_data_type == 'matlab':

                        self.save_mesh_matlab_3D(u,v,w,p,filename_output)
                    
                    elif self.save_data_type == 'tfrecords':

                        self.save_mesh_tfrecords_3D(u,v,w,p,filename_output)

                    self.save_mesh_3D(xv, yv, zv, mesh_output)
            
            else:

                print(f'{filename_output:s} is already generated')

            if self.delete_files:

                pool = multiprocessing.Pool(processes=64)
                pool.map(self.remove_files, filenames_input)
                pool.close()
                pool.join()

                print(f'Files with .vti extension for {filename_output:s} have been removed')
        
        else:

            print(f'The timestamp {timestamp} is not ready to post-process')

        return


    def read_blocks(self, block):
        
        reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName(block)
        reader.Update()
        image = reader.GetOutput()

        """
            Extract the vector quantities
        """

        # Get the data dimensions (note that since we are working with a 2D simulation we add an extra dimension at the end to account for the two vectors)

        dim = image.GetDimensions()
        vec = list(dim)
        vec = [i-1 for i in dim]
        vec.append(3)

        # Transform the vtk information into numpy arrays

        velocity = numpy_support.vtk_to_numpy(image.GetCellData().GetArray('velocity'))
        u = velocity.reshape(vec,order='F')[:,:,:,0]
        v = velocity.reshape(vec,order='F')[:,:,:,1]
        w = velocity.reshape(vec,order='F')[:,:,:,2]


        """
            Extract the scalar quantities
        """

        # Get the data dimensions

        dim = image.GetDimensions()
        vec = list(dim)
        vec = [i-1 for i in dim]

        # Transform the vtk information into numpy arrays

        pressure = numpy_support.vtk_to_numpy(image.GetCellData().GetArray('pressure'))
        p = pressure.reshape(vec,order='F')[:,:,:]

        """
            Extract the spatial information
        """

        # Allocate the memory

        x = np.zeros(image.GetNumberOfPoints())
        y = np.zeros(image.GetNumberOfPoints())
        z = np.zeros(image.GetNumberOfPoints())

        # Iterate over the points in the simulation

        for i in range(image.GetNumberOfPoints()):
            
            x[i],y[i],z[i] = image.GetPoint(i)

        # Reshape the numpy vectors into matrices
        
        x = x.reshape(dim,order='F')
        y = y.reshape(dim,order='F')
        z = z.reshape(dim,order='F')

        x = 0.5 * (x[:-1,:,:] + x[1:,:,:])
        x = 0.5 * (x[:,:-1,:] + x[:,1:,:])
        x = 0.5 * (x[:,:,:-1] + x[:,:,1:])

        y = 0.5 * (y[:-1,:,:] + y[1:,:,:])
        y = 0.5 * (y[:,:-1,:] + y[:,1:,:])
        y = 0.5 * (y[:,:,:-1] + y[:,:,1:])

        z = 0.5 * (z[:-1,:,:] + z[1:,:,:])
        z = 0.5 * (z[:,:-1,:] + z[:,1:,:])
        z = 0.5 * (z[:,:,:-1] + z[:,:,1:])

        X = x.flatten()
        Y = y.flatten()
        Z = z.flatten()

        U = u[:,:,:].flatten()
        V = v[:,:,:].flatten()
        W = w[:,:,:].flatten()
        P = p[:,:,:].flatten()

        return X, Y, Z, U, V, W, P


    def remove_files(self, filename):

        os.remove(
            os.path.join(self.directory_input, filename)
        )

        return


    def save_data_matlab_2D(self, u, v, p, filename_output):

        print('This function is pending to be built.')
        print('Contact guemes.turb@gmail.com for development status.')

        return


    def save_data_matlab_3D(self, u, v, w, p, filename_output):

        results = {
            'u': np.single(u),
            'v': np.single(v),
            'w': np.single(w),
            'p': np.single(p),
        }

        # Generate the Matlab filename

        # Save the data

        sio.savemat(
            filename_output,
            results
            )

        print(f'Saved file {filename_output:s}')

        return


    def save_data_tfrecords_2D(self, u, v, p, filename_output):

        print('This function is pending to be built.')
        print('Contact guemes.turb@gmail.com for development status.')

        return


    def save_data_tfrecords_3D(self, u, v, w, p, filename_output):

        print('This function is pending to be built.')
        print('Contact guemes.turb@gmail.com for development status.')

        return


    def save_mesh_matlab_2D(self, x, y, filename_output):

        print('This function is pending to be built.')
        print('Contact guemes.turb@gmail.com for development status.')

        return


    def save_mesh_matlab_3D(self, x, y, z, filename_output):

        results = {
            'x': np.single(z),
            'y': np.single(y),
            'z': np.single(z)
        }

        # Generate the Matlab filename

        # Save the data

        sio.savemat(
            filename_output,
            results
            )

        print('Mesh is saved')

        return


    def save_mesh_tfrecords_2D(self, x, y, filename_output):

        print('This function is pending to be built.')
        print('Contact guemes.turb@gmail.com for development status.')

        return


    def save_mesh_tfrecords_3D(self, x, y, filename_output):

        print('This function is pending to be built.')
        print('Contact guemes.turb@gmail.com for development status.')

        return

