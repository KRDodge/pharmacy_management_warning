import pandas as pd
import re

# CSV 읽기
df = pd.read_csv("약국만.csv", dtype=str)

def parse_barcode(barcode):
    if pd.isna(barcode):
        return pd.Series([None, None, None, None, None, None, "EMPTY"])

    # 숫자만 남기기
    code = re.sub(r"\D", "", str(barcode))

    if not code:
        return pd.Series([None, None, None, None, None, None, "EMPTY"])

    # 처음 등장한 880부터 끝까지 추출
    match = re.search(r"880\d+", code)

    if not match:
        return pd.Series([code, None, None, None, None, None, "NO_880"])

    normalized = match.group()

    # 880 제거 후 본문
    body = normalized[3:]

    # 회사코드 4 + 품목코드 4 + 최소 나머지 2자리(수량코드, 검증번호)는 있어야 함
    if len(body) < 10:
        return pd.Series([normalized, body, None, None, None, None, "TOO_SHORT"])

    company_code = body[:4]
    item_code = body[4:8]
    quantity_code = body[-2]
    check_digit = body[-1]

    return pd.Series([
        normalized,
        body,
        company_code,
        item_code,
        quantity_code,
        check_digit,
        "OK"
    ])

# 새 컬럼 생성
df[[
    "정규화바코드",
    "파싱문자열",
    "회사코드",
    "품목코드",
    "수량코드",
    "검증번호",
    "상태"
]] = df["바코드"].apply(parse_barcode)

# 결과 저장
df.to_csv("약국만_정제.csv", index=False, encoding="utf-8-sig")

print("완료: 약국만_정제.csv 생성")