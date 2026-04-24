import re


class HiraMapper:
    def __init__(self, hira_df):
        self.hira_df = hira_df.copy()
        self.hira_df.columns = [str(col).replace("\ufeff", "").strip() for col in self.hira_df.columns]

        self.itemseq_col = self._find_column([
            "품목기준코드", "품목기준 코드", "itemSeq", "ITEM_SEQ"
        ])
        self.standard_col = self._find_column([
            "표준코드", "표준 코드"
        ])
        self.representative_col = self._find_column([
            "대표코드", "대표 코드", "제품코드(개정후)"
        ])

        if self.itemseq_col is None:
            raise KeyError(
                "HIRA.csv에서 품목기준코드 컬럼을 찾지 못했습니다. 현재 컬럼: "
                + ", ".join(self.hira_df.columns)
            )

        if self.standard_col is None and self.representative_col is None:
            raise KeyError(
                "HIRA.csv에서 표준코드/대표코드 컬럼을 찾지 못했습니다. 현재 컬럼: "
                + ", ".join(self.hira_df.columns)
            )

        if self.standard_col is not None:
            self.hira_df["표준코드_정제"] = self.hira_df[self.standard_col].apply(self._only_digits)

        if self.representative_col is not None:
            self.hira_df["대표코드_정제"] = self.hira_df[self.representative_col].apply(self._only_digits)

        self.hira_df[self.itemseq_col] = self.hira_df[self.itemseq_col].astype(str).str.strip()

        self.standard_map = {}
        self.representative_map = {}

        if "표준코드_정제" in self.hira_df.columns:
            self.standard_map = (
                self.hira_df[["표준코드_정제", self.itemseq_col]]
                .dropna(subset=["표준코드_정제", self.itemseq_col])
                .drop_duplicates(subset=["표준코드_정제"])
                .set_index("표준코드_정제")[self.itemseq_col]
                .to_dict()
            )

        if "대표코드_정제" in self.hira_df.columns:
            self.representative_map = (
                self.hira_df[["대표코드_정제", self.itemseq_col]]
                .dropna(subset=["대표코드_정제", self.itemseq_col])
                .drop_duplicates(subset=["대표코드_정제"])
                .set_index("대표코드_정제")[self.itemseq_col]
                .to_dict()
            )

    def _find_column(self, candidates):
        for candidate in candidates:
            if candidate in self.hira_df.columns:
                return candidate
        return None

    def _only_digits(self, value):
        if value is None:
            return None
        s = re.sub(r"\D", "", str(value).strip())
        return s if s else None

    def find_item_seq(self, standard_code=None, representative_code=None):
        standard_code = self._only_digits(standard_code)
        representative_code = self._only_digits(representative_code)

        if standard_code and standard_code in self.standard_map:
            return self.standard_map[standard_code]

        if representative_code and representative_code in self.representative_map:
            return self.representative_map[representative_code]

        return None