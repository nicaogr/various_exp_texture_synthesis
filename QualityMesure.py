#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  The goal of this script is to evaluate a quality metrics between the 
# synthetic images and the reference one
# The idea is to compute the distance of the distribution of the images 
# to do so we can use a KL distance at 3 different scale or 
# but maybe need to use a small number of bins for the histogram
# or compute alpha and etha then we have an explicit formula up to KL 
#  
# it is a quality measure after the synthesis, this quality measure is not
# used during synthesis process
#
#  Copyright 2019 gonthier <gonthier@Morisot>

import numpy as np
from scipy.ndimage.filters import gaussian_filter
from skimage.transform import resize
import os
import os.path
from scipy import fftpack
from skimage import io


from skimage.color import rgb2hsv
import pathlib
import pywt # Wavelet
import pickle
import Orange
import csv
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from matplotlib.patches import Polygon
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
import matplotlib.image as mpimg
import pandas as pd
matplotlib.rcParams['text.usetex'] = True
sns.set()
sns.set_style("whitegrid")

from shutil import copyfile    

from scipy.stats import gennorm
from scipy.special import gamma

import tikzplotlib

from DataForPerceptual_Evaluation import modify_underscore,modify_labels,modify_fontsizeByInput

import platform

if platform.system()=='Windows':
    os.environ["path"] += os.path.join('C:\\','Program Files','MiKTeX','miktex','bin','x64')
else:
   os.environ["PATH"] += os.path.join( 'usr','bin')

directory = "./im/References/"
ResultsDir = "./im/"
#if os.environ.get('OS','') == 'Windows_NT':
path_base  = os.path.join('C:\\','Users','gonthier')
ownCloudname = 'ownCloud'
if not(os.path.exists(path_base)):
    path_base  = os.path.join(os.sep,'media','gonthier','HDD')
    ownCloudname ='owncloud'
if os.path.exists(path_base):
    ResultsDir = os.path.join(path_base,ownCloudname,'These Gonthier Nicolas Partage','Images Textures Résultats')
    directory = os.path.join(path_base,ownCloudname,'These Gonthier Nicolas Partage','Images Textures References Subset')
    directory_betaTexture = os.path.join(path_base,ownCloudname,'These Gonthier Nicolas Partage','ForTexturePaper','Output','1024_Beta')
    dir_for_quality_measure = os.path.join(path_base,ownCloudname,'These Gonthier Nicolas Partage','ForTexturePaper','Output','QualityMeasure')
    dir_deplacement_carte = os.path.join(path_base,ownCloudname,'These Gonthier Nicolas Partage','Cartes_de_deplacements_SAID','Resultats_textures')
else:
    print(path_base,'not found')
    raise(NotImplementedError)


extension = ".png"
files = [file for file in os.listdir(directory) if file.lower().endswith(extension)]
listofmethod =['','_SAME_Gatys','_EfrosLeung','_EfrosFreeman',
'_SAME_Gatys_spectrumTFabs_eps10m16','MultiScale_o5_l3_8_psame',
'_DCor','_SAME_Gatys_MSSInit','_SAME_Gatys_spectrumTFabs_eps10m16_MSSInit'
,'_SAME_autocorr','_SAME_autocorr_MSSInit','1','2','3','4']
# Si vous voulez afficher plus de choses
#['','_SAME_Gatys','_EfrosLeung','_EfrosFreeman','_SAME_Gatys_spectrum','_SAME_Gatys_spectrumTFabs_eps10m16','MultiScale_o5_l3_8_psame','_DCor','_Gatys_Gang','_SAME_Gatys_MSSInit','_SAME_Gatys_spectrum_MSSInit','_SAME_Gatys_spectrumTFabs_eps10m16_MSSInit','_Gatys_Gang_MSInit','_SAME_autocorr','_SAME_autocorr_MSSInit','_SAME_phaseAlea_MSSInit']
# ,'_SAME_texture_spectrum_MSSInit','_SAME_phaseAlea'
listNameMethod = ['Reference','Gatys','Efros Leung','Efros Freeman','Gatys + Spectrum','Snelgrove','Deep Corr','Gatys + MSInit','Gatys + Spectrum + MSInit','Autocorr','Autocorr + MSInit','1 : OT Galerne Leclair','2 :Guisong method','3 : Tartavel','GAN Zalando Jetchev']
# listNameMethod = ['Reference','Gatys','EfrosLeung','EfrosFreeman','Gatys + Spectrum TF','Gatys + Spectrum TF eps10m16','Snelgorove','Deep Corr','Gang Spectrum Code','Gatys + MSInit','Gatys + Spectrum TF + MSInit','Gatys + Spectrum TF eps10m16 + MSInit','Gang code for MSInit','Autocorr','Autocorr + MSInit','PhaseAlea + MSInit']
#'Gatys + Spectrum + multi-scale Init','PhaseAlea'

listofmethod = ['','_SAME_Gatys','_SAME_Gatys_MSSInit','_SAME_Gatys_spectrumTFabs_eps10m16','_SAME_Gatys_spectrumTFabs_eps10m16_MSSInit',\
    '_SAME_autocorr','_SAME_autocorr_MSSInit','MultiScale_o5_l3_8_psame','_DCor','_EfrosLeung','_EfrosFreeman','_TextureNets']
listNameMethod = ['Reference','Gatys','Gatys + MSInit','Gatys + Spectrum','Gatys + Spectrum + MSInit',\
    'Autocorr','Autocorr + MSInit','Snelgrove','Deep Corr','Efros Leung','Efros Freeman','Ulyanov']

# The goal is to have the same order in the color plot
# ['Gatys','Gram + MSInit','Gram + Spectrum + MSInit','Snelgrove','Deep Corr'] doivent etre
# '#377eb8', '#ff7f00',      '#4daf4a'                ,'#f781bf', '#a65628'

CB_color_cycle = ['#377eb8', '#ff7f00','#984ea3', '#4daf4a','#A2C8EC','#e41a1c',
                  '#f781bf', '#a65628', '#dede00','#FFBC79','#999999']



listRegularImages = ['BrickRound0122_1_seamless_S',
                     'CRW_5751_1024',
                     'Pierzga_2006_1024',
                     'fabric_white_blue_1024',
                     'lego_1024',
                     'TexturesCom_BrickSmallBrown0473_1_M_1024',
                     'TexturesCom_FloorsCheckerboard0046_4_seamless_S_1024',
                     'TexturesCom_TilesOrnate0085_1_seamless_S',
                     'TexturesCom_TilesOrnate0158_1_seamless_S',
                     'metal_ground_1024']

# La difference entre la liste structured et la liste Regular est que la premiere contient tricot et la seconde CRW_5751_1024

listStructuredImages = ['BrickRound0122_1_seamless_S','fabric_white_blue_1024','lego_1024','metal_ground_1024','Pierzga_2006_1024','TexturesCom_BrickSmallBrown0473_1_M_1024',
    'TexturesCom_FloorsCheckerboard0046_4_seamless_S_1024','TexturesCom_TilesOrnate0085_1_seamless_S','TexturesCom_TilesOrnate0158_1_seamless_S','tricot_1024']



#trucEnPlus = ['_SAME_OnInput_autocorr','_SAME_OnInput_autocorr_MSSInit','_SAME_OnInput_SpectrumOnFeatures']

#listofmethod += trucEnPlus
#listNameMethod += trucEnPlus

cmap='viridis' 
#cmap='plasma' 
files_short = files
#files_short = [files[-1]]
#files_short = ['BrickRound0122_1_seamless_S.png']

def kl(p, q):
    p = np.asarray(p, dtype=np.float)
    q = np.asarray(q, dtype=np.float)

    return np.sum(np.where(p != 0, p * np.log(p / q), 0))

def smoothed_hist_kl_distance(a, b, nbins=10, sigma=1):
    ahist, bhist = (np.histogram(a, bins=nbins)[0],
                    np.histogram(b, bins=nbins)[0])

    asmooth, bsmooth = (gaussian_filter(ahist, sigma),
                        gaussian_filter(bhist, sigma))
    return kl(asmooth, bsmooth)
    
def hist_kl_distance(a, b, nbins=10):
    ahist, bhist = (np.histogram(a, bins=nbins,density=True)[0],
                    np.histogram(b, bins=nbins,density=True)[0])
    return kl(ahist, bhist)
    


def gennorm_kl_distance(a, b,verbose=False):
    beta_a,loc_a,scale_a = gennorm.fit(a) # beta =  shape parameter and scale = alpha
    beta_b,loc_b,scale_b = gennorm.fit(b)
    if verbose:
        print('beta_a,loc_a,scale_a')
        print(beta_a,loc_a,scale_a)
        print('beta_b,loc_b,scale_b')
        print(beta_b,loc_b,scale_b )
    D = np.log((beta_a*scale_b*gamma(1./beta_b)) / (beta_b*scale_a*gamma(1./beta_a))) +  (((scale_a/scale_b)**(beta_b)) * (gamma((beta_b+1)/beta_a)/gamma(1/beta_a))) - 1./beta_a

    return D

def plot_hist_of_coeffs(coeffs,namestr=''):
    
    n_bins= 50
    axes = []
    number_img_h = len(coeffs)-1
    number_img_w = 3
    #cAn = coeffs[0]
    plt.figure()
    gs00 = gridspec.GridSpec(number_img_h, number_img_w)
    list_str = ['cH','cV','cD']

    for j in range(number_img_w*number_img_h):
        ax = plt.subplot(gs00[j])
        axes += [ax]

    for k,ax in enumerate(axes):
        scale_ = (k // 3  ) + 1
        o_ = k % 3 # Orientation
#        print('scale_,o_',scale_,o_)
        coeffs_s_o = coeffs[scale_][o_]
        coeffs_s_o = coeffs_s_o.reshape(-1,3)
#        print('len(coeffs_s_o)',len(coeffs_s_o))
#        print('shape(coeffs_s_o)',coeffs_s_o.shape)
        title_local_str = list_str[o_] + str(len(coeffs)-scale_)
        _ = ax.hist(coeffs_s_o,n_bins, density=False,label=['R','G','B'],color=['r','g','b'])
        ax.tick_params(axis='both', which='major', labelsize=3)
        ax.tick_params(axis='both', which='minor', labelsize=3)
        ax.legend(loc='upper right', prop={'size': 2})
        ax.set_title(title_local_str)
    titre = 'DB4 coeffs ' +namestr
    plt.suptitle(titre)
    plt.show()


def computeKL_forbeta_images(ReDo=False):
    """
    compute the quality measure : KL between new and reference texture
    """
    
    files_short = ['TexturesCom_TilesOrnate0085_1_seamless_S.png']
    # path_output = os.path.join('Spectrum','Crops',str(dim))
    # pathlib.Path(path_output).mkdir(parents=True, exist_ok=True)
    verbose = False
    plot_hist = False
    With_formula = True # If False we will use the histogram
    number_of_scale = 3
    
    name = 'Wavelets_KL_'+str(number_of_scale)+'Scale'
    if With_formula:
        name += '_ExplicitFormula'
    else:
        name +=  '_Hist'
    name += '_forBetaValue'
    beta_list = [0.1,1,10,100,1000,10000,10**5,100000000]
    #name += 'OnlySum'
    name += '.pkl'

    local_path = pathlib.Path(__file__).parent.absolute()
    data_path_save = os.path.join(local_path,'data',name)
    if os.path.isfile(data_path_save):
        with open(data_path_save, 'rb') as pkl:
            data = pickle.load(pkl)
        if len(data)==2:
            dictTotal,dictTotal_all = data
        else:
            dictTotal = data
            dictTotal_all = {}
    else:
        dictTotal = {}
        dictTotal_all = {}
        
    #data_path_save = data_path_save.replace('OnlySum','')      
    
    wavelet_db4 = pywt.Wavelet('db4') # Daubechies D4 : lenght filter = 8
    # In this experiment, we employed the conventional pyramid
    # wavelet decomposition with three levels using the Daubechies’
    # maximally flat orthogonal filters of length 8 ( filters)

    listofmethod_beta = ['','_SAME_Gatys','_SAME_Gatys_MSSInit','_SAME_Gatys_spectrumTFabs_eps10m16','_SAME_Gatys_spectrumTFabs_eps10m16_MSSInit']
    listNameMethod_beta = ['Reference','Gatys','Gatys + MSInit','Gatys + Spectrum TF','Gatys + Spectrum TF + MSInit']

    for file in files_short:
        filewithoutext = '.'.join(file.split('.')[:-1])
        print('Image :',filewithoutext)
        filewithoutextreplaced = filewithoutext.replace('_','$\_$')
        dict_imgs = {}
        
        # Load the images
        for i,zipped in enumerate(zip(listofmethod_beta,listNameMethod_beta)):
            method,nameMethod = zipped
            
            if 'spectrumTFabs' in method:
                beta_list_local = beta_list
            else:
                beta_list_local = [0.0]
                
            for beta in beta_list_local:
                
                if method =='':
                    stringname = os.path.join(directory,filewithoutext + method)
                    nameMethod_local = nameMethod
                elif method =='_SAME_Gatys' or method=='_SAME_Gatys_MSSInit':
                    stringname = os.path.join(ResultsDir,filewithoutext,filewithoutext + method)
                    nameMethod_local = nameMethod
                else:
                    stringname = os.path.join(directory_betaTexture,filewithoutext,filewithoutext + method)
                    if not(beta==0.0):
                        stringname = stringname.replace('_SAME','_SAME_beta'+str(beta))
                        nameMethod_local = nameMethod + str(beta)
                    else:
                        nameMethod_local = nameMethod
                        
                print(method,nameMethod,beta)
                stringnamepng = stringname + '.png'
                stringnamejpg = stringname + '.jpg'
                if os.path.isfile(stringnamepng):
                    filename = stringnamepng
                    image_available = True
                elif os.path.isfile(stringnamejpg):
                    filename = stringnamejpg
                    image_available = True
                else:
                    print('Neither',stringnamepng,' or ',stringnamejpg,'exist. Wrong path  or image not yet computed ?')
                    image_available = False
                #print(filename)
                if image_available:
                    imagergb = io.imread(filename)
                    
                    # Multilevel 2D Discrete Wavelet Transform. if level = None take the maximum
                    coeffs = pywt.wavedec2(imagergb, wavelet_db4, mode='symmetric', level=number_of_scale,\
                                  axes=(0,1))
                    
                    if plot_hist:
                        plot_hist_of_coeffs(coeffs,namestr=nameMethod)
                    # len(coeffs)  = level + 1 
                    
                    dict_imgs[nameMethod_local] = coeffs
        
#        # Compute the metrics between the reference and the images

        dict_all_scores = {}
        dict_scores = {}
        for method,nameMethod in zip(listofmethod_beta,listNameMethod_beta):
            if nameMethod=='Reference': # Reference one
                continue
            if 'spectrumTFabs' in method:
                beta_list_local = beta_list
            else:
                beta_list_local = [0.0]
                
            for beta in beta_list_local:
                # Check if the score already exist
                if filewithoutext in  dictTotal.keys():
                    dict_scores_local =  dictTotal[filewithoutext]
                    if nameMethod in list(dict_scores_local.keys()):
                        print('Already computed :',filewithoutext,nameMethod)
                        dict_scores[nameMethod] = dict_scores_local[nameMethod]
                        if filewithoutext in list(dictTotal_all.keys()):
                            dict_all_scores_local = dictTotal_all[filewithoutext]
                            if nameMethod in dict_all_scores_local.keys():
                                dict_all_scores[nameMethod] = dict_all_scores_local[nameMethod]
                        continue
                if not(beta==0.0):
                    nameMethod_local = nameMethod + str(beta)
                else:
                    nameMethod_local = nameMethod

                ref_coeff = dict_imgs['Reference']
                syn_coeff = dict_imgs[nameMethod_local]
                dict_all_scores[nameMethod_local] = []
                dict_scores[nameMethod_local] = 0.
    #            ref_img = dict_imgs['Reference']
    #            syn_img = dict_imgs[nameMethod]
                for s in range(number_of_scale+1): # scale
                    if s==0:
                        # Average case : cAn : ie approximation at rank n 
                        # we will pass it 
                        cAn = ref_coeff[s]
                        continue
                    else:
                        # (cHn, cVn, cDn) : the coefficient are provide in the decreasing
                        # order
                        (ref_cHn, ref_cVn, ref_cDn) = ref_coeff[s]
                        (syn_cHn, syn_cVn, syn_cDn) = syn_coeff[s]
                        # We will extract 2 * 9  parameters (2 per generalised gaussian, for 3 scale times 3 orientations)
                        o = 0
                        for ref_coeffs_s_o,syn_coeffs_s_o in zip([ref_cHn, ref_cVn, ref_cDn],[syn_cHn, syn_cVn, syn_cDn]):
                            for c in range(3): # Color channet
                                ref_coeffs_s_o_c = ref_coeffs_s_o[:,:,c].ravel()
                                syn_coeffs_s_o_c = syn_coeffs_s_o[:,:,c].ravel()
                                
                                if With_formula:
                                    # KL divergence with explicit formula
                                    gennorm_kl_s_o_c = gennorm_kl_distance(ref_coeffs_s_o_c, syn_coeffs_s_o_c,verbose=verbose)
                                    if verbose : print('kl with gennorm at s : ',s,'o : ',o,'c : ',c,' = ',gennorm_kl_s_o_c)
                                    dict_all_scores[nameMethod_local] += [gennorm_kl_s_o_c]
                                    dict_scores[nameMethod_local] += gennorm_kl_s_o_c
                                else:
                                    # Use Histogram to estimate KL divergence
                                    hist_kl_s_c = hist_kl_distance(ref_coeffs_s_o_c, syn_coeffs_s_o_c, nbins=10)
                                    if verbose : print('kl with hist at s : ',s,'o : ',o,'c : ',c,' = ',hist_kl_s_c)
                                    dict_all_scores[nameMethod_local] += [hist_kl_s_c]
                                    dict_scores[nameMethod_local] += hist_kl_s_c
                                
                            o += 1
                # Print one global score = sum at different scale of the different orientation and for the 3 color     
                if With_formula:       
                    print('Reference against ',nameMethod_local,' ',dict_scores[nameMethod_local])
                else:
                    print('Reference against ',nameMethod_local,' ',dict_scores_hist[nameMethod_local],' with hist')
        dictTotal[filewithoutext] = dict_scores
        dictTotal_all[filewithoutext] = dict_all_scores
    data = dictTotal,dictTotal_all
    with open(data_path_save, 'wb') as pkl:
        pickle.dump(data,pkl)
        
def main(ReDo=False,number_of_scale = 3):
    """
    compute the quality measure : KL between new and reference texture
    @param : number_of_scale : number of scale in the wavelets decomposition 
        = None for automatic computation
    """
    # path_output = os.path.join('Spectrum','Crops',str(dim))
    # pathlib.Path(path_output).mkdir(parents=True, exist_ok=True)
    verbose = False
    plot_hist = False
    With_formula = True # If False we will use the histogram
    
    
    name = 'Wavelets_KL_'+str(number_of_scale)+'Scale'
    if With_formula:
        name += '_ExplicitFormula'
    else:
        name +=  '_Hist'

    #name += 'OnlySum'
    name += '.pkl'
    data_path_save = os.path.join('data',name)
    if os.path.isfile(data_path_save):
        with open(data_path_save, 'rb') as pkl:
            data = pickle.load(pkl)
        if len(data)==2:
            dictTotal,dictTotal_all = data
        else:
            dictTotal = data
            dictTotal_all = {}
    else:
        dictTotal = {}
        dictTotal_all = {}
        
    #data_path_save = data_path_save.replace('OnlySum','')      
    
    wavelet_db4 = pywt.Wavelet('db4') # Daubechies D4 : lenght filter = 8
    # In this experiment, we employed the conventional pyramid
    # wavelet decomposition with three levels using the Daubechies’
    # maximally flat orthogonal filters of length 8 ( filters)

    for file in files_short:
        filewithoutext = '.'.join(file.split('.')[:-1])
        print('Image :',filewithoutext)
        filewithoutextreplaced = filewithoutext.replace('_','$\_$')
        dict_imgs = {}
        
        # Load the images
        for i,zipped in enumerate(zip(listofmethod,listNameMethod)):
            method,nameMethod = zipped
            
            if method =='':
                stringname = os.path.join(directory,filewithoutext + method)
            else:
                stringname = os.path.join(ResultsDir,filewithoutext,filewithoutext + method)
            #print(method,nameMethod)
            stringnamepng = stringname + '.png'
            stringnamejpg = stringname + '.jpg'
            if os.path.isfile(stringnamepng):
                filename = stringnamepng
            elif os.path.isfile(stringnamejpg):
                filename = stringnamejpg
            else:
                print('Neither',stringnamepng,' or ',stringnamejpg,'exist. Wrong path ?')
            #print(filename)
            imagergb = io.imread(filename)
            
            # Multilevel 2D Discrete Wavelet Transform. if level = None take the maximum
            coeffs = pywt.wavedec2(imagergb, wavelet_db4, mode='symmetric', level=number_of_scale,\
                          axes=(0,1))
            
            if plot_hist:
                plot_hist_of_coeffs(coeffs,namestr=nameMethod)
            # len(coeffs)  = level + 1 
            
            dict_imgs[nameMethod] = coeffs
        
#        # Compute the metrics between the reference and the images

        dict_all_scores = {}
        dict_scores = {}
        for method,nameMethod in zip(listofmethod,listNameMethod):
            if nameMethod=='Reference': # Reference one
                continue
            # Check if the score already exist
            if filewithoutext in  dictTotal.keys():
                dict_scores_local =  dictTotal[filewithoutext]
                if nameMethod in list(dict_scores_local.keys()):
                    print('Already computed :',filewithoutext,nameMethod)
                    dict_scores[nameMethod] = dict_scores_local[nameMethod]
                    if filewithoutext in list(dictTotal_all.keys()):
                        dict_all_scores_local = dictTotal_all[filewithoutext]
                        if nameMethod in dict_all_scores_local.keys():
                            dict_all_scores[nameMethod] = dict_all_scores_local[nameMethod]
                    continue

            ref_coeff = dict_imgs['Reference']
            syn_coeff = dict_imgs[nameMethod]
            dict_all_scores[nameMethod] = []
            dict_scores[nameMethod] = 0.
#            ref_img = dict_imgs['Reference']
#            syn_img = dict_imgs[nameMethod]
            len_ref_coeff = len(ref_coeff)
            for s in range(len_ref_coeff): # scale
                if s==0:
                    # Average case : cAn : ie approximation at rank n 
                    # we will pass it 
                    cAn = ref_coeff[s]
                    continue
                else:
                    # (cHn, cVn, cDn) : the coefficient are provide in the decreasing
                    # order
                    (ref_cHn, ref_cVn, ref_cDn) = ref_coeff[s]
                    (syn_cHn, syn_cVn, syn_cDn) = syn_coeff[s]
                    # We will extract 2 * 9  parameters (2 per generalised gaussian, for 3 scale times 3 orientations)
                    o = 0
                    for ref_coeffs_s_o,syn_coeffs_s_o in zip([ref_cHn, ref_cVn, ref_cDn],[syn_cHn, syn_cVn, syn_cDn]):
                        for c in range(3): # Color channet
                            ref_coeffs_s_o_c = ref_coeffs_s_o[:,:,c].ravel()
                            syn_coeffs_s_o_c = syn_coeffs_s_o[:,:,c].ravel()
                            
                            if With_formula:
                                # KL divergence with explicit formula
                                gennorm_kl_s_o_c = gennorm_kl_distance(ref_coeffs_s_o_c, syn_coeffs_s_o_c,verbose=verbose)
                                if verbose : print('kl with gennorm at s : ',s,'o : ',o,'c : ',c,' = ',gennorm_kl_s_o_c)
                                dict_all_scores[nameMethod] += [gennorm_kl_s_o_c]
                                dict_scores[nameMethod] += gennorm_kl_s_o_c
                            else:
                                # Use Histogram to estimate KL divergence
                                hist_kl_s_c = hist_kl_distance(ref_coeffs_s_o_c, syn_coeffs_s_o_c, nbins=10)
                                if verbose : print('kl with hist at s : ',s,'o : ',o,'c : ',c,' = ',hist_kl_s_c)
                                dict_all_scores[nameMethod] += [hist_kl_s_c]
                                dict_scores[nameMethod] += hist_kl_s_c
                            
                        o += 1
            # Print one global score = sum at different scale of the different orientation and for the 3 color     
            if With_formula:       
                print('Reference against ',nameMethod,dict_scores[nameMethod])
            else:
                print('Reference against ',nameMethod,dict_scores_hist[nameMethod],' with hist')
        dictTotal[filewithoutext] = dict_scores
        dictTotal_all[filewithoutext] = dict_all_scores
    data = dictTotal,dictTotal_all
    with open(data_path_save, 'wb') as pkl:
        pickle.dump(data,pkl)

def readData():
    With_formula = True # If False we will use the histogram
    number_of_scale = 3
    
    name = 'Wavelets_KL_'+str(number_of_scale)+'Scale'
    if With_formula:
        name += '_ExplicitFormula'
    else:
        name +=  '_Hist'

    name += '.pkl'
    data_path_save = os.path.join('data',name)
    with open(data_path_save, 'rb') as pkl:
         data = pickle.load(pkl)
    dict_all_scores,dict_scores = data
    print(dict_scores)
    
def readDataAndPlot(OnlyStructuredImages=False,
                    OnlySubset_of_methods=False,
                    ReadWhat='KL',
                    save_or_show=True,d=1,
                    number_of_scale = 3,
                    output_img='png'):
    """
    This function will read the images synthesis and plot the quality 
    measure based on Wavelet coefficients
    For Texture paper
    @param : OnlyStructuredImages : we will only plot the regular images
    @param ReadWhat == KL plot the KL method 
    @param ReadWhat == DisplacementScore plot the DisplacementScore of the methods
    @param : if save_or_show = True we save the figure, otherwise we only show it
    @param : d = 1 distance used for thresholding in the displacement maps
    @param :  number_of_scale = 3 number of scale for the wavelet decomposition
    @param : output_img == png for saving png figures
                ==tikz for save tikzpicture for tex
    """
    
#    listStructuredImages = ['BrickRound0122_1_seamless_S','fabric_white_blue_1024','lego_1024','metal_ground_1024','Pierzga_2006_1024','TexturesCom_BrickSmallBrown0473_1_M_1024',
#        'TexturesCom_FloorsCheckerboard0046_4_seamless_S_1024','TexturesCom_TilesOrnate0085_1_seamless_S','TexturesCom_TilesOrnate0158_1_seamless_S','tricot_1024']
   
    pathlib.Path(dir_for_quality_measure).mkdir(parents=True, exist_ok=True)
    if not(save_or_show):
        plt.ion()
        
    if output_img=='tikz':
        plt.rc('text', usetex=True)
    
    if ReadWhat=='KL':
        case_str = 'KL'
        if not(number_of_scale==3):
            case_str += '_NScale'+str(number_of_scale)
        leg_str = 'KL'
        With_formula = True # If False we will use the histogram
        
        name = 'Wavelets_KL_'+str(number_of_scale)+'Scale'
        if With_formula:
            name += '_ExplicitFormula'
        else:
            name +=  '_Hist'

        #name += 'OnlySum'
        name += '.pkl'
        data_path_save = os.path.join('data',name)
        if not(os.path.isfile(data_path_save)):
            data_path_save = os.path.join(dir_for_quality_measure,name)
        print('The wavelet KL score are store in ',data_path_save)
        with open(data_path_save, 'rb') as pkl:
             data = pickle.load(pkl)
        # print(len(data))
        # print(data)
        if len(data)==2:
            dict_scores,dict_all_scores = data
        else:
            dict_scores = data
        print(dict_scores)
        save_name_csv = 'KL_methods.csv'
    elif ReadWhat=='DisplacementScore':
        case_str = 'DS'
        leg_str = 'Displacement'
        name = 'Displacements_Score'
        if not(d==1):
            name+='_d'+str(d)
            case_str +='_d'+str(d)
            leg_str = 'Displacement d = '+str(d)
        name += '.pkl'
        data_path_save = os.path.join('data',name)
        if not(os.path.isfile(data_path_save)):
            data_path_save = os.path.join(dir_for_quality_measure,name)
        with open(data_path_save, 'rb') as pkl:
             data = pickle.load(pkl)
        dict_scores = data
        save_name_csv = 'DS_methods.csv'
    # Save to csv file 
    firstLine = True

    with open(save_name_csv, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for texture_name, dico in dict_scores.items():
            if firstLine:
                methodsname = list(dico.keys())
                print(methodsname)
                methodsname = [''] + methodsname
                writer.writerow(methodsname)
                firstLine = False
            v = list(dico.values())
            v = [texture_name] + v
            writer.writerow(v)
        
    list_markers = ['o','s','X','*','v','^','<','>','d','1','2','3','4','8','h','H','p','d','$f$','P']
        
    dicoOfMethods = {}
    
    if OnlySubset_of_methods: 
        list_methods = ['Gatys','Gatys + MSInit','Gatys + Spectrum TF + MSInit',\
                                    'Snelgorove','Deep Corr']
        list_methods = ['Gatys','Gatys + MSInit','Gatys + Spectrum + MSInit',\
                                    'Snelgrove','Deep Corr']
        if output_img=='png':
            list_methods_withoutTF = ['Gatys','Gram +\n MSInit','Gram +\n Spectrum +\n MSInit',\
                                    'Snelgrove','Deep Corr']
        elif output_img=='tikz':
            list_methods_withoutTF = [r'Gatys \cite{gatys_texture_2015}',r'Gram + MSInit',r'Gram + Spectrum + MSInit',\
                                                           r'Snelgrove \cite{snelgrove_highresolution_2017}',r'Deep Corr \cite{sendik_deep_2017}']

    else:
        list_methods = ['Gatys','Gatys + MSInit','Gatys + Spectrum TF','Gatys + Spectrum TF + MSInit', 'Autocorr', \
                        'Autocorr + MSInit','Snelgorove','Deep Corr','EfrosLeung','EfrosFreeman','Ulyanov']
        list_methods = ['Gatys','Gatys + MSInit','Gatys + Spectrum','Gatys + Spectrum + MSInit', 'Autocorr', \
                        'Autocorr + MSInit','Snelgrove','Deep Corr','Efros Leung','Efros Freeman','Ulyanov']
        if output_img=='png':
            list_methods_withoutTF = ['Gatys','Gram +\n MSInit','Gram +\n Spectrum','Gram +\n Spectrum +\n MSInit', 'Autocorr', \
                        'Autocorr +\n MSInit','Snelgrove','Deep Corr','Efros Leung','Efros Freeman','Ulyanov'] # IE the string used in the figure as label 
        elif output_img=='tikz':
            list_methods_withoutTF = [r'Gatys \cite{gatys_texture_2015}',r'Gram + MSInit',r'Gram + Spectrum',r'Gram + Spectrum + MSInit',r'Autocorr', \
                        r'Autocorr + MSInit',r'Snelgrove \cite{snelgrove_highresolution_2017}',r'Deep Corr \cite{sendik_deep_2017}',r'Efros Leung \cite{efros_texture_1999}',r'Efros Freeman \cite{efros_image_2001}',r'Ulyanov \cite{ulyanov2016} '] # IE the string used in the figure as label 
       
    
    NUM_COLORS = len(list_methods)
    color_number_for_frozen = [0,NUM_COLORS//2,NUM_COLORS-1]
    cm = plt.get_cmap('gist_rainbow')
    cNorm  = colors.Normalize(vmin=0, vmax=NUM_COLORS-1)
    scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
    
    for method in list_methods:
        dicoOfMethods[method] = []
    
    print(dict_scores)
    listnameIm = []
    if OnlyStructuredImages:
        numberImages = len(listRegularImages)
    else:
        numberImages = len(dict_scores.keys())
    number_of_methods = len(list_methods)
    print('len(list_methods)',number_of_methods)
    listOfRank = np.zeros((numberImages,number_of_methods))
    ki = 0
    if OnlyStructuredImages:
        ext_name = 'Struct_'
    else:
        ext_name = ''
        
    if OnlySubset_of_methods:
        ext_name += 'SubsetOfMethods_'
    
    for k in dict_scores.keys(): # Loop on images
        if OnlyStructuredImages:
            if not(k in listRegularImages):
                continue
        dico = dict_scores[k]
        # print(k,dico)
        # print(dico.keys())
        listnameIm += [k]
        list_scores = []
        for method in list_methods:
            # print(method)
            if method in dico.keys():
                
                dicoOfMethods[method] += [dico[method]]
                list_scores  += [dico[method]]
        indice = np.argsort(list_scores)
        rank = np.zeros((number_of_methods,))
        for j,indice_j in enumerate(indice):
             rank[indice_j] = j+1
        print(k,list_scores,rank)
        listOfRank[ki,:] = rank
        ki += 1
    print(listOfRank)
    meanRank = np.mean(listOfRank,axis=0)
    print('MeanRank',meanRank)
    # mean Rank
    argsort_ofMeanRank = np.argsort(meanRank)
    
    sorted_meanRank = meanRank[argsort_ofMeanRank]
    sorted_methods = np.array(list_methods)[argsort_ofMeanRank]
    i = 0
    for mR,method in zip(sorted_meanRank,sorted_methods):
        print(i,method,' mean rank : ',mR)
        i += 1
    
    
    # rank_ofMeanRank = np.argsort(meanRank)
    # print(rank_ofMeanRank)
    # for i in range(len(list_methods)):
        # for ri,r in enumerate(rank_ofMeanRank):
            # if r==i:
                # print(i,list_methods[ri],' mean rank : ',meanRank[ri])
    
    # Critical Diagram 
    if output_img=='tikz':
        print('Not possible to save critical diagram in tikz')
    else:
        cd = Orange.evaluation.compute_CD(meanRank, numberImages) #tested on numberImages images
        Orange.evaluation.graph_ranks(meanRank, list_methods_withoutTF, cd=cd, width=8, textspace=1.5)
        if save_or_show:
            matplotlib.use('Agg')
            plt.tight_layout()
            path_fig = os.path.join(dir_for_quality_measure,ext_name+case_str+'_CD.png')
            plt.savefig(path_fig,bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    
    # Value plot
           
#    
    
    # Boxplots
    if output_img=='png':
        fig, ax1 = plt.subplots(figsize=(10, 6))
    elif output_img=='tikz':
        fig, ax1 = plt.subplots()
        
    fig.canvas.set_window_title('Boxplots of the '+leg_str+' distances.')
    #fig.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)plt.figure()    
#    fig_i_c = 0
#    x = list(range(0,len(listnameIm)))
#    for method,labelstr in zip(list_methods,list_methods_withoutTF):
#        #print(method) 
#        #print(dicoOfMethods[method])
#        plt.plot(x,dicoOfMethods[method],label=labelstr,color=CB_color_cycle[fig_i_c],\
#                         marker=list_markers[fig_i_c],linestyle='')# color=scalarMap.to_rgba(fig_i_c)
#        fig_i_c+=1
#    
#    listnameIm_without1024 = []
#    for elt in listnameIm:
#        elt_wt1024 = elt.replace('_1024','')
#        elt_wt1024 = elt_wt1024.replace('_seamless_S','')
#        elt_wt1024 = elt_wt1024.replace('TexturesCom_','')
#        listnameIm_without1024+= [elt_wt1024]
#
#    title = leg_str+' score computed with Wavelets coeffs'
#    #plt.xticks(x, listnameIm, rotation='vertical')
#    plt.xticks(x, listnameIm_without1024, rotation=90,fontsize=5)
#    plt.ylabel(leg_str+' score')
#    plt.ylim(bottom=0.)  # adjust the bottom leaving top unchanged
#    plt.title(title)
#    plt.legend(loc='best')
#    if save_or_show:
#        
#        if output_img=='png':
#            plt.tight_layout()
#            path_fig = os.path.join(dir_for_quality_measure,ext_name+case_str+'.png')
#            plt.savefig(path_fig,bbox_inches='tight')
#            plt.close()
#        if output_img=='tikz':
#            path_fig = os.path.join(dir_for_quality_measure,ext_name+case_str+'.tex')
#            #tikzplotlib.save(path_fig)
#            #modify_underscore(path_fig) # PB il va y avoir un probleme entre les 
#            # cas cite et les cas non cite il faudra regler cela plus tard  peut etre !!
#            #modify_labels(path_fig)
#    else:
#        plt.show()
#    
#    # Log(x)
#    plt.figure()    
#    fig_i_c = 0
#    x = list(range(0,len(listnameIm)))
#    for method,labelstr in zip(list_methods,list_methods_withoutTF): 
#        #labelstr = method
#        # print(dicoOfMethods[method])
#        plt.plot(x,np.log(np.array(dicoOfMethods[method])),label=labelstr,color=CB_color_cycle[fig_i_c],\
#                         marker=list_markers[fig_i_c],linestyle='') # color = scalarMap.to_rgba(fig_i_c)
#        fig_i_c+=1
#
#    title = 'Log '+leg_str+'score computed with Wavelets coeffs'
#    #plt.xticks(x, listnameIm, rotation='vertical')
#    plt.xticks(x, listnameIm_without1024, rotation=90,fontsize=5)
#    plt.ylabel('log ('+leg_str+' score)')
#    plt.title(title)
#    plt.legend(loc='best')
#    if save_or_show:
#    
#        if output_img=='png':
#            plt.tight_layout()
#            path_fig = os.path.join(dir_for_quality_measure,ext_name+'log'+case_str+'.png')
#            plt.savefig(path_fig,bbox_inches='tight')
#            plt.close()
#        if output_img=='tikz':
#            path_fig = os.path.join(dir_for_quality_measure,ext_name+'log'+case_str+'.tex')
#            #tikzplotlib.save(path_fig)
#            #modify_underscore(path_fig)
#            #modify_labels(path_fig)
#    else:
#        plt.show() 
#        plt.pause(0.001)
#    
#    
#    # Mean of KL
#    plt.figure()    
    list_KLs = []
    for i,method in enumerate(list_methods): 
        labelstr = list_methods_withoutTF[i]
        # print(dicoOfMethods[method])
        KLs = np.array(dicoOfMethods[method])
        list_KLs += [KLs]
#        meanKL = np.mean(KLs)
#        stdKL = np.std(KLs)
#        plt.errorbar(i, meanKL, yerr=stdKL,label=labelstr,color=CB_color_cycle[i],\
#                          marker=list_markers[i],linestyle='', markersize=8,uplims=True, lolims=True)
#
#    title = 'Mean and std of '+leg_str+' score per method.'
#    plt.xticks(list(range(0,len(list_methods))), list_methods, rotation=45,fontsize=8)
#    plt.ylabel('Mean '+leg_str+' score')
#    plt.title(title)
#    plt.legend(loc='best')
#    if save_or_show:
#        if output_img=='png':
#            plt.tight_layout()
#            path_fig = os.path.join(dir_for_quality_measure,ext_name+case_str+'_MeanStd_per_method.png')
#            plt.savefig(path_fig,bbox_inches='tight')
#            plt.close()
#        if output_img=='tikz':
#            path_fig = os.path.join(dir_for_quality_measure,ext_name+case_str+'_MeanStd_per_method.tex')
#            tikzplotlib.save(path_fig)
#            modify_underscore(path_fig)
#            modify_labels(path_fig)
#        
#    else:
#        plt.show()
#
    #bp = ax1.boxplot(list_KLs, notch=0, sym='+', vert=1, whis=1.5)
    bp = ax1.boxplot(list_KLs, notch=0, sym='+')
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='black', marker='+')
    # Hide these grid behind plot objects
    ax1.set_axisbelow(True)
    #ax1.set_title('Comparison of '+leg_str+' score for different methods')
    ax1.set_xlabel('Method')
    ax1.set_ylabel(leg_str)
    
    medians = np.empty(len(list_methods))
    for i in range(len(list_methods)):
        box = bp['boxes'][i]
        boxX = []
        boxY = []
        for j in range(5):
            boxX.append(box.get_xdata()[j])
            boxY.append(box.get_ydata()[j])
        box_coords = np.column_stack([boxX, boxY])
        # Color of the box
        ax1.add_patch(Polygon(box_coords, facecolor=CB_color_cycle[i],alpha=0.5))
        # Now draw the median lines back over what we just filled in
        med = bp['medians'][i]
        medianX = []
        medianY = []
        for j in range(2):
            medianX.append(med.get_xdata()[j])
            medianY.append(med.get_ydata()[j])
            ax1.plot(medianX, medianY, 'k')
        # Finally, overplot the sample averages, with horizontal alignment
        # in the center of each box
        if output_img=='png':
            ax1.plot(np.average(med.get_xdata()), np.average(list_KLs[i]),
                 color='w', marker='*', markeredgecolor='k', markersize=8)
        elif output_img=='tikz':
            ax1.plot(np.average(med.get_xdata()), np.average(list_KLs[i]),
                 color='w', marker='h', markeredgecolor='k', markersize=6)
    # X labels
    if output_img=='png':
        ax1.set_xticklabels(list_methods_withoutTF,
                    rotation=45, fontsize=8) 
    elif output_img=='tikz':
        ax1.set_xticklabels(list_methods_withoutTF,
                    rotation=75, fontsize=8)    
    if save_or_show:
        if output_img=='png':
            plt.tight_layout()
            path_fig = os.path.join(dir_for_quality_measure,ext_name+case_str+'_Boxplots_per_method.png')
            plt.savefig(path_fig,bbox_inches='tight')
            plt.close()
        if output_img=='tikz':
            path_fig = os.path.join(dir_for_quality_measure,ext_name+case_str+'_Boxplots_per_method.tex')
            tikzplotlib.save(path_fig)
            modify_underscore(path_fig)
            modify_labels(path_fig)
            modify_fontsizeByInput(path_fig)
    else:
        plt.show()
        input('Enter to close.')
        plt.close()
        
    # Boxplots of log values
    list_KLs_log = []
    for elt in list_KLs:
        list_KLs_log += [np.log(elt)]
    if output_img=='png':
        fig, ax1 = plt.subplots(figsize=(10, 6))
    elif output_img=='tikz':
        fig, ax1 = plt.subplots()
    #fig.canvas.set_window_title('Boxplots of the log '+leg_str+' distances.') 
    #fig.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)
#
    #bp = ax1.boxplot(list_KLs_log, notch=0, sym='+', vert=1, whis=1.5)
    
    #g =sns.boxplot(y=list_KLs_log,x=list_methods,showmeans=True)
    #g.set_xticklabels(labels=list_methods,rotation=45)
    bp = ax1.boxplot(list_KLs_log, notch=0, sym='+')
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='black', marker='+')
    # Hide these grid behind plot objects
    ax1.set_axisbelow(True)
    #ax1.set_title('Comparison of log '+leg_str+' score for different methods') # No title
    #ax1.set_xlabel('Method')
    ax1.set_ylabel('log '+leg_str)
    
    medians = np.empty(len(list_methods))
    for i in range(len(list_methods)):
        box = bp['boxes'][i]
        boxX = []
        boxY = []
        for j in range(5):
            boxX.append(box.get_xdata()[j])
            boxY.append(box.get_ydata()[j])
        box_coords = np.column_stack([boxX, boxY])
        # Color of the box
        ax1.add_patch(Polygon(box_coords, facecolor=CB_color_cycle[i],alpha=0.5))
        # Now draw the median lines back over what we just filled in
        med = bp['medians'][i]
        medianX = []
        medianY = []
        for j in range(2):
            medianX.append(med.get_xdata()[j])
            medianY.append(med.get_ydata()[j])
            ax1.plot(medianX, medianY, 'k')
        # Finally, overplot the sample averages, with horizontal alignment
        # in the center of each box
        if output_img=='png':
            ax1.plot(np.average(med.get_xdata()), np.average(list_KLs_log[i]),
                 color='w', marker='*', markeredgecolor='k', markersize=8)
        elif output_img=='tikz':
            ax1.plot(np.average(med.get_xdata()), np.average(list_KLs_log[i]),
                 color='w', marker='h', markeredgecolor='k', markersize=6)
    # X labels
    if output_img=='png':
        ax1.set_xticklabels(list_methods_withoutTF,
                    rotation=45, fontsize=8) 
    elif output_img=='tikz':
        ax1.set_xticklabels(list_methods_withoutTF,
                    rotation=75, fontsize=8)  #,fontdict={'horizontalalignment': 'center'}
    if save_or_show:
        if output_img=='png':
            plt.tight_layout()
            path_fig = os.path.join(dir_for_quality_measure,ext_name+case_str+'_logBoxplots_per_method.png')
            plt.savefig(path_fig,bbox_inches='tight')
            plt.close()
        if output_img=='tikz':
            path_fig = os.path.join(dir_for_quality_measure,ext_name+case_str+'_logBoxplots_per_method.tex')
            tikzplotlib.save(path_fig)
            modify_underscore(path_fig)
            modify_labels(path_fig)
            modify_fontsizeByInput(path_fig)
        
    else:
        plt.show()
        input('Enter to close.')
        plt.close()
    
def Plot_KL_forDiffBetaValues(OnlyStructuredImages=False):
    """
    This function will plot the quality  measure based on Wavelet coefficients
    For different beta values 
    """
    
    flatten = lambda l: [item for axes in l for item in axes]
    
    beta_list = [0.1,1,10,100,1000,10000,10**5,100000000]
    

    plt.ion()
    With_formula = True # If False we will use the histogram
    number_of_scale = 3
    
    name = 'Wavelets_KL_'+str(number_of_scale)+'Scale'
    if With_formula:
        name += '_ExplicitFormula'
    else:
        name +=  '_Hist'
    name += '_forBetaValue'
    #name += 'OnlySum'
    name += '.pkl'
    local_path = pathlib.Path(__file__).parent.absolute()
    data_path_save = os.path.join(local_path,'data',name)
    print('The wavelet KL score are store in ',data_path_save)
    with open(data_path_save, 'rb') as pkl:
         data = pickle.load(pkl)
    print(len(data))
    print(data)
    if len(data)==2:
        dict_scores,dict_all_scores = data
    else:
        dict_scores = data
    print(dict_scores)

    # Save to csv file 
    firstLine = True

    with open('KL_methods_betavalues.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for texture_name, dico in dict_scores.items():
            if firstLine:
                methodsname = list(dico.keys())
                print(methodsname)
                methodsname = [''] + methodsname
                writer.writerow(methodsname)
                firstLine = False
            v = list(dico.values())
            v = [texture_name] + v
            writer.writerow(v)
        
    list_markers = ['o','s','X','*','v','^','<','>','d','1','2','3','4','8','h','H','p','d','$f$','P']
        
    dicoOfMethods = {}
    list_methods = ['Gatys','Gatys + MSInit','Gatys + Spectrum TF','Gatys + Spectrum TF + MSInit', 'Autocorr', \
        'Autocorr + MSInit','Snelgorove','Deep Corr','EfrosLeung','EfrosFreeman','Ulyanov']
    
    list_methodsGatysPlusSpectrum = ['Gatys']
    list_methodsGatysPlusSpectrum_ext = ['_SAME_Gatys']
    
    nameMethod = 'Gatys + Spectrum TF'
    nameMethodextBegin = '_SAME'
    nameMethodextEnd = '_Gatys_spectrumTFabs_eps10m16'
    for beta in beta_list:
        list_methodsGatysPlusSpectrum += [nameMethod + str(beta)]
        list_methodsGatysPlusSpectrum_ext += [nameMethodextBegin +'_beta'+ str(beta)+nameMethodextEnd]
    list_methodsMSINIt = ['Gatys + MSInit']
    list_methodsMSINIt_ext = ['_SAME_Gatys_MSSInit']
    nameMethod = 'Gatys + Spectrum TF + MSInit'
    nameMethodextBegin = '_SAME'
    nameMethodextEnd = '_Gatys_spectrumTFabs_eps10m16_MSSInit'
    for beta in beta_list:
        list_methodsMSINIt += [nameMethod + str(beta)]
        list_methodsMSINIt_ext += [nameMethodextBegin +'_beta'+ str(beta)+nameMethodextEnd]
    
    minimum_beta =10**(-9)
    beta_list_plusZero = [minimum_beta]+beta_list
    labellist = ['$-\infty$']
    for beta in beta_list:
        labellist += ['{}'.format(int(np.log10(beta)))]
    
    for method in list_methods:
        dicoOfMethods[method] = []
    
    print(dict_scores)
    listnameIm = []
    if OnlyStructuredImages:
        numberImages = len(listRegularImages)
    else:
        numberImages = len(dict_scores.keys())
    number_of_methods = len(list_methods)
    print('len(list_methods)',number_of_methods)
    listOfRank = np.zeros((numberImages,number_of_methods))
    ki = 0
    for k in dict_scores.keys(): # Loop on images
        if OnlyStructuredImages:
            if not(k in listRegularImages):
                continue
            
        #plt.figure() 
        dico = dict_scores[k]
        print(dico)
        #print(dico.keys())
        listnameIm += [k]
        list_scores = []
        list_beta_local = []
        fig, axs = plt.subplots(3,3)
        axs_flatten = flatten(axs)
        i = 0
        for method,beta in zip(list_methodsGatysPlusSpectrum,beta_list_plusZero):
            #print(method,method in dico.keys())
            if method in dico.keys():
                list_scores  += [dico[method]]
        argmin = np.argmin(np.array(list_scores))
        # Sans MSInit
        list_scores = []
        for method,beta in zip(list_methodsGatysPlusSpectrum,beta_list_plusZero):
            #print(method,method in dico.keys())
            if method in dico.keys():
                #print(dico.keys())
                score = dico[method]
                #dicoOfMethods[method] += [score]
                list_scores  += [score]
                list_beta_local += [beta]
                if beta==minimum_beta:
                    directoryloacl = ResultsDir
                else:
                    directoryloacl = directory_betaTexture
                name_image = os.path.join(directoryloacl,k,k+list_methodsGatysPlusSpectrum_ext[i]+'.png')
                img = mpimg.imread(name_image)
                axs_flatten[i].imshow(img)
                if beta==minimum_beta:
                    title = r'$log10 \  \beta \ : \ -\infty \  log10 \  KL \ :\ {0:.2f}$'.format(np.log10(dico[method]))
                else:
                    title = r'$log10  \ \beta \ : \ {0:d} \  log10 \  KL \ : \ {1:.2f}$'.format(int(np.log10(beta)),np.log10(dico[method]))
                title_obj = axs_flatten[i].set_title(title)
                if i==argmin:
                    plt.setp(title_obj, color='r')         #set the color of title to red
                i += 1 
        #plt.show()
        print(list_scores)
        if len(list_scores)>0:
            plt.figure()
            plt.plot(np.log10(np.array(list_beta_local)),np.log(np.array(list_scores)),'bo',label='Gatys + Spectrum TF')
            
        fig, axs = plt.subplots(3,3)
        axs_flatten = flatten(axs)
        # Avec MSInit
        list_scores = []
        list_beta_local = []
        for method,beta in zip(list_methodsMSINIt,beta_list_plusZero):
            #print(method,method in dico.keys())
            if method in dico.keys():
                list_scores  += [dico[method]]
        argmin = np.argmin(np.array(list_scores))
        print('argmin',argmin)
        list_scores = []
        i = 0
        for method,beta in zip(list_methodsMSINIt,beta_list_plusZero):
            #print(method)
            if method in dico.keys():
                #print(dico.keys())
                #dicoOfMethods[method] += [dico[method]]
                list_scores  += [dico[method]]
                list_beta_local += [beta]
                if beta==minimum_beta:
                    directoryloacl = ResultsDir
                else:
                    directoryloacl = directory_betaTexture
                name_image = os.path.join(directoryloacl,k,k+list_methodsMSINIt_ext[i]+'.png')
                img = mpimg.imread(name_image)
                axs_flatten[i].imshow(img)
                if beta==minimum_beta:
                    title = r'$log10 \  \beta \ : \ -\infty \  log10 \  KL \ :\ {0:.2f}$'.format(np.log10(dico[method]))
                else:
                    title = r'$log10  \ \beta \ : \ {0:d} \  log10 \  KL \ : \ {1:.2f}$'.format(int(np.log10(beta)),np.log10(dico[method]))
                title_obj = axs_flatten[i].set_title(title)
                if i==argmin:
                    plt.setp(title_obj, color='r')         #set the color of title to red
                i += 1 

        if len(list_scores)>0:
            plt.figure()
            plt.plot(np.log10(np.array(list_beta_local)),np.log(np.array(list_scores)),'ro',label='Gatys + Spectrum TF + MSInit')
        plt.show()  
                
        title = 'log KL div computed with Wavelets coeffs ' +k 
        plt.xlabel('log10 beta')
        plt.ylabel('log KL score')
        plt.xticks(np.log10(np.array(list_beta_local)),labellist)
        #plt.ylim(bottom=0.)  # adjust the bottom leaving top unchanged
        plt.title(title)
        plt.legend(loc='best')
        plt.show()
        
        
        
    input('Enter to close.')
    plt.close()
   
def score_decalage(matrix,d=1):
    """
    @input : a matrix of the pixel coordinate
    @param : d = 1 the distance where the score is computed or not
    """
    diff_vert = np.diff(matrix,axis=0)
    diff_hor = np.diff(matrix,axis=1)
    #  Calcul des différences entre les coordinonnés en verticals et en horizontales
    abs_diff_vert = np.abs(diff_vert)
    abs_diff_hor = np.abs(diff_hor)
    where_1_vert = np.where(abs_diff_vert<=d)
    where_1_hor = np.where(abs_diff_hor<=d)
    sum_where_1_vert = np.sum(where_1_vert[2])/ (abs_diff_vert.shape[0]*abs_diff_vert.shape[1])
    sum_where_1_hor = np.sum(where_1_hor[2])/ (abs_diff_hor.shape[0]*abs_diff_hor.shape[1])
    sum_v_h = 1 - (sum_where_1_vert + sum_where_1_hor)/2
    return(sum_v_h)

def compute_deplacements_score(d=1):
    """
    Le but de cette fonction est de calculer un score de deplacement a partir des
    cartes de deplacements calculees par Said 
    """
    ext_displ = '_X_Y_displacements.pickle'
    dir_deplacement_carte
    dictTotal = {}
    print('=== d',d,' ===')
    for file in files_short:
        filewithoutext = '.'.join(file.split('.')[:-1])
        print('Image :',filewithoutext)
        #filewithoutextreplaced = filewithoutext.replace('_','$\_$')
        dict_scores = {}
        
        # Load the images
        for i,zipped in enumerate(zip(listofmethod,listNameMethod)):
            method,nameMethod = zipped
            
            if method =='':
                continue
            else:
                data_pickle_path = os.path.join(dir_deplacement_carte,filewithoutext,filewithoutext + method+ext_displ)
            data_pickle_path = data_pickle_path.replace('TextureNets','Ulyanov') 
               
            #print(method,nameMethod)
            if os.path.isfile(data_pickle_path):
                with open(data_pickle_path, 'rb') as pkl:
                    data = pickle.load(pkl) # It is a list of the two matrices coordinate X and Y
            else:
                print(data_pickle_path,' does not exist. Wrong path ?')
                raise(ValueError(data_pickle_path))
                
            
            # The simplest way to compute a score is to compute the 
            matrix = np.stack(data,axis=-1) # h,w,pixel coord
            sum_v_h =  score_decalage(matrix,d=d)
            
            print(nameMethod,sum_v_h)
            
            dict_scores[nameMethod] = sum_v_h
            
        dictTotal[filewithoutext] = dict_scores
            
        
    name = 'Displacements_Score'
    if not(d==1):
        name+='_d'+str(d)
    name += '.pkl'
    data_path_save = os.path.join('data',name)
    with open(data_path_save, 'wb') as pkl:
        pickle.dump(dictTotal,pkl)

def copy_displacementMaps():
    """
    This function only serve to copy the displacement maps from 
        dir_deplacement_carte = os.path.join(path_base,ownCloudname,'These Gonthier Nicolas Partage','Cartes_de_deplacements_SAID','Resultats_textures')
        to the latex im folder 
    """             
    output_dir = os.path.join('C:\\','Users','gonthier','Travail','TexturePaper','im','DisplacementMaps')
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    ext_displ = '_colored_displacements.png'

    for file in files_short:
        filewithoutext = '.'.join(file.split('.')[:-1])
        print('Image :',filewithoutext)
       
        # Load the images
        for i,zipped in enumerate(zip(listofmethod,listNameMethod)):
            method,nameMethod = zipped
            
            if method =='':
                continue
            else:
                im_name =filewithoutext + method+ext_displ
                name_im = os.path.join(dir_deplacement_carte,filewithoutext,im_name)
            name_src = name_im.replace('TextureNets','Ulyanov') 
            name_dst = os.path.join(output_dir,im_name.replace('TextureNets','Ulyanov'))
            if os.path.isfile(name_src):
                copyfile(name_src,name_dst)
                                
                                
                                
                                
                                
                                

if __name__ == '__main__':
    #main()
    #readData()
    
   #main(number_of_scale=None)
   # To plot all the figures
#   for OnlyStructuredImages in [True,False]:
#       for OnlySubset_of_methods in [True,False]:
#               readDataAndPlot(OnlyStructuredImages=OnlyStructuredImages,
#                               OnlySubset_of_methods=OnlySubset_of_methods,
#                               ReadWhat='KL',number_of_scale=None)
#   for OnlyStructuredImages in [True,False]:
#       for OnlySubset_of_methods in [True,False]:
#               readDataAndPlot(OnlyStructuredImages=OnlyStructuredImages,
#                               OnlySubset_of_methods=OnlySubset_of_methods,
#                               ReadWhat='DisplacementScore',number_of_scale=None)

   readDataAndPlot(OnlyStructuredImages=False,
                   OnlySubset_of_methods=False,
                   ReadWhat='KL',number_of_scale=None,output_img='tikz')
   readDataAndPlot(OnlyStructuredImages=False,
                   OnlySubset_of_methods=False,
                   ReadWhat='DisplacementScore',number_of_scale=None,output_img='tikz')
   #main() # To compute for the Wavelets
   #compute_deplacements_score()
   # tab = ['KL','DisplacementScore']
   # for OnlyStructuredImages in [True,False]:
       # for OnlySubset_of_methods in [True,False]:
           # for ReadWhat in tab:
               # readDataAndPlot(OnlyStructuredImages=OnlyStructuredImages,
                               # OnlySubset_of_methods=OnlySubset_of_methods,
                               # ReadWhat=ReadWhat)
    # tab = ['DisplacementScore']
    # for d in [2,5,10,50,100,128,256]:
        # for OnlyStructuredImages in [True,False]:
            # for OnlySubset_of_methods in [True,False]:
                # for ReadWhat in tab:
                    # compute_deplacements_score(d=d)
                    # readDataAndPlot(OnlyStructuredImages=OnlyStructuredImages,
                                    # OnlySubset_of_methods=OnlySubset_of_methods,
                                    # ReadWhat=ReadWhat,d=d)
    # import sys
    # sys.exit(main(sys.argv))
    #computeKL_forbeta_images()
    #Plot_KL_forDiffBetaValues()
