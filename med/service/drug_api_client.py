import requests
from urllib.parse import unquote


class DrugApiClient:
    def __init__(self, service_key):
        self.service_key = service_key
        self.api_url = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
        self.cache = {}

    def _empty_result(self, status):
        return {
            "API상태": status,
            "효능": None,
            "사용법": None,
            "주의사항경고": None,
            "상호작용": None,
            "부작용": None,
            "보관법": None,
        }

    def build_error_result(self, status):
        return self._empty_result(status)

    def fetch(self, item_seq):
        if item_seq is None:
            return self._empty_result("NO_ITEMSEQ")

        item_seq = str(item_seq).strip()
        if item_seq == "" or item_seq.lower() == "nan":
            return self._empty_result("NO_ITEMSEQ")

        if item_seq in self.cache:
            return self.cache[item_seq]

        params = {
            "ServiceKey": unquote(self.service_key),
            "pageNo": "1",
            "numOfRows": "1",
            "itemSeq": item_seq,
            "type": "json"
        }

        try:
            response = requests.get(self.api_url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            header = data.get("header", {})
            result_code = header.get("resultCode")
            result_msg = header.get("resultMsg")

            if result_code and result_code != "00":
                result = self._empty_result(f"API_ERROR_{result_code}: {result_msg}")
                print(f"[DrugApiClient] API error - itemSeq={item_seq}, code={result_code}, msg={result_msg}")
                self.cache[item_seq] = result
                return result

            items = data.get("body", {}).get("items", [])
            if not items:
                result = self._empty_result("NO_ITEM")
                self.cache[item_seq] = result
            else:
                item = items[0]
                result = {
                    "API상태": "OK",
                    "효능": item.get("efcyQesitm"),
                    "사용법": item.get("useMethodQesitm"),
                    "주의사항경고": item.get("atpnWarnQesitm"),
                    "상호작용": item.get("intrcQesitm"),
                    "부작용": item.get("seQesitm"),
                    "보관법": item.get("depositMethodQesitm"),
                }
                self.cache[item_seq] = result
            return result

        except requests.RequestException as e:
            result = self._empty_result(f"REQUEST_ERROR: {e}")
            print(f"[DrugApiClient] request failed - itemSeq={item_seq}, error={e}")
            return result
        except ValueError as e:
            result = self._empty_result(f"JSON_ERROR: {e}")
            print(f"[DrugApiClient] json parse failed - itemSeq={item_seq}, error={e}")
            return result
        except Exception as e:
            result = self._empty_result(f"ERROR: {e}")
            print(f"[DrugApiClient] unexpected error - itemSeq={item_seq}, error={e}")
            return result
