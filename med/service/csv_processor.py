import pandas as pd


class CsvProcessor:
    def __init__(self, barcode_parser, hira_mapper, api_client, api_batch_size=40):
        self.barcode_parser = barcode_parser
        self.hira_mapper = hira_mapper
        self.api_client = api_client
        self.api_batch_size = max(int(api_batch_size), 1)

    def _fetch_api_rows_in_batches(self, item_seqs):
        item_seq_list = item_seqs.tolist()
        total_items = len(item_seq_list)

        if total_items == 0:
            return pd.DataFrame()

        total_batches = (total_items + self.api_batch_size - 1) // self.api_batch_size
        api_results = []

        for batch_index, start in enumerate(range(0, total_items, self.api_batch_size), start=1):
            end = min(start + self.api_batch_size, total_items)
            print(f"api fetch batch {batch_index}/{total_batches} ({start + 1}-{end}/{total_items})")

            batch_item_seqs = item_seq_list[start:end]
            for item_index, item_seq in enumerate(batch_item_seqs, start=start + 1):
                try:
                    api_results.append(self.api_client.fetch(item_seq))
                except Exception as e:
                    print(
                        f"[CsvProcessor] api fetch failed but continuing "
                        f"- batch={batch_index}/{total_batches}, row={item_index}, itemSeq={item_seq}, error={e}"
                    )
                    api_results.append(self.api_client.build_error_result(f"BATCH_FETCH_ERROR: {e}"))

        return pd.DataFrame(api_results)

    def process(self, input_csv_path, output_csv_path):
        df = pd.read_csv(input_csv_path, dtype=str)

        print('parsing data')
        parsed_rows = df["바코드"].apply(self.barcode_parser.parse)
        parsed_df = pd.DataFrame(parsed_rows.tolist())
        print('data parsed')

        # 혹시 기존 컬럼이 있으면 제거
        for col in parsed_df.columns:
            if col in df.columns:
                df = df.drop(columns=[col])

        result_df = pd.concat([df, parsed_df], axis=1)

        print('finding prod Code from Hira')
        result_df["품목기준코드"] = result_df["표준코드후보"].apply(
            lambda code: self.hira_mapper.find_item_seq(code, None))
        print('Hira complete')

        print('api fetch start')
        api_df = self._fetch_api_rows_in_batches(result_df["품목기준코드"])
        print('api fetch complete')

        result_df = pd.concat([result_df, api_df], axis=1)
        result_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")

        print('csv created')
