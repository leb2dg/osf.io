from website.addons.googledrive import routes, model_1, views


MODELS = [
    model_1.GoogleDriveUserSettings,
    model_1.GoogleDriveNodeSettings,
    # model.GoogleDriveOAuthSettings,
    model_1.GoogleDriveGuidFile,
]
USER_SETTINGS_MODEL = model_1.GoogleDriveUserSettings
NODE_SETTINGS_MODEL = model_1.GoogleDriveNodeSettings

ROUTES = [routes.auth_routes, routes.api_routes]

SHORT_NAME = 'googledrive'
FULL_NAME = 'Google Drive'

OWNERS = ['user', 'node']  # can include any of ['user', 'node']

VIEWS = []  # page, widget
CONFIGS = ['user', 'node']  # any of ['user', 'node']

CATEGORIES = ['storage']

INCLUDE_JS = {
    'page': [],
    'files': []
}

INCLUDE_CSS = {
    'page': [],
    'files': []
}

HAS_HGRID_FILES = True  # set to True for storage addons that display in HGrid
GET_HGRID_DATA = views.hgrid.googledrive_addon_folder
# MAX_FILE_SIZE = 10  # MB
