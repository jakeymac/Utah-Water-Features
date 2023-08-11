from django.shortcuts import render
from tethys_sdk.routing import controller
from tethys_sdk.layouts import MapLayout
from pathlib import Path
from .app import UtahWaterFeatures as app
import json
import pandas as pd


@controller
def home(request):
    """
    Controller for the app home page.
    """
    return render(request, 'utah_water_features/home.html', {})

@controller(url='utah_water_features/map',name="map",app_workspace=True)
class MyMapLayout(MapLayout):
    app = app
    base_template = 'utah_water_features/base.html'
    map_title = 'Utah Water Features'

    #Set initial zoom
    default_map_extent = [-112.12724351410439, 38.402436892959884, -108.83472682102519, 41.8331592667235]
    max_zoom = 14
    min_zoom = 2
    show_properties_popup = True #Allow clicking on features for information
    plot_slide_sheet = True
    geoserver_workspace = 'geoserver_app'


    def compose_layers(self, request, map_view, app_workspace, *args, **kwargs):
        data_directory = Path(app_workspace.path)

        
        reservoir_geojson_file = data_directory / 'Utah_Reservoirs_NHD_4326.geojson'

        with open(reservoir_geojson_file) as ff:
            reservoir_geojson = json.loads(ff.read())

        #Prepare wms layer
        wms_layer = self.build_wms_layer(
            endpoint = "http://localhost:8181/geoserver/wms",
            server_type = 'geoserver',
            layer_name="geoserver_app:iqh8fp",
            layer_title='Utah Rivers',
            layer_variable='utah_rivers',
            visible=True,
            selectable=True,
            geometry_attribute='the_geom',
            excluded_properties = ["OBJECTID","WB_", "WB_ID","COM_ID","RCH_COM_ID","FTYPE","FCODE","STAGE","GNIS_ID","SHAPE_Leng","SHAPE_Area","ELEV"]
        )

        #Prepare geojson layer
        reservoirs_layer = self.build_geojson_layer(
            geojson=reservoir_geojson,
            layer_name='reservoirs',
            layer_title = 'Reservoirs',
            layer_variable='reservoirs',
            visible=True,
            selectable=True,
            plottable=True,
            excluded_properties = ["OBJECTID","Permanent_Identifier", "FDate", "Resolution","GNIS_ID","ReachCode","FType","FType_Text","FCode","InUtah","IsMajor", "SHAPE_Length","SHAPE_Area"]
        )

        #Prepare layer groups and controls
        layer_groups = [
            self.build_layer_group(
            id='layer-features',
            display_name= "Layer Features",
            layer_control='checkbox',
            layers=[
                reservoirs_layer,
                wms_layer,
            ]
            )
        ]

        return layer_groups


    #Geojson layer visual preferences
    @classmethod
    def get_vector_style_map(cls):
        return {
            'MultiPolygon': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': 'blue',
                    'width': 3
                }},
                'fill': {'ol.style.Fill': {
                    'color': 'rgba(0, 75, 128, 0.1)'
                }}
            }},
        }

    #Define data for time series plot
    def get_plot_for_layer_feature(self, request, layer_name, feature_id, layer_data, feature_props,app_workspace,*args, **kwargs):
        data_directory = Path(app_workspace.path)
        
        #Plot x and y axis labels
        layout = {
            'yaxis': {
                'title': 'Water Level (cubic feet)'
            },
            'xaxis': {
                'title': 'Month'
            }
        }
        #CSV file for plot information
        time_water_level_data_file = data_directory / 'Utah_Reservoir_Levels.csv'
        
        df = pd.read_csv(time_water_level_data_file)

        #Grab all unique dates in the dataframe
        dates = df.iloc[:,1].unique()
        
        #Find the reservoir the user has clicked on
        selected_reservoir = feature_props["Name"]

        #Filter for water levels for the chosen reservoir
        levels = df[df["Name"] == selected_reservoir]
        
        #Data used in the plot
        data = [
            { 'name':'Water Levels',
               'mode':'lines',
               'x': dates.tolist(),
               'y': levels.iloc[:,7].tolist()
             }
        ]

        return f"{selected_reservoir} levels over the past year", data, layout