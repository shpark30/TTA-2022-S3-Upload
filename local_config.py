MMDD = "(11|12|01|02|03)\.(3[0-1]|[0-2][0-9])"

DATA_INFO_PATH = "W:/2022 TTA/2022 이관/{0}/data_info.csv"
RESULT_DIR_ORIGINAL = "W:/2022 TTA/2022 이관/{0}/검사 결과/{1}"
RESULT_DIR_EDIT = "W:/2022 TTA/2022 이관/{0}/검사 결과/EDIT_{1}"
REPORT_DIR_ORIGINAL = "W:/2022 TTA/2022 이관/{0}/체크리스트/{1}"
REPORT_DIR_EDIT = "W:/2022 TTA/2022 이관/{0}/체크리스트/EDIT_{1}"
RULE_DIR_ORIGIN = "W:/2022 TTA/2022 이관/{0}/검사 규칙/{1}"
RULE_DIR_EDIT = "W:/2022 TTA/2022 이관/{0}/검사 규칙/EDIT_{1}"

ID_FORMAT = "\d-\d{3}-\d{3}"
CATEGORY_FORMAT = "[A-Z]{2}"
RESULT_TYPE_FORMAT = "(사전이슈리포트|구문정확성사전검사결과|통계다양성사전검사결과|사전검사형식오류목록|사전검사구조오류목록|사전검사파일오류목록)"
DATE_FORMAT = "22(08|09|10|11|12)(31|30|[0-2][0-9])"
EXTENSION_FORMAT = "(csv|xlsx|docx)"
FILE_NAME_FORMAT = f"^\[{ID_FORMAT}-{CATEGORY_FORMAT}\] {RESULT_TYPE_FORMAT}_.+_{DATE_FORMAT}\.{EXTENSION_FORMAT}$"

RULE_NAME_FORMAT = f"^\[{ID_FORMAT}-{CATEGORY_FORMAT}\] (사전검사규칙|최종검사규칙)_.+\.json$"
