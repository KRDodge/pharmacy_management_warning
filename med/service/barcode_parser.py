import re
import pandas as pd


class BarcodeParser:
    def parse(self, barcode):
        if pd.isna(barcode):
            return {
                "정규화바코드": None,
                "표준코드후보": None,
                "대표코드후보": None,
                "상태": "EMPTY"
            }

        code = re.sub(r"\D", "", str(barcode))

        if not code:
            return {
                "정규화바코드": None,
                "표준코드후보": None,
                "대표코드후보": None,
                "상태": "EMPTY"
            }

        match = re.search(r"880\d+", code)
        if not match:
            return {
                "정규화바코드": code,
                "표준코드후보": None,
                "대표코드후보": None,
                "상태": "NO_880"
            }

        normalized = match.group()

        # 표준코드후보: 880부터 시작하는 전체 코드
        standard_candidate = normalized

        # 대표코드후보: 880 제거 후 마지막 2자리 제거 전 앞부분
        # 네 규칙: 회사4 + 품목4 = 8자리
        body = normalized[3:]
        representative_candidate = body[:8] if len(body) >= 8 else None

        return {
            "정규화바코드": normalized,
            "표준코드후보": standard_candidate,
            "대표코드후보": representative_candidate,
            "상태": "OK"
        }