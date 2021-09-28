import geopandas as gd

path_to_data = gd.datasets.get_path('nybb')
gdf = gd.read_file(path_to_data)

gdf['bd'] = gdf.boundary
print(gdf['bd'])
print(type(gdf['bd']))