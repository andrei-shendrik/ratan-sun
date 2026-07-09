from ratanpy.common.advanced_enum import AdvancedEnum


class PolarizationType(AdvancedEnum):

    """
    polarization = PolarizationType.LHCP

    """

    LHCP = "LHCP"
    RHCP = "RHCP"
    STOKES_I = "Stokes I"
    STOKES_V = "Stokes V"