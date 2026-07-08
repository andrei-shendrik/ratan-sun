import logging
from pathlib import Path

import numpy as np
from astropy.io import fits

from ratanpy.observation.observation_reader import ObservationReader
from ratanpy.ratan.channel_mapper import ChannelMapper
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_data import FastAcquisition1To3GHzData
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata import FastAcquisition1To3GHzMetadata
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata_fits_loader import \
    FastAcquisition1To3GHzMetadataFitsLoader
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import FastAcquisition1To3GHzObservation

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzFitsReader(ObservationReader):

    def can_read(self, file: Path) -> bool:
        if not file.suffix.lower() == '.fits':
            return False
            # try:
            #
            # except Exception:
            #     return False
        return True

    def read(self, file_path: Path) -> 'FastAcquisition1To3GHzObservation':
        try:
            with fits.open(file_path, memmap=True) as hdul:
                header = hdul[0].header
                # table_hdu = hdul[1]
                data_cube = hdul[0].data.astype(np.float32)

            metadata = FastAcquisition1To3GHzMetadataFitsLoader.load(header) # , table_hdu

            mapping = ChannelMapper.get_channel_mapping(metadata.polarization_channel0, metadata.polarization_channel1)
            fast_acq_data = FastAcquisition1To3GHzData(mapping)

            fast_acq_data.pol_channel0 = data_cube[:, 0, :]
            fast_acq_data.pol_channel1 = data_cube[:, 1, :]

            return FastAcquisition1To3GHzObservation(metadata, fast_acq_data)

        except Exception as e:
            logger.exception(f"Failed to read full FITS {file_path.name}: {e}")
            raise IOError(f"Full read error: {e}") from e

    def read_metadata(self, file_path: Path) -> 'FastAcquisition1To3GHzMetadata':
        try:
            with fits.open(file_path, memmap=True) as hdul:
                header = hdul[0].header
                # table_hdu = hdul[1]
            return FastAcquisition1To3GHzMetadataFitsLoader.load(header) # (header, table_hdu)
        except Exception as e:
            logger.error(f"Failed to read FITS metadata from {file_path.name}: {e}")
            raise IOError(f"Metadata read error: {e}") from e
