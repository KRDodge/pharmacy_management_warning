import argparse
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

SERVICE_KEY = "0dpmdc2FE6BlxQH1ApIaxodKsJobGA9yu7qG4lTln1Y9WAXFJEu48Lsn1avbVzt3wrr%2FvBuiWYZITzi%2Bc6u%2Fzg%3D%3D"
API_BATCH_SIZE = 40

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hira", default="HIRA.csv")
    parser.add_argument("--input", default="약국만.csv")
    parser.add_argument("--output", default="약국만_API결과.csv")
    return parser.parse_args()


def main():
    args = parse_args()

    hira_path = resolve_path(args.hira)
    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)

    if not hira_path.exists():
        raise FileNotFoundError(f"HIRA.csv not found: {hira_path}")

    if not input_path.exists():
        raise FileNotFoundError(f"Input csv not found: {input_path}")

    hira_df = load_hira_df(hira_path)

    barcode_parser = BarcodeParser()
    hira_mapper = HiraMapper(hira_df)
    api_client = DrugApiClient(SERVICE_KEY)

    processor = CsvProcessor(barcode_parser, hira_mapper, api_client, api_batch_size=API_BATCH_SIZE)
    processor.process(str(input_path), str(output_path))

    print("finished")


if __name__ == "__main__":
    main()
