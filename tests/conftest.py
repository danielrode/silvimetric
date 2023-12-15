import pytest
import os
import dask
import pdal
import json

from silvimetric import Extents, Bounds, Metrics, Attribute, Storage, Log
from silvimetric import ShatterConfig, StorageConfig, ApplicationConfig
from silvimetric import __version__ as svversion

from silvimetric.commands.shatter import create_pipeline

@pytest.fixture(scope="session", autouse=True)
def configure_dask():
    dask.config.set(scheduler="single-threaded")

@pytest.fixture(scope="function")
def threaded_dask():
    dask.config.set(scheduler="threads")

@pytest.fixture(scope='function')
def tdb_filepath(tmp_path_factory) -> str:
    path = tmp_path_factory.mktemp("test_tdb")
    yield os.path.abspath(path)

@pytest.fixture(scope='function')
def storage_config(tdb_filepath, bounds, resolution, crs, attrs, metrics):
    log = Log(20)
    yield StorageConfig(tdb_dir = tdb_filepath,
                        log = log,
                        crs = crs,
                        bounds = bounds,
                        resolution = resolution,
                        attrs = attrs,
                        metrics = metrics,
                        version = svversion)

@pytest.fixture(scope='function')
def metrics():
    yield [Metrics['mean'], Metrics['median']]

@pytest.fixture(scope="function")
def storage(storage_config) -> Storage:
    yield Storage.create(storage_config)

@pytest.fixture(scope='function')
def app_config(tdb_filepath, debug=True):
    log = Log(20) # INFO
    app = ApplicationConfig(tdb_dir = tdb_filepath,
                            log = log)
    yield app

@pytest.fixture(scope='function')
def shatter_config(tdb_filepath, filepath, tile_size, storage_config, app_config, storage):
    log = Log(20) # INFO
    s = ShatterConfig(tdb_dir = tdb_filepath,
                      log = log,
                      filename = filepath,
                      tile_size = tile_size,
                      attrs = storage_config.attrs,
                      metrics = storage_config.metrics,
                      debug = True)
    yield s

@pytest.fixture(scope="function")
def secrets():
    path = os.path.join(os.path.dirname(__file__), ".secrets")
    assert os.path.exists(path)
    p = os.path.abspath(path)
    with open(p, 'r') as secret:
        secret_json = json.loads(secret.read())
    yield secret_json

@pytest.fixture(scope="function")
def s3_bucket():
    yield "silvimetric"

@pytest.fixture(scope='function')
def s3_uri(s3_bucket):
    yield f"s3://{s3_bucket}/test_copc_shatter"

@pytest.fixture(scope="function")
def s3_storage_config(s3_uri, bounds, resolution, crs, attrs, metrics):
    yield StorageConfig(bounds, crs, resolution, attrs, metrics,
                        svversion, tdb_dir=s3_uri)

@pytest.fixture(scope='function')
def s3_storage(s3_storage_config, s3_bucket, secrets):
    import subprocess
    os.environ['AWS_ACCESS_KEY_ID'] = secrets['AWS_ACCESS_KEY_ID']
    os.environ['AWS_SECRET_ACCESS_KEY'] = secrets['AWS_SECRET_ACCESS_KEY']
    yield Storage.create(s3_storage_config)
    subprocess.call(["aws", "s3", "rm", "--recursive", s3_storage_config.tdb_dir])

@pytest.fixture(scope="function")
def s3_shatter_config(s3_storage, filepath, attrs, metrics):
    config = s3_storage.config
    yield ShatterConfig(filepath, 30, attrs, metrics, debug=True, tdb_dir=config.tdb_dir)

@pytest.fixture(scope='session')
def filepath() -> str:
    path = os.path.join(os.path.dirname(__file__), "data",
            "test_data_2.copc.laz")
    assert os.path.exists(path)
    yield os.path.abspath(path)

@pytest.fixture(scope='class')
def bounds(minx, maxx, miny, maxy) -> Bounds:
    yield Bounds(minx, miny, maxx, maxy)

@pytest.fixture(scope='class')
def extents(resolution, tile_size, bounds, crs) -> Extents:
    yield Extents(bounds,resolution,tile_size,crs)

@pytest.fixture(scope="session")
def attrs(dims) -> list[str]:
    yield [Attribute(a, dims[a]) for a in
           ['Z', 'NumberOfReturns', 'ReturnNumber', 'Intensity']]

@pytest.fixture(scope="session")
def dims():
    yield { d['name']: d['dtype'] for d in pdal.dimensions }

@pytest.fixture(scope='class')
def pipeline(filepath) -> pdal.Pipeline:
    yield create_pipeline(filepath)

@pytest.fixture(scope='class')
def resolution() -> int:
    yield 30

@pytest.fixture(scope='class')
def tile_size() -> int:
    yield 4

@pytest.fixture(scope='class')
def test_point_count() -> int:
    yield 84100

@pytest.fixture(scope='class')
def minx() -> float:
    yield 300

@pytest.fixture(scope='class')
def miny() -> float:
    yield 300

@pytest.fixture(scope='class')
def maxx() -> float:
    yield 600

@pytest.fixture(scope='class')
def maxy() -> float:
    yield 600

@pytest.fixture(scope="class")
def crs():
    yield "EPSG:5070"
