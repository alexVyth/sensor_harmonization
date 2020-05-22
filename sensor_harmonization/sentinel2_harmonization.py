# Python Native
import glob
import logging
import os
import re
import shutil

import gdal

# Local import
import sentinel2_angle_bands
import harmonization_model
import utils


def sentinel_NBAR(sz_path, sa_path, vz_path, va_path, SAFEL2A, target_dir):
    ### Sentinel-2 data set ###
    pars_array_index = {'B02': 0, 'B03': 1, 'B04': 2, 'B08': 3, 'B8A': 3, 'B11': 4, 'B12': 5}

    satsen = os.path.basename(SAFEL2A)[0:3]
    logging.info('SatSen: {}'.format(satsen))

    img_dir = os.path.join(SAFEL2A, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEL2A,'GRANULE/'))[0], 'IMG_DATA/R10m/'))
    bands10m = ['B02','B03','B04','B08']
    band_sz = utils.load_img(sz_path)
    band_sa = utils.load_img(sa_path)
    band_vz = utils.load_img(vz_path)
    band_va = utils.load_img(va_path)
    harmonization_model.process_NBAR(img_dir, bands10m, band_sz, band_sa, band_vz, band_va, satsen, pars_array_index, target_dir)

    img_dir = os.path.join(SAFEL2A, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEL2A,'GRANULE/'))[0], 'IMG_DATA/R20m/'))
    bands20m = ['B8A','B11','B12']
    band_sz = utils.load_img_resampled_to_half(sz_path)
    band_sa = utils.load_img_resampled_to_half(sa_path)
    band_vz = utils.load_img_resampled_to_half(vz_path)
    band_va = utils.load_img_resampled_to_half(va_path)
    harmonization_model.process_NBAR(img_dir, bands20m, band_sz, band_sa, band_vz, band_va, satsen, pars_array_index, target_dir)

def sentinel_harmonize(SAFEL1C, SAFEL2A, target_dir=None):
    logging.info('Generating Angles from {} ...'.format(SAFEL1C))
    sz_path, sa_path, vz_path, va_path = sentinel2_angle_bands.gen_s2_ang(SAFEL1C)

    if target_dir is None:
        target_dir = os.path.join(SAFEL2A, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEL2A,'GRANULE/'))[0], 'HARMONIZED_DATA/'))
    os.makedirs(target_dir, exist_ok=True)

    logging.info('Harmonization ...')
    sentinel_NBAR(sz_path, sa_path, vz_path, va_path, SAFEL2A, target_dir)

    #COPY quality band
    pattern = re.compile('.*SCL.*')
    img_list = [f for f in glob.glob(os.path.join(SAFEL2A, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEL2A,'GRANULE/'))[0], 'IMG_DATA/R20m/')) + "/*.jp2", recursive=True)]
    qa_filepath = list(filter(pattern.match, img_list))[0]
    #Convert jp2 to tiff
    src_ds = gdal.Open(qa_filepath)
    os.system('gdal_translate -of Gtiff ' + qa_filepath + ' ' + target_dir + '/' + os.path.basename(qa_filepath)[:-4] + '.tif')
    # out_ds = gdal.Translate(target_dir + '/' + os.path.basename(qa_filepath)[:-4] + '.tif', src_ds, format='Gtiff', bandList=[1])
    out_ds = None
    src_ds = None

    return target_dir


def sentinel_NBAR_lasrc(sz_path, sa_path, vz_path, va_path, sr_dir, target_dir):
    ### Sentinel-2 data set ###
    pars_array_index = {'band2': 0, 'band3': 1, 'band4': 2, 'band8': 3, 'band8a': 3, 'band11': 4, 'band12': 5}

    satsen = os.path.basename(sr_dir)[0:3]
    print('SatSen: {}'.format(satsen), flush=True)

    bands = ['band2','band3','band4','band8', 'band8a','band11','band12']
    band_sz = utils.load_img(sz_path)
    band_sa = utils.load_img(sa_path)
    band_vz = utils.load_img(vz_path)
    band_va = utils.load_img(va_path)
    harmonization_model.process_NBAR(sr_dir, bands, band_sz, band_sa, band_vz, band_va, satsen, pars_array_index, target_dir)


def sentinel_harmonize_lasrc(SAFEL1C, sr_dir, target_dir):
    print('Generating Angles from {} ...'.format(SAFEL1C), flush=True)
    sz_path, sa_path, vz_path, va_path = sentinel2_angle_bands.gen_s2_ang(SAFEL1C)

    os.makedirs(target_dir, exist_ok=True)

    print('Harmonization ...', flush=True)
    sentinel_NBAR_lasrc(sz_path, sa_path, vz_path, va_path, sr_dir, target_dir)

    return target_dir
