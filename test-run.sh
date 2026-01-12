#!/usr/bin/env bash
# author: daniel rode


./docker/build.sh

pdal tindex create --tindex collective_bounds.gpkg --filespec "tmp-import/*.laz" --fast_boundary --ogrdriver GPKG

bbox="$(ogrinfo -so -al collective_bounds.gpkg | grep "Extent:" | sed 's/Extent: //g' | sed 's/(//g; s/)//g; s/ - /, /g' | awk -F', ' '{printf "{\"minx\":%s,\"miny\":%s,\"maxx\":%s,\"maxy\":%s}\n", $1, $2, $3, $4}')"

db_name="pc.tdb"
crs="EPSG:4326"
res=20

podman run --rm -it -v "$PWD:$PWD" -w "$PWD" silvimetric:latest silvimetric -d "${db_name}" initialize --bounds "${bbox}" --crs "${crs}" --resolution="${res}" -m grid_metrics
# gives error message:
#    Usage: silvimetric initialize [OPTIONS]
#    Try 'silvimetric initialize --help' for help.
#
#    Error: Invalid value for '--metrics' / '-m': 'grid_metrics' is not available in Metrics

podman run --rm -it -v "$PWD:$PWD" -w "$PWD" silvimetric:latest silvimetric -d "${db_name}" initialize --bounds "${bbox}" --crs "${crs}" --resolution="${res}" -m stats,percentiles
# gives error message:
#    Traceback (most recent call last):
#      File "/opt/conda/bin/silvimetric", line 10, in <module>
#        sys.exit(cli())
#                 ~~~^^
#      File "/opt/conda/lib/python3.14/site-packages/click/core.py", line 1485, in __call__
#        return self.main(*args, **kwargs)
#               ~~~~~~~~~^^^^^^^^^^^^^^^^^
#      File "/opt/conda/lib/python3.14/site-packages/click/core.py", line 1406, in main
#        rv = self.invoke(ctx)
#      File "/opt/conda/lib/python3.14/site-packages/click/core.py", line 1873, in invoke
#        return _process_result(sub_ctx.command.invoke(sub_ctx))
#                               ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
#      File "/opt/conda/lib/python3.14/site-packages/click/core.py", line 1269, in invoke
#        return ctx.invoke(self.callback, **ctx.params)
#               ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#      File "/opt/conda/lib/python3.14/site-packages/click/core.py", line 824, in invoke
#        return callback(*args, **kwargs)
#      File "/opt/conda/lib/python3.14/site-packages/click/decorators.py", line 46, in new_func
#        return f(get_current_context().obj, *args, **kwargs)
#      File "/opt/conda/lib/python3.14/site-packages/silvimetric/cli/cli.py", line 276, in initialize_cmd
#        storageconfig = StorageConfig(
#            tdb_dir=app.tdb_dir,
#        ...<6 lines>...
#            alignment=alignment
#        )
#      File "<string>", line 15, in __init__
#      File "/opt/conda/lib/python3.14/site-packages/silvimetric/resources/config.py", line 106, in __post_init__
#        raise Exception(
#        ...<2 lines>...
#        )
#    Exception: Given coordinate system is not a rectilinear projected coordinate system

