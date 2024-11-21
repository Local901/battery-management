from dynaconf import Dynaconf

config = Dynaconf(
    envvar_prefix="CONF",
    settings_files=["settings.json", "/data/options.json"],
)
