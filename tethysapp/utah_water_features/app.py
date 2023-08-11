from tethys_sdk.base import TethysAppBase


class UtahWaterFeatures(TethysAppBase):
    """
    Tethys app class for Map Layout Tutorial.
    """

    name = 'Utah Water Features'
    description = ''
    package = 'utah_water_features'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/sand_hollow_icon.jpeg'
    root_url = 'utah-water-features'
    color = '#16a085'
    tags = ''
    enable_feedback = False
    feedback_emails = []