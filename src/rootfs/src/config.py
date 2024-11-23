from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["/data/options.json"],
)
