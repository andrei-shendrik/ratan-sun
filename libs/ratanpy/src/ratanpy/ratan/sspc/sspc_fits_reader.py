import logging
from pathlib import Path

import numpy as np
from astropy.io import fits

from ratanpy.observation.observation import Observation
from ratanpy.ratan.services.ratan_observation_reader import RatanObservationReader
from ratanpy.ratan.sspc.sspc_data import SSPCData
from ratanpy.ratan.sspc.sspc_metadata_fits_loader import SSPCMetadataFitsLoader
from ratanpy.ratan.sspc.sspc_observation import SSPCObservation

logger = logging.getLogger(__name__)

class SSPCFitsReader(RatanObservationReader):

    def can_read(self, file: Path) -> bool:
        if not file.suffix.lower() == '.fits':
            return False
        # try:
        #
        # except Exception:
        #     return False
        return True

    def read(self, file: Path) -> SSPCObservation:

        try:
            with fits.open(file) as hdul:
                header = hdul[0].header
                hdu2_table = hdul[1].data
                array_3d = hdul[0].data.astype(np.float32)
        except (FileNotFoundError, OSError, ValueError) as e:
            message = f"Error while reading file: {file}"
            logger.exception(f"{message}")
            raise IOError(f"{message}: {e}") from e

        sspc_metadata = SSPCMetadataFitsLoader.load(header, hdu2_table, array_3d)
        sspc_data = SSPCData(array_3d = array_3d)
        observation = SSPCObservation(sspc_metadata, sspc_data)

        return observation

    def read_metadata(self, file_path: Path) -> Observation:
        pass