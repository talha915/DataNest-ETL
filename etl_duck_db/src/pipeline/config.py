from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class DatabaseConfig:
    db_path: str


@dataclass(frozen=True)
class SourceConfig:
    source_path: str


@dataclass(frozen=True)
class BronzeConfig:
    data_path: str

@dataclass(frozen=True)
class SilverConfig:
    data_path: str

@dataclass(frozen=True)
class SqlConfig:
    sql_path: str


@dataclass(frozen=True)
class SchemaConfig:
    bronze: str
    silver: str
    gold: str
    system: str


@dataclass(frozen=True)
class PipelineConfig:
    pipeline_name: str


@dataclass(frozen=True)
class Config:
    database: DatabaseConfig
    source: SourceConfig
    bronze: BronzeConfig
    silver: SilverConfig
    sql: SqlConfig
    schemas: SchemaConfig
    pipeline: PipelineConfig


def load_config_file(path: str = "config/config.yaml") -> Config:
    file_path = Path(path)

    with file_path.open("r", encoding="utf-8") as file:
        yaml_content = yaml.safe_load(file)

    return Config(
        database=DatabaseConfig(
            db_path = yaml_content["database"]["path"]
        ),
        source=SourceConfig(
            source_path = yaml_content["source"]["spotify_json_path"]
        ),
        bronze=BronzeConfig(
            data_path = yaml_content["bronze"]["data_path"]
        ),
        silver = SilverConfig(
            data_path = yaml_content["silver"]["data_path"]
        ),
        sql=SqlConfig(
            sql_path = yaml_content["sql"]["path"]
        ),
        schemas=SchemaConfig(
            bronze = yaml_content["schemas"]["bronze"],
            silver = yaml_content["schemas"]["silver"],
            gold = yaml_content["schemas"]["gold"],
            system = yaml_content["schemas"]["system"],
        ),
        pipeline=PipelineConfig(
            pipeline_name = yaml_content["pipeline"]["name"]
        ),
    )

# loaded_content = load_config_file()  
# print(loaded_content)  