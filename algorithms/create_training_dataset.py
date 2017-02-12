#################################################################################
#################################################################################
#################################################################################
#######                                                                   #######
#######               CREATE TRAINING DATASET FOR NN-FBP                  #######
#######                                                                   #######
#################################################################################
#################################################################################
#################################################################################




####  PYTHON MODULES
from __future__ import division , print_function
import time
import datetime
import argparse
import sys
import os
import glob
import numpy as np
import multiprocessing as mproc    




####  MY PYTHON MODULES
import my_image_io as io




####  NNFBP UTILITIES
import utils




####  MY FORMAT VARIABLES & CONSTANTS
myfloat = np.float32
myint = np.int 




##########################################################
##########################################################
####                                                  ####
####             MULTI-THREAD RECONSTRUCTION          ####
####               WITH CUSTOMIZED FILTERS            ####
####                                                  ####
##########################################################
##########################################################

def reconstr_filter_custom( sino , angles , ctr , filt_custom , picked ):
    ##  Prepare filter
    n         = len( filt_custom )
    nh        = np.int( 0.5 * n )
    filt      = np.zeros( len( filt_custom ) , dtype=myfloat )
    filt[::2] = filt_custom[:nh]
      
    ##  Reconstruction
    reco = utils.fbp( sino , angles , [ctr,0.0] , filt )
    
    ##  Pick up only selected pixels
    reco = reco[ picked ]  
    
    return reco




##########################################################
##########################################################
####                                                  ####
####                CREATE TRAINING FILE              ####
####                                                  ####
##########################################################
##########################################################
  
def create_training_file( input_path , train_path , filein , angles , npix_train_slice , 
                          idx , nang_lq , ctr_hq , nfilt , filt_custom , filt ):
    ##  Read high-quality sinogram
    sino_hq = io.readImage( input_path + filein ).astype( myfloat )
    
    ##  Reconstruct high-quality sinogram with standard filter
    params = utils.select_filter( ctr_hq , filt )
    reco_hq = utils.fbp( sino_hq , angles , params , None )
        
    ##  Create output training array
    train_data = np.zeros( ( npix_train_slice , nfilt+1 ) , dtype=myfloat ) 
        
    ##  Randomly select training pixels
    picked = utils.getPickedIndices( idx , npix_train_slice )
    
    ##  Save validation data
    train_data[:,-1] = reco_hq[picked]
        
    ##  Downsample sinogram
    sino_lq , angles_lq = utils.downsample_sinogram_angles( sino_hq , angles , nang_lq )
    
    ##  Reconstruct low-quality sinograms with customized filters
    for j in range( nfilt ):
        train_data[:,j] = reconstr_filter_custom( sino_lq , angles_lq , ctr_hq , filt_custom[j,:] , picked )

    ##  Save training data
    filename = filein
    fileout  = train_path + filename[:len(filename)-4] + '_train.npy'
    np.save( fileout , train_data )
    print( '\nTraining data saved in:\n', fileout ) 


 
    
##########################################################
##########################################################
####                                                  ####
####                       MAIN                       ####
####                                                  ####
##########################################################
##########################################################

def main():
    ##  Initial print
    print('\n')
    print('########################################################')
    print('###              CREATING TRAINING DATASET           ###')
    print('########################################################')
    print('\n')

    
    
    ##  Read config file
    if len( sys.argv ) < 2:
        sys.exit( '\nERROR: Missing input config file .cfg!\n' )
    else:
        cfg_file = open( sys.argv[1] , 'r' )
        exec( cfg_file )
        cfg_file.close()
        
    
    ##  Get list of input files
    cwd = os.getcwd()
    
    input_path = utils.analyze_path( input_path , mode='check' )
    
    os.chdir( input_path )
    file_list = []    
    file_list.append( sorted( glob.glob( '*' + input_files_hq + '*' ) ) )
    os.chdir( cwd )
    
    nfiles = len( file_list[0] )
    if nfiles == 0:
        sys.exit( '\nERROR: No file *' + input_files_hq + '* found!\n' )
        
    train_path = utils.analyze_path( train_path , mode='create_new' )    
        
    print( '\nInput data folder:\n' , input_path )
    print( '\nTrain data folder:\n' , train_path )
    print( '\nInput high-quality sinograms: ' , nfiles )
        
    
    ##  Read one file
    sino = io.readImage( input_path + file_list[0][0] )
    nang , npix = sino.shape
    print( '\nSinogram(s) with ' , nang ,' views X ' , npix, ' pixels' )
    
    
    ##  Create array of projection angles
    angles = utils.create_projection_angles( nang=nang )
    
     
    ##  Compute number of views for low-quality training sinograms
    factor = nang / ( nang_lq * 1.0 )
    print( '\nDownsampling factor for training sinograms: ' , factor )
    
    
    ##  Create customized filters
    print( '\nCreating customized filters ....' )
    filt_size   = 2 * ( 2**int( np.ceil( np.log2( npix ) ) ) )
    filt_custom = utils.generateFilterBasis( filt_size , 2 )
    nfilt       = filt_custom.shape[0]
    

    ##  Region of interest to select training data
    idx = utils.getIDX( npix , roi_l , roi_r , roi_b , roi_t )
    nh = np.int( npix * 0.5 );  l   = np.abs( roi_l )
    
    
    ##  Create training dataset 
    print( '\nCreating training dataset ....' ) 
    
    ncores_avail = mproc.cpu_count()
    if ncores > ncores_avail:
        ncores =  ncores_avail        
    print( 'Working with ncores: ' , ncores )

        
    if slice_ind_1 > 0 and slice_ind_1 <= nfiles:
        ind_1 = slice_ind_1
    else:
        ind_1 = 0
        
    if slice_ind_2 > 0 and slice_ind_2 <= nfiles:
        ind_2 = slice_ind_2
    else:
        ind_2 = nfiles
        
    if take_every <= 0 or take_every >= (ind_2-ind_1):
        take_every = 1
    print( 'Start slice index: ' , ind_1 )
    print( 'End slice index: ' , ind_2 )
    print( 'Use 1 slice every ', take_every,' slices' )
    
    pool = mproc.Pool( processes=ncores )
    for i in range( ind_1 , ind_2 , take_every ):
        pool.apply_async( create_training_file , 
                          ( input_path , train_path , file_list[0][i] , angles ,
                            npix_train_slice , idx , nang_lq , ctr_hq , nfilt ,
                            filt_custom , filt ) 
                        )            
    pool.close()
    pool.join()
    
    #for i in range( ind_1 , ind_2 ):
    #    create_training_file( input_path , train_path , file_list[0][i] , angles , npix_train_slice , 
    #                          idx , nang_lq , ctr_hq , nfilt , filt_custom , filt )
    
    


##########################################################
##########################################################
####                                                  ####
####               CALL TO MAIN                       ####
####                                                  ####
##########################################################
##########################################################  

if __name__ == '__main__':
    main()
