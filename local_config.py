DATA_INFO_PATH = "C:/Users/seohy/workspace/upload_S3/test-data/data_info.csv"
RESULT_DIR_ORIGINAL = "W:/2022 TTA/2022 사전 검사 결과서/검사 결과/ORIGINAL"
RESULT_DIR_EDIT = "W:/2022 TTA/2022 사전 검사 결과서/검사 결과/EDIT"
REPORT_DIR_ORIGINAL = "W:/2022 TTA/2022 사전 검사 결과서/체크리스트/ORIGINAL"
REPORT_DIR_EDIT = "W:/2022 TTA/2022 사전 검사 결과서/체크리스트/EDIT"

ID_FORMAT = "\d-\d{3}-\d{3}"
CATEGORY_FORMAT = "[A-Z]{2}"
RESULT_TYPE_FORMAT = "(사전이슈리포트|구문정확성사전검사결과|통계다양성사전검사결과|사전검사형식오류목록|사전검사구조오류목록|사전검사파일오류목록)"
DATE_FORMAT = "22(08|09|10|11|12)(31|30|[0-2][0-9])"
EXTENSION_FORMAT = "(csv|xlsx|docx)"
FILE_NAME_FORMAT = f"^\[{ID_FORMAT}-{CATEGORY_FORMAT}\] {RESULT_TYPE_FORMAT}_.+_{DATE_FORMAT}\.{EXTENSION_FORMAT}$"

RULE_NAME_FORMAT = f"^\[{ID_FORMAT}-{CATEGORY_FORMAT}\] (사전검사규칙|최종검사규칙)_.+\.json$"
