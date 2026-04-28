import argparse
import configparser
import os
import sys
from pathlib import Path
import pandas as pd

from service.barcode_parser import BarcodeParser
from service.hira_mapper import HiraMapper
from service.drug_api_client import DrugApiClient
from service.csv_processor import CsvProcessor

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

API_BATCH_SIZE = 40
DEFAULT_CONFIG_FILE = "config.ini"
ENV_SERVICE_KEY = "MED_SERVICE_KEY"

def load_hira_df(hira_csv_path):
    try:
        return pd.read_csv(hira_csv_path, dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return pd.read_csv(hira_csv_path, dtype=str, encoding="cp949")
        except UnicodeDecodeError:
            return pd.read_csv(hira_csv_path, dtype=str, encoding="euc-kr")


def resolve_path(path_value):
    path = Path(path_value)
    if path.is_absolute():
        return path
    return BASE_DIR / path


def load_config(config_path):
    config = configparser.RawConfigParser()
    if config_path.exists():
        config.read(config_path, encoding="utf-8")
    return config


def get_api_setting(config, option_name, default=None):
    if not config.has_section("api"):
        return default
    return config.get("api", option_name, fallback=default)


def resolve_service_key(args, config):
    service_key = args.service_key or os.getenv(ENV_SERVICE_KEY) or get_api_setting(config, "service_key")
    if not service_key:
        raise ValueError(
            "API service key is missing. Set it in config.ini [api] service_key, "
            f"or set {ENV_SERVICE_KEY}, or pass --service-key."
        )
    return service_key.strip()


def resolve_api_batch_size(args, config):
    batch_size = args.api_batch_size or get_api_setting(config, "batch_size", str(API_BATCH_SIZE))
    try:
        return max(int(batch_size), 1)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid api batch size: {batch_size}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hira", default="HIRA.csv")
    parser.add_argument("--input", default="약국만.csv")
    parser.add_argument("--output", default="약국만_API결과.csv")
    parser.add_argument("--config", default=DEFAULT_CONFIG_FILE)
    parser.add_argument("--service-key", default=None)
    parser.add_argument("--api-batch-size", default=None)
    return parser.parse_args()


def main():
    args = parse_args()

    hira_path = resolve_path(args.hira)
    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)
    config_path = resolve_path(args.config)

    if not hira_path.exists():
        raise FileNotFoundError(f"HIRA.csv not found: {hira_path}")

    if not input_path.exists():
        raise FileNotFoundError(f"Input csv not found: {input_path}")

    config = load_config(config_path)
    service_key = resolve_service_key(args, config)
    api_batch_size = resolve_api_batch_size(args, config)

    hira_df = load_hira_df(hira_path)

    barcode_parser = BarcodeParser()
    hira_mapper = HiraMapper(hira_df)
    api_client = DrugApiClient(service_key)

    processor = CsvProcessor(barcode_parser, hira_mapper, api_client, api_batch_size=api_batch_size)
    processor.process(str(input_path), str(output_path))

    print("finished")


if __name__ == "__main__":
    main()
