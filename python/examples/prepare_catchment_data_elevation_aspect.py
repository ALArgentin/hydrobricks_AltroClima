import os.path
import tempfile
from pathlib import Path

import hydrobricks as hb

# Paths
TEST_FILES_DIR = Path(
    os.path.dirname(os.path.realpath(__file__)),
    '..', '..', 'tests', 'files', 'catchments'
)
CATCHMENT_OUTLINE = TEST_FILES_DIR / 'ch_sitter_appenzell' / 'outline.shp'
CATCHMENT_DEM = TEST_FILES_DIR / 'ch_sitter_appenzell' / 'dem.tif'

# Create temporary directory
with tempfile.TemporaryDirectory() as tmp_dir_name:
    tmp_dir = tmp_dir_name

os.mkdir(tmp_dir)
working_dir = Path(tmp_dir)

# Prepare catchment data
catchment = hb.Catchment(CATCHMENT_OUTLINE)
catchment.extract_dem(CATCHMENT_DEM)

# Compute the slope and aspect
catchment.calculate_slope_aspect()

# Create elevation bands
bands = catchment.discretize_by(criteria=['elevation', 'aspect'],
                                elevation_method='isohypse', elevation_distance=100)

# Save elevation bands to a raster
catchment.save_unit_ids_raster(working_dir / 'unit_ids.tif')

# Save the elevation band properties to a csv file
bands.to_csv(working_dir / 'bands.csv')

print(f"Files saved to: {working_dir}")
