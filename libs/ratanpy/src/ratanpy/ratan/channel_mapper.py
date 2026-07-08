from ratanpy.ratan.polarization_type import PolarizationType


class ChannelMapper:
    """
    Соответствие каналов 0 и 1 поляризации
    """

    _POLARIZATION_TO_ATTRIBUTE = {
        PolarizationType.LHCP: 'lhcp',
        PolarizationType.RHCP: 'rhcp',
        PolarizationType.STOKES_I: 'stokes_i',
        PolarizationType.STOKES_V: 'stokes_v'
    }

    @classmethod
    def get_channel_mapping(cls, pol_ch0: PolarizationType, pol_ch1: PolarizationType) -> dict:

        ch0_attr = cls._POLARIZATION_TO_ATTRIBUTE.get(pol_ch0)
        ch1_attr = cls._POLARIZATION_TO_ATTRIBUTE.get(pol_ch1)

        if not ch0_attr or not ch1_attr:
            raise ValueError(f"Invalid polarization types provided: ch0='{pol_ch0}', ch1='{pol_ch1}'")

        return {
            'pol_channel0': ch0_attr,
            'pol_channel1': ch1_attr,
        }