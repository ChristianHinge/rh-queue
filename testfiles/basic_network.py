#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 09:34:44 2019

@author: amalie

Most Updated version of segmentation script from master project taken from test_weights_final which was used to train the weights_combo.
Used for developing new and improved version. 7/5 2020

Next steps: 
1. remove the prediction part from the training part.
2. Comment and remove all unnecessary code.
3. Test
4. Make 3D

"""


from __future__ import print_function
import os
import numpy as np
import tensorflow as tf
import difflib                  
import SimpleITK as sitk
import scipy.spatial
#import keras.utils.Sequence
from keras.models import Model
from keras.layers.merge import concatenate
from keras.layers import Input, merge, Convolution2D, MaxPooling2D, UpSampling2D, Cropping2D, ZeroPadding2D, Dropout, BatchNormalization, Activation
from keras.optimizers import Adam
from evaluation_npad import getDSC, getHausdorff, getLesionDetection, getLesionDetectionNum, getAVD, getImages  #please download evaluation.py from the WMH website
from keras.callbacks import ModelCheckpoint
from keras import backend as K
from keras.preprocessing.image import ImageDataGenerator

cfg = K.tf.ConfigProto(gpu_options={'allow_growth': True})
K.set_session(K.tf.Session(config=cfg))
import glob
import warnings
warnings.filterwarnings("ignore")
import pyminc.volumes.factory as pyfac
import pickle
from DataGen import DataGenerator2DStacks
from scipy import ndimage
#from sklearn.utils import class_weight
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import collections


### ----define loss function for U-net ------------


def save_history_plot(history,outname):
    plt.figure()
    plt.subplot(121)
    plt.plot(np.arange(len(history['loss'])),history['loss'],'r-',label='Loss')
    plt.plot(np.arange(len(history['val_loss'])),history['val_loss'],'g-',alpha=0.5,label='val_Loss')#Indsat af Amalie
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.subplot(122)
    plt.plot(np.arange(len(history['loss'])),history['dice_coef_for_training'],'b-',label='Dice')
    plt.ylabel('Dice')
    plt.xlabel('Epoch')
    plt.tight_layout()
    plt.savefig('history/%s.png' % outname)


smooth = 1.
def dice_coef_for_training(y_true, y_pred):
    print('1',np.shape(y_pred))
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)
def dice_coef_loss(y_true, y_pred):
    print('2',np.shape(y_pred))
    print('3',np.shape(y_true))
    return -dice_coef_for_training(y_true, y_pred)

def get_crop_shape(target, refer):
        # width, the 3rd dimension
        cw = (target.get_shape()[2] - refer.get_shape()[2]).value
        assert (cw >= 0)
        if cw % 2 != 0:
            cw1, cw2 = int(cw/2), int(cw/2) + 1
        else:
            cw1, cw2 = int(cw/2), int(cw/2)
        # height, the 2nd dimension
        ch = (target.get_shape()[1] - refer.get_shape()[1]).value
        assert (ch >= 0)
        if ch % 2 != 0:
            ch1, ch2 = int(ch/2), int(ch/2) + 1
        else:
            ch1, ch2 = int(ch/2), int(ch/2)

        return (ch1, ch2), (cw1, cw2)



### ----define U-net architecture--------------
def get_do_unet(img_shape = None, weights_file=None, custom_load_func = False):

        dim_ordering = 'tf'
        inputs = Input(shape = img_shape)
        concat_axis = -1
        ### the size of convolutional kernels is defined here    
        conv1 = Convolution2D(64, 5, 5, border_mode='same', dim_ordering=dim_ordering, name='conv1_1')(inputs)
        ac = Activation('relu')(conv1)
        do = Dropout(0.2)(ac)
        conv1 = Convolution2D(64, 5, 5, border_mode='same', dim_ordering=dim_ordering)(do)
        ac = Activation('relu')(conv1)
        do = Dropout(0.2)(ac)
        pool1 = MaxPooling2D(pool_size=(2, 2), dim_ordering=dim_ordering)(do)
        conv2 = Convolution2D(96, 3, 3, border_mode='same', dim_ordering=dim_ordering)(pool1)
        ac2 = Activation('relu')(conv2)
        do2 = Dropout(0.2)(ac2)
        conv2 = Convolution2D(96, 3, 3, border_mode='same', dim_ordering=dim_ordering)(do2)
        ac2 = Activation('relu')(conv2)
        do2 = Dropout(0.2)(ac2)
        pool2 = MaxPooling2D(pool_size=(2, 2), dim_ordering=dim_ordering)(do2)

        conv3 = Convolution2D(128, 3, 3, border_mode='same', dim_ordering=dim_ordering)(pool2)
        ac3 = Activation('relu')(conv3)
        do3 = Dropout(0.2)(ac3)
        conv3 = Convolution2D(128, 3, 3, border_mode='same', dim_ordering=dim_ordering)(do3)
        ac3 = Activation('relu')(conv3)
        do3 = Dropout(0.2)(ac3)
        pool3 = MaxPooling2D(pool_size=(2, 2), dim_ordering=dim_ordering)(do3)

        conv4 = Convolution2D(256, 3, 3, border_mode='same', dim_ordering=dim_ordering)(pool3)
        ac4 = Activation('relu')(conv4)
        do4 = Dropout(0.2)(ac4)
        conv4 = Convolution2D(256, 4, 4, border_mode='same', dim_ordering=dim_ordering)(do4)
        ac4 = Activation('relu')(conv4)
        do4 = Dropout(0.2)(ac4)
        pool4 = MaxPooling2D(pool_size=(2, 2), dim_ordering=dim_ordering)(do4)
        
        conv5 = Convolution2D(512, 3, 3, border_mode='same', dim_ordering=dim_ordering)(pool4)
        ac5 = Activation('relu')(conv5)
        do5 = Dropout(0.2)(ac5)
        conv5 = Convolution2D(512, 3, 3, border_mode='same', dim_ordering=dim_ordering)(do5)
        ac5 = Activation('relu')(conv5)
        do5 = Dropout(0.2)(ac5)

        up_conv5 = UpSampling2D(size=(2, 2), dim_ordering=dim_ordering)(do5)
        ch, cw = get_crop_shape(conv4, up_conv5)
        crop_conv4 = Cropping2D(cropping=(ch,cw), dim_ordering=dim_ordering)(conv4)
        up6 = concatenate([up_conv5, crop_conv4], axis=concat_axis)     #Amalie chaned it from merge to concatenate
        conv6 = Convolution2D(256, 3, 3, border_mode='same', dim_ordering=dim_ordering)(up6)
        ac6 = Activation('relu')(conv6)
        do6 = Dropout(0.2)(ac6)
        conv6 = Convolution2D(256, 3, 3, border_mode='same', dim_ordering=dim_ordering)(do6)
        ac6 = Activation('relu')(conv6)
        do6 = Dropout(0.2)(ac6)

        up_conv6 = UpSampling2D(size=(2, 2), dim_ordering=dim_ordering)(do6)
        ch, cw = get_crop_shape(conv3, up_conv6)
        crop_conv3 = Cropping2D(cropping=(ch,cw), dim_ordering=dim_ordering)(conv3)
        up7 = concatenate([up_conv6, crop_conv3], axis=concat_axis)
        conv7 = Convolution2D(128, 3, 3, border_mode='same', dim_ordering=dim_ordering)(up7)
        ac7 = Activation('relu')(conv7)
        do7 = Dropout(0.2)(ac7)
        conv7 = Convolution2D(128, 3, 3, border_mode='same', dim_ordering=dim_ordering)(do7)
        ac7 = Activation('relu')(conv7)
        do7 = Dropout(0.2)(ac7)

        up_conv7 = UpSampling2D(size=(2, 2), dim_ordering=dim_ordering)(do7)
        ch, cw = get_crop_shape(conv2, up_conv7)
        crop_conv2 = Cropping2D(cropping=(ch,cw), dim_ordering=dim_ordering)(conv2)
        up8 = concatenate([up_conv7, crop_conv2], axis=concat_axis)
        conv8 = Convolution2D(96, 3, 3, border_mode='same', dim_ordering=dim_ordering)(up8)
        ac8 = Activation('relu')(conv8)
        do8 = Dropout(0.2)(ac8)
        conv8 = Convolution2D(96, 3, 3, border_mode='same', dim_ordering=dim_ordering)(do8)
        ac8 = Activation('relu')(conv8)
        do8 = Dropout(0.2)(ac8)

        up_conv8 = UpSampling2D(size=(2, 2), dim_ordering=dim_ordering)(do8)
        ch, cw = get_crop_shape(conv1, up_conv8)
        crop_conv1 = Cropping2D(cropping=(ch,cw), dim_ordering=dim_ordering)(conv1)
        up9 = concatenate([up_conv8, crop_conv1], axis=concat_axis)
        conv9 = Convolution2D(64, 3, 3, border_mode='same', dim_ordering=dim_ordering)(up9)
        ac9 = Activation('relu')(conv9)
        do9 = Dropout(0.2)(ac9)
        conv9 = Convolution2D(64, 3, 3, border_mode='same', dim_ordering=dim_ordering)(do9)
        ac9 = Activation('relu')(conv9)
        do9 = Dropout(0.2)(ac9)

        ch, cw = get_crop_shape(inputs, do9)
        conv9 = ZeroPadding2D(padding=(ch, cw), dim_ordering=dim_ordering)(conv9)
        conv10 = Convolution2D(1, 1, 1, activation='sigmoid', dim_ordering=dim_ordering)(conv9)
        model = Model(input=inputs, output=conv10)
        
        if not weights_file == None:
            j = 0
            i = 0
            oldlayers=[]
            if custom_load_func:
                #pass # TODO
                img_shape_old=(rows_standard, cols_standard, 3)
                model_old = get_unet(img_shape_old,weights_file,custom_load_func=False)
                for layer in model.layers:
                
                   if layer.name.startswith('conv'):
                       
                       
                       for layer_old in model_old.layers:
                           if layer_old.name.startswith('conv'):
                               oldlayers.append(layer_old)
                           i += 1
                       old_weight = oldlayers[j].get_weights()
                       layer.set_weights(old_weight)
                       
                       j += 1
            else:
                model.load_weights(weights_file)
        
        model.compile(optimizer=Adam(lr=(1e-5)), loss=dice_coef_loss, metrics=[dice_coef_for_training])
        

        return model

 
def Utrecht_preprocessing(FLAIR_image):
    
    # Preprocessing: converting input to a size of 384x384, Gaussian Normalisation
    print('4',np.shape(FLAIR_image))
    num_selected_slice = np.shape(FLAIR_image)[0]
    image_rows_Dataset = np.shape(FLAIR_image)[1]
    image_cols_Dataset = np.shape(FLAIR_image)[2]

    brain_mask_FLAIR = np.zeros((np.shape(FLAIR_image)[0],image_rows_Dataset, image_cols_Dataset), dtype=np.float32)
    FLAIR_image_suitable = np.zeros((num_selected_slice, rows_standard, cols_standard), dtype=np.float32)
    Brain_mask_flair_suitable = np.zeros((num_selected_slice, rows_standard, cols_standard), dtype=np.float32)

    # FLAIR
    if FLAIR_image.shape[0] == 44:
        thresh_FLAIR = thresh_FLAIR_2
    else:
        thresh_FLAIR = thresh_FLAIR_1
    
    brain_mask_FLAIR[FLAIR_image >=thresh_FLAIR] = 1
    print('flair1',FLAIR_image.shape)
    brain_mask_FLAIR[FLAIR_image < thresh_FLAIR] = 0
    
    
    for iii in range(np.shape(FLAIR_image)[0]):
        brain_mask_FLAIR[iii,:,:] = scipy.ndimage.morphology.binary_fill_holes(brain_mask_FLAIR[iii,:,:])  #fill the holes inside brain
    print('flair2',FLAIR_image.shape)
    
    # Different input-sizes
    if np.shape(FLAIR_image)[1] < std_res:
        FLAIR_image_suitable[:, (int(cols_standard/2)-int(image_cols_Dataset/2)):(int(cols_standard/2)+int(image_cols_Dataset/2)), (int(cols_standard/2)-int(image_cols_Dataset/2)):(int(cols_standard/2)+int(image_cols_Dataset/2))] = FLAIR_image
        Brain_mask_flair_suitable[:, (int(cols_standard/2)-int(image_cols_Dataset/2)):(int(cols_standard/2)+int(image_cols_Dataset/2)), (int(cols_standard/2)-int(image_cols_Dataset/2)):(int(cols_standard/2)+int(image_cols_Dataset/2))] = brain_mask_FLAIR
        FLAIR_image = FLAIR_image_suitable
        brain_mask_FLAIR = Brain_mask_flair_suitable
    
    elif np.shape(FLAIR_image)[1] >= std_res:
        FLAIR_image = FLAIR_image[:, (int(image_rows_Dataset/2)-int(rows_standard/2)):(int(image_rows_Dataset/2)+int(rows_standard/2)), (int(image_cols_Dataset/2)-int(cols_standard/2)):(int(image_cols_Dataset/2)+int(cols_standard/2))]
        brain_mask_FLAIR = brain_mask_FLAIR[:, (int(image_rows_Dataset/2)-int(rows_standard/2)):(int(image_rows_Dataset/2)+int(rows_standard/2)), (int(image_cols_Dataset/2)-int(cols_standard/2)):(int(image_cols_Dataset/2)+int(cols_standard/2))]
    print('flair3',FLAIR_image.shape)
    FLAIR_image -=np.mean(FLAIR_image[brain_mask_FLAIR == 1])      #Gaussion Normalization
    FLAIR_image /=np.std(FLAIR_image[brain_mask_FLAIR == 1])
    
    
    FLAIR_image  = FLAIR_image[..., np.newaxis]
    
    return FLAIR_image


def Utrecht_postprocessing(FLAIR_array, pred):
    print('post_flair:', FLAIR_array.shape)
    print('post_pred:', pred.shape)
    num_selected_slice = np.shape(FLAIR_array)[0]
    image_rows_Dataset = np.shape(FLAIR_array)[1]
    image_cols_Dataset = np.shape(FLAIR_array)[2]
    if np.shape(FLAIR_array)[1] < std_res:
        original_pred = pred[:, (int(rows_standard/2)-int(image_rows_Dataset/2)):(int(rows_standard/2)+int(image_rows_Dataset/2)), (int(cols_standard/2)-int(image_cols_Dataset/2)):(int(cols_standard/2)+int(image_cols_Dataset/2))]
        
    elif np.shape(FLAIR_array)[1] >= std_res:
        original_pred = np.zeros((num_selected_slice,image_rows_Dataset,image_cols_Dataset), np.float32) # Converting to old image-size
        original_pred[:,int((int(image_rows_Dataset)-int(rows_standard))/2):int((int(image_rows_Dataset)+int(rows_standard))/2),int((int(image_cols_Dataset)-int(cols_standard))/2):int((int(image_cols_Dataset)+int(cols_standard))/2)] = pred[:,:,:,0]
        
    print('original_pred:', original_pred.shape)
    return original_pred

###---Here comes the main funtion--------------------------------------------
###---Leave one patient out validation--------------------------------------------

std_res = 384
rows_standard = std_res
cols_standard = std_res
### SHOULD BE STANDARDISED ###
thresh_FLAIR_1 = 70     #to mask the brain
thresh_T1_1 = 40
thresh_FLAIR_2 = 1000     #to mask the brain
thresh_T1_2 = 1000
    
#read the dirs of test data 
inputDir = '/homes/amalie/WMH/WMH'
input_dir_all = '/homes/amalie/WMH/WMH'


#------------------------ t1 ELLER t2 ------------------------------------

modality = 'none'
d=3


###---dir to save results---------
if modality == 'T1':
    outputDir = '/homes/amalie/Amalie/PhD/Code/MS_SEG/results/basic_network_test'
elif modality == 'T2':
    outputDir = 'evaluation_result_ownres_uT1_multi_selected/do_gen_sb_aug_whole_T2'
elif modality == 'none':
    outputDir = '/homes/amalie/Amalie/PhD/Code/MS_SEG/results/original_test3'


if not os.path.exists(outputDir):
    os.mkdir(outputDir)  
    os.mkdir(os.path.join(outputDir,'preds'))
    os.mkdir(os.path.join(outputDir,'weights'))
#-------------------------------------------

#All the slices and the corresponding patients id


###---train u-net models-------------------------------------------------------------------------------

rand_samp = [7]#[24,26,17,35,1,76,78,84,93,94] 
print(rand_samp)


print('-'*30)
print('Fitting model...')
print('-'*30)

###---parameters of training are set here------------------------------------
ensemble_parameter = 1
epoch =2
BS = 6
lr = 5

if d == 1:
    weights_file = '/homes/amalie/Amalie/Speciale/MICCAI17/evaluation_result_LOOV_M17_multi/weights17/weights_three_datasets_two_channels_LOOV_uT1_17_pids23_ens2_ep100.h5' #<- miccai model
elif d == 2:
    weights_file = '/homes/amalie/Amalie/Speciale/MICCAI17/evaluation_result_LOOV_M17_multi/weights17/weights_three_datasets_two_channels_LOOV_17_pids23_ens2_ep100.h5'
elif d == 3: 
    weights_file = '/homes/amalie/Amalie/Speciale/MICCAI17/evaluation_result_LOOV_M17_multi/weights17/weights_three_datasets_two_channels_LOOV_sb_uT1_17_pids23_ens0_ep100.h5' #<- miccai model
elif d == 6: 
    weights_file = False # no miccai model for two channels and slices input
   
img_shape=(rows_standard, cols_standard, d)

###---ensemble model --------------------------

# IDs for training and validation generator
pid_ids = np.load(os.path.join(input_dir_all,'ids_individual_train_sel_wo94_wo17_384.npy'))
print("patient training ids", pid_ids)
val_ids = np.load(os.path.join(input_dir_all,'ids_individual_val.npy'))


num_epoch = int(np.ceil(len(pid_ids)/BS))
val_step =  int(np.ceil(len(val_ids)/BS))
print('num_epoch',num_epoch)
print('val_step',val_step)

aug = ImageDataGenerator(rotation_range=15,
           shear_range=0.01,
           zoom_range=[0.9, 1.1],
           horizontal_flip=True,
           vertical_flip=False,
           data_format='channels_last', fill_mode='constant', cval=0)

# Husk at ændre data_folder hvis træningsdata ændres
for iiii in range(ensemble_parameter):
        training_generator = DataGenerator2DStacks(dim_x= std_res,dim_y= std_res, dim_d= d, batch_size= BS,  data_folder= 'IDs_train_sel_384', shuffle= True, aug=aug, visualize_batch=True).generate(pid_ids,'train')
        validation_generator = DataGenerator2DStacks(dim_x= std_res,dim_y= std_res, dim_d= d, batch_size= BS,  data_folder= 'IDs_val', shuffle= True, aug=False, visualize_batch=True).generate(val_ids,'val')
    
        #model = get_do_unet(img_shape)
        if d == 6: 
            model = get_unet(img_shape,custom_load_func=True)
        else:
            model = get_do_unet(img_shape,weights_file,custom_load_func=False)
    
        filepath = os.path.join(outputDir,'weights/weights-{epoch:02d}-{val_loss:.2f}'+str(iiii)+'.hdf5')
        model_checkpoint_long = ModelCheckpoint(filepath, save_best_only=False, period = 50)
        history = model.fit_generator(generator=training_generator, steps_per_epoch=num_epoch, epochs=epoch, validation_data=validation_generator, validation_steps=val_step, callbacks=[model_checkpoint_long])
        with open('history/weights_384_'+str(modality)+'_ens'+str(iiii)+'_ep'+str(epoch)+'_lr'+str(lr)+'_bs'+str(BS)+'_ens'+str(ensemble_parameter)+'.pickle', 'wb') as file_pi:
            pickle.dump(history.history, file_pi)
        
        model.save(os.path.join(outputDir,'weights/weights_384_'+str(modality)+'_ens'+str(iiii)+'_ep'+str(epoch)+'_lr'+str(lr)+'_bs'+str(BS)+'_ens'+str(ensemble_parameter)+'.h5'))
        save_history_plot(history.history,'weights_384_'+str(modality)+'_ens'+str(iiii)+'_ep'+str(epoch)+'_lr'+str(lr)+'_bs'+str(BS)+'_ens'+str(ensemble_parameter))
        print('ensamble',iiii)
        
    
print('-'*30)
print('Testing model...')
print('-'*30)
# ----------------------- Testing the model -----------------------------
for pid_test in rand_samp:
    if pid_test == 31:
        continue
    i =0
    pid_test_s = str(pid_test)
    
    if int(pid_test) in range (1,10):
        pid_test = "0"+str(pid_test)
    
    
    string = os.path.join(inputDir,'sub-patient'+str(pid_test))
    subd = glob.glob(string+'/*/')
    for time in subd:
            
            if i >= 1:
                continue
            if pid_test == 14:
                    print(time.split('/')[6])
                    if time.split('/')[6] != '20160517x2':
                        continue
            
            print(time)
            fil = glob.glob(str(time)+'anat/*T2w.nii.gz')[0]
            exists = os.path.isfile(str(fil))
            fil_mask = str(time)+'WMHmask.nii.gz'
            exists_mask = os.path.isfile(str(fil_mask))
            if exists_mask:
                
                fil_flair = glob.glob(str(time)+'anat/*FLAIR.nii.gz')[0]
                exists_flair = os.path.isfile(str(fil_flair))
                
                if exists_flair:
                    FLAIR_img = sitk.ReadImage(fil_flair)
                                    
                
                # CHANGE THIS IN NEW SCRPIT
                if modality  == 'T1':
                    T1_img =  sitk.ReadImage(glob.glob(str(time)+'anat/*T2w.nii.gz')[0])
                    T1_array = sitk.GetArrayFromImage(T1_img)
                    T1_spacing = T1_img.GetSpacing
                elif modality == 'T2':
                    T1_img =  sitk.ReadImage(glob.glob(str(time)+'anat/*T2w.nii.gz')[0])
                    T1_array = sitk.GetArrayFromImage(T1_img)
                    T1_spacing = T1_img.GetSpacing
                                
                FLAIR_arr = sitk.GetArrayFromImage(FLAIR_img)
                FLAIR_array = sitk.GetArrayFromImage(FLAIR_img)
                FLAIR_spacing = FLAIR_img.GetSpacing()
                FLAIR_origin = FLAIR_img.GetOrigin()
                FLAIR_direction = FLAIR_img.GetDirection()
            
                
                #Proccess testing data-----
            
                # To save previous and next slice for slice sequence
                imgs_test = Utrecht_preprocessing(FLAIR_array)
                print(imgs_test.shape)
                
                if d ==3 or d == 6 or d==1:
                    if  modality  == 'none':
                        imgs_test = imgs_test[..., 0:1].copy()
                    
                    # Save previous and next slice for slice sequences
                    if modality  == 'none' and d != 1:
                        imgs_trip_test = np.empty((imgs_test.shape[0], imgs_test.shape[1], imgs_test.shape[2], 3))
                        for test_slice in np.arange(imgs_test.shape[0]):
                          if test_slice == 0:
                              imgs_trip_test[test_slice, :, :, 0] = imgs_test[test_slice,...,0]
                          else:
                              imgs_trip_test[test_slice, :, :, 0] = imgs_test[test_slice-1,...,0]
                          imgs_trip_test[test_slice, :, :, 1] = imgs_test[test_slice,...,0]
                          if test_slice == imgs_test.shape[0]-1:
                              imgs_trip_test[test_slice, :, :, 2] = imgs_test[test_slice,...,0]
                          else:
                              imgs_trip_test[test_slice, :, :, 2] = imgs_test[test_slice+1,...,0]
                              
                    if modality == 'T2' or modality == 'T1':
                        imgs_trip_test = np.empty((imgs_test.shape[0], imgs_test.shape[1], imgs_test.shape[2], 6))
                         
                        for test_slice in np.arange(imgs_test.shape[0]):
                          if test_slice == 0:
                              imgs_trip_test[test_slice, :, :, 0] = imgs_test[test_slice,...,0]
                          else:
                              imgs_trip_test[test_slice, :, :, 0] = imgs_test[test_slice-1,...,0]
                          imgs_trip_test[test_slice, :, :, 1] = imgs_test[test_slice,...,0]
                          if test_slice == imgs_test.shape[0]-1:
                              imgs_trip_test[test_slice, :, :, 2] = imgs_test[test_slice,...,0]
                          else:
                              imgs_trip_test[test_slice, :, :, 2] = imgs_test[test_slice+1,...,0]
                             
                        
                          if test_slice == 0:
                              imgs_trip_test[test_slice, :, :, 3] = imgs_test[test_slice,...,1]
                          else:
                              imgs_trip_test[test_slice, :, :, 3] = imgs_test[test_slice-1,...,1]
                          imgs_trip_test[test_slice, :, :, 4] = imgs_test[test_slice,...,1]
                          if test_slice == imgs_test.shape[0]-1:
                              imgs_trip_test[test_slice, :, :, 5] = imgs_test[test_slice,...,1]
                          else:
                              imgs_trip_test[test_slice, :, :, 5] = imgs_test[test_slice+1,...,0]       
                       
                       
                print('shape of imgs_test', imgs_test.shape)
                pred = 0

                #Transfer learning
                if d == 1:
                    weights_file = '/homes/amalie/Amalie/Speciale/MICCAI17/evaluation_result_LOOV_M17_multi/weights17/weights_three_datasets_two_channels_LOOV_uT1_17_pids23_ens2_ep100.h5' #<- miccai model
                elif d == 2:
                    weights_file = '/homes/amalie/Amalie/Speciale/MICCAI17/evaluation_result_LOOV_M17_multi/weights17/weights_three_datasets_two_channels_LOOV_17_pids23_ens2_ep100.h5'
                elif d == 3:
                    weights_file = '/homes/amalie/Amalie/Speciale/MICCAI17/evaluation_result_LOOV_M17_multi/weights17/weights_three_datasets_two_channels_LOOV_sb_uT1_17_pids23_ens0_ep100.h5' #<- miccai model
                    imgs_test = imgs_trip_test
                elif d == 6:
                    weights_file = '/homes/amalie/Amalie/Speciale/MICCAI17/evaluation_result_LOOV_M17_multi/weights17/weights_three_datasets_two_channels_LOOV_sb_uT1_17_pids23_ens0_ep100.h5' #<- miccai model
                    imgs_test = imgs_trip_test
                #Training
                for iiii in range(ensemble_parameter):
                    if d == 6: 
                        model = get_do_bn_unet(img_shape,custom_load_func=False)
                    else:
                        model = get_do_unet(img_shape,weights_file,custom_load_func=False)
                    
                    model.load_weights(os.path.join(outputDir,'weights/weights_384_'+str(modality)+'_ens'+str(iiii)+'_ep'+str(epoch)+'_lr'+str(lr)+'_bs'+str(BS)+'_ens'+str(ensemble_parameter)+'.h5'))
                    pred_temp_ = model.predict(imgs_test, batch_size=1,verbose=1)
                    pred = pred + pred_temp_
                    np.save(os.path.join(outputDir,'preds/pred_temp_'+str(modality)+'_pid'+str(pid_test)+'_ens'+str(iiii)+'_ep'+str(epoch)), pred_temp_)
                    print('ensamble',iiii)
                
                thres = 0.5
                thr = '05'
                pred = pred/int(ensemble_parameter)
                pred[pred[...,0] > thres] = 1      #thresholding 
                pred[pred[...,0] <= thres] = 0
                print("predicted image shape:", pred[...,0].shape)
                
                #Save lesion image
                new_img = sitk.GetImageFromArray(pred[...,0])
                new_img.SetSpacing(FLAIR_spacing)
                new_img.SetDirection(FLAIR_direction)
                new_img.SetOrigin(FLAIR_origin)
                sitk.WriteImage(new_img, os.path.join(outputDir,'FLAIR_test_noPostp.nii'))
                
            
                #Postprocessing
                original_pred = Utrecht_postprocessing(FLAIR_array, pred)
                print('originalpred shape: ',original_pred[...].shape)
                #Make outputdir
                if not os.path.exists(outputDir):
                    os.mkdir(outputDir)
                print('test_patient',pid_test)
                mid_dir = os.path.join(outputDir,str(pid_test))  #directory for images
                if not os.path.exists(mid_dir):
                    os.mkdir(mid_dir)
                
                filename_resultImage_nii = os.path.join(outputDir, str(pid_test), 'result_384_'+str(modality)+'_ens'+str(iiii)+'_ep'+str(epoch)+'_lr'+str(lr)+'_bs'+str(BS)+'_ens'+str(ensemble_parameter)+'.nii')
                # Set image metadata from input image
                nii_img = sitk.GetImageFromArray(original_pred)
                nii_img.SetSpacing(FLAIR_spacing)
                nii_img.SetDirection(FLAIR_direction)
                nii_img.SetOrigin(FLAIR_origin)
                sitk.WriteImage(nii_img, filename_resultImage_nii)
                
                #Get manual mask for comparison
                filename_testImage_nii = os.path.join(time, 'WMHmask.nii.gz')
                #Get image
                testImage_vac, resultImage_vac = getImages(filename_testImage_nii, filename_resultImage_nii)
                
                recall, f1, arrTest, arrRes = getLesionDetectionNum(testImage_vac, resultImage_vac)
                testUn, testCounts = np.unique(arrTest, return_counts=True)
                for les in testUn:
                    if les == 0:
                        continue
                    les_size = testCounts[np.where((testUn==les))] * nii_img.GetSpacing()[0]* nii_img.GetSpacing()[1]*nii_img.GetSpacing()[2] 
                    if les_size < 8:
                        arrTest[np.where((arrTest==les))] = 0
                testUn, testCounts = np.unique(arrTest, return_counts=True)
                
                resUn, resCounts = np.unique(arrRes, return_counts=True)
                for les in resUn:
                    if les == 0:
                        continue
                    les_size = resCounts[np.where((resUn==les))] * nii_img.GetSpacing()[0]* nii_img.GetSpacing()[1]*nii_img.GetSpacing()[2] 
                    if les_size < 8:
                        arrRes[np.where((arrRes==les))] = 0 
                resUn, resCounts = np.unique(arrRes, return_counts=True)
                
                for vox in original_pred:
                    original_pred[np.where((arrRes == 0))] = 0
                filename_vac_resultImage_nii = os.path.join(outputDir, str(pid_test), 'result_vac_384_'+str(modality)+'_ens'+str(iiii)+'_ep'+str(epoch)+'_lr'+str(lr)+'_bs'+str(BS)+'_ens'+str(ensemble_parameter)+'.nii')
                
                nii_img = sitk.GetImageFromArray(original_pred)
                nii_img.SetSpacing(FLAIR_spacing)
                nii_img.SetDirection(FLAIR_direction)
                nii_img.SetOrigin(FLAIR_origin)
                sitk.WriteImage(nii_img, filename_vac_resultImage_nii)
                
                original_test =sitk.GetArrayFromImage(sitk.ReadImage(filename_testImage_nii))
                for vox in original_test:
                    original_test[np.where((arrTest == 0))] = 0

                filename_vac_testImage_nii = os.path.join(time, 'WMHmask_8_vac.nii') 
                test_img = sitk.GetImageFromArray(original_test)
                original_test_img=sitk.ReadImage(filename_testImage_nii)
                testSpace= original_test_img.GetSpacing()
                testDirec= original_test_img.GetDirection()
                testOri= original_test_img.GetOrigin()
                test_img.SetSpacing(testSpace)
                test_img.SetDirection(testDirec)
                test_img.SetOrigin(testOri)
                sitk.WriteImage(test_img, filename_vac_testImage_nii)
                
            # Calculate vacuumed metrics    
                testImage_vac, resultImage_vac = getImages(filename_vac_testImage_nii, filename_vac_resultImage_nii)
                testImage, resultImage = getImages(filename_testImage_nii, filename_resultImage_nii)
                dsc_vac = getDSC(testImage_vac, resultImage_vac)
                avd_vac = getAVD(testImage_vac, resultImage_vac) 
                recall_vac, f1_vac = getLesionDetection(testImage_vac, resultImage_vac)
                print('Result of patient '+str(pid_test))    
                print('Dice_vac',                dsc_vac,       '(higher is better, max=1)')
                print('avd_vac',                 avd_vac,  '%',  '(lower is better, min=0)')
                print('Lesion detection vac', recall_vac,       '(higher is better, max=1)')
                print('Lesion F1 vac',            f1_vac,       '(higher is better, max=1)')
            #Save result vacuumed-------------------------------------------------------	
                result_output_dir = os.path.join(outputDir,str(pid_test),str(pid_test)+'_'+str(time.split('/')[6])+'_sb_ep'+str(epoch)+'_lr'+str(lr)+'_bs'+str(BS)+'left_out')  #directory for images
                if not os.path.exists(result_output_dir):
                    os.mkdir(result_output_dir)
                np.save(os.path.join(result_output_dir,'dsc_vac.npy'), dsc_vac)
                np.save(os.path.join(result_output_dir,'avd_vac.npy'), avd_vac)
                np.save(os.path.join(result_output_dir,'recall_vac.npy'), recall_vac)
                np.save(os.path.join(result_output_dir,'f1_vac.npy'), f1_vac)
            # Calculate original results
                dsc = getDSC(testImage, resultImage)
                avd = getAVD(testImage, resultImage) 
                recall, f1 = getLesionDetection(testImage, resultImage)
                print('Result of patient '+str(pid_test))    
                print('Dice',                dsc,       '(higher is better, max=1)')
                print('AVD',                 avd,  '%',  '(lower is better, min=0)')
                print('Lesion detection', recall,       '(higher is better, max=1)')
                print('Lesion F1',            f1,       '(higher is better, max=1)')
            #Save original result-------------------------------------------------------	
                result_output_dir = os.path.join(outputDir,str(pid_test),str(pid_test)+'_'+str(time.split('/')[6])+'_sb_ep'+str(epoch)+'_lr'+str(lr)+'_bs'+str(BS)+'left_out')  #directory for images
                if not os.path.exists(result_output_dir):
                    os.mkdir(result_output_dir)
                np.save(os.path.join(result_output_dir,'dsc.npy'), dsc)
                np.save(os.path.join(result_output_dir,'avd.npy'), avd)
                np.save(os.path.join(result_output_dir,'recall.npy'), recall)
                np.save(os.path.join(result_output_dir,'f1.npy'), f1)
            #-------------------------------------------------------------------
            # Save images for surveying result
                img_outputDir = os.path.join(outputDir,str(pid_test),'imgs_sb'+'_'+str(time.split('/')[6])+'_ep'+str(epoch)+'_lr'+str(lr)+'_bs'+str(BS))     
                if not os.path.exists(img_outputDir):
                    os.mkdir(img_outputDir)    
            
                '''
                for slices in [12, 18, 24]:
                    plt.figure()
                    img_s = original_pred
                    #sitk.Show(img_s)
                    plt.imshow(img_s[slices, :, :], interpolation='nearest',cmap = 'gray')
                    plt.savefig(os.path.join(img_outputDir,str(epoch)+'_'+str(slices)+'_result.png'))    
                    
                    testImage_nii =  sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(time, 'anat/mask_ownres_rd_o.nii')))
                    mask = testImage_nii
                    plt.imshow(mask[slices, :, :], interpolation='nearest',cmap = 'gray')
                    plt.savefig(os.path.join(img_outputDir,str(epoch)+'_'+str(slices)+'_testmask.png'))   
                    
                    flair = FLAIR_arr
                    plt.imshow(flair[slices, :, :], interpolation='nearest',cmap = 'gray')
                    plt.savefig(os.path.join(img_outputDir,str(epoch)+'_'+str(slices)+'_flair.png'))                         
                    fig, ax = plt.subplots()    
                    img_s = np.ma.masked_where(img_s == 0, img_s)
                    mask = np.ma.masked_where(mask == 0, mask)

                    
                    ax.imshow(flair[slices, :, :], interpolation='nearest',cmap = 'gray')                        
                    ax.imshow(mask[slices, :, :], interpolation='nearest',cmap = 'autumn', alpha = 0.9)
                    ax.imshow(img_s[slices, :, :], interpolation='nearest',cmap = 'cool', alpha = 0.6)
                    plt.savefig(os.path.join(img_outputDir,str(epoch)+'_'+str(slices)+'_mix.png')) 
                '''
                     
                fig = plt.figure()
                sub_plt = 0
                for slices in [12, 18, 24]:
                
                    print(sub_plt)
                    #f, axarr = plt.subplots(1, 4)
                    plt.subplot(3, 4, 1+(sub_plt*4))
                    flair = FLAIR_arr
                    plt.imshow(np.flipud(flair[slices, :, :]), interpolation='nearest',cmap = 'gray')
                    plt.title(str(slices)+'FLAIR')
                    plt.xticks([])
                    plt.yticks([])
                    plt.subplot(3, 4, 2+(sub_plt*4))
                    testImage_nii =  sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(time, 'anat/mask_ownres_rd_o.nii')))
                    mask = testImage_nii
                    plt.imshow(np.flipud(mask[slices, :, :]), interpolation='nearest',cmap = 'gray')
                    plt.title(str(slices)+'Mask')                   
                    plt.xticks([])
                    plt.yticks([])
                    plt.subplot(3, 4, 3+(sub_plt*4))
                    img_s = original_pred
                    plt.imshow(np.flipud(img_s[slices, :, :]), interpolation='nearest',cmap = 'gray')
                    plt.title(str(slices)+'Result')
                    plt.xticks([])
                    plt.yticks([])
                    plt.subplot(3, 4, 4+(sub_plt*4))
                    img_s = np.ma.masked_where(img_s == 0, img_s)
                    mask = np.ma.masked_where(mask == 0, mask)
                    plt.imshow(np.flipud(flair[slices, :, :]), interpolation='nearest',cmap = 'gray')
                    plt.imshow(np.flipud(mask[slices, :, :]), interpolation='nearest',cmap = 'autumn', alpha = 0.9)
                    plt.imshow(np.flipud(img_s[slices, :, :]), interpolation='nearest',cmap = 'cool', alpha = 0.6)
                    plt.title(str(slices)+'mix')
                    plt.xticks([])
                    plt.yticks([])
                    sub_plt += 1
        
                fig.savefig(os.path.join(img_outputDir,str(pid_test)+'_wo'+str(modality)+'_multi.pdf'),dpi = 1000)

    
#---------------------------------------------------------------------
                    
            i += 1



'''
Possible weights: weights/weights_three_datasets_one_channels_LOOV_384_uT1_TL_DO_sb_gen_aug_selected_ownres_T1_pid01_ens0_ep1000_lr5_bs8.h5
'''



