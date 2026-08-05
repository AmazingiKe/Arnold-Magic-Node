"""Maya-specific environment paths.

Only this adapter knows how to ask Maya for the per-user application
directory. It intentionally does not create directories while being imported.
"""

from ..core.paths import user_data_root


def get_user_data_root():
    """Return the shared, cross-version Arnold Magic Node user data root."""
    import maya.cmds as cmds

    return user_data_root(cmds.internalVar(userAppDir=True))
