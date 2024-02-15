import mimetypes
from coordextract.factory import process_gpx_to_point_models

def filehandler(file):
    mimetype, _= mimetypes.guess_type(file)
    if mimetype == 'application/gpx+xml':
        return process_gpx_to_point_models(file)
    else:
        raise ValueError(f"Unknown filetype: {file}")