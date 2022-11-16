"""
Foxx Exceptions
"""

from .foxx_commit_error import FoxxCommitError
from .foxx_config_get_error import FoxxConfigGetError
from .foxx_config_replace_error import FoxxConfigReplaceError
from .foxx_config_update_error import FoxxConfigUpdateError
from .foxx_dependency_replace_error import FoxxDependencyReplaceError
from .foxx_dependency_update_error import FoxxDependencyUpdateError
from .foxx_depenedency_get_error import FoxxDependencyGetError
from .foxx_dev_mode_disable_error import FoxxDevModeDisableError
from .foxx_dev_mode_enable_error import FoxxDevModeEnableError
from .foxx_download_error import FoxxDownloadError
from .foxx_readme_get_error import FoxxReadmeGetError
from .foxx_script_list_error import FoxxScriptListError
from .foxx_script_run_error import FoxxScriptRunError
from .foxx_service_create_error import FoxxServiceCreateError
from .foxx_service_delete_error import FoxxServiceDeleteError
from .foxx_service_get_error import FoxxServiceGetError
from .foxx_service_list_error import FoxxServiceListError
from .foxx_service_replace_error import FoxxServiceReplaceError
from .foxx_service_update_error import FoxxServiceUpdateError
from .foxx_swagger_get_error import FoxxSwaggerGetError
from .foxx_test_run_error import FoxxTestRunError

__all__ = [
    "FoxxCommitError",
    "FoxxConfigGetError",
    "FoxxConfigReplaceError",
    "FoxxConfigUpdateError",
    "FoxxDependencyReplaceError",
    "FoxxDependencyUpdateError",
    "FoxxDependencyGetError",
    "FoxxDevModeDisableError",
    "FoxxDevModeEnableError",
    "FoxxDownloadError",
    "FoxxReadmeGetError",
    "FoxxScriptListError",
    "FoxxScriptRunError",
    "FoxxServiceCreateError",
    "FoxxServiceDeleteError",
    "FoxxServiceGetError",
    "FoxxServiceListError",
    "FoxxServiceReplaceError",
    "FoxxServiceUpdateError",
    "FoxxSwaggerGetError",
    "FoxxTestRunError",
]
