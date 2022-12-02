import sqlalchemy as db
import pandas as pd
import access_info as info
from utils import extract_task_id


engine = db.create_engine(info.url)

rules: pd.DataFrame = pd.read_sql(info.rule_query, engine)
rules.sort_values(by="group_nm")


# 구문 검사 완료한 데이터셋만 필터링
def get_diagnosed_hist() -> pd.DataFrame:
    diagnosis_hist: pd.DataFrame = pd.read_sql(info.syntax_query, engine)
    has_diagnosed_cond: pd.Series = diagnosis_hist["exec_sttus_cd"] == "COMPLETE"
    diagnosed_hist: pd.DataFrame = diagnosis_hist[has_diagnosed_cond]["dgnss_id"]
    .drop_duplicates(subset="dgnss_id")
    return diagnosed_hist.loc[:, ["dgnss_id", "exec_sttus_cd"]]


diagnosed_hist: pd.DataFrame = get_diagnosed_hist()
rules = pd.merge(
    left=result,
    right=diagnosed_hist,
    how="left",
    on="dgnss_id")

has_diagnosed_cond = rules["exec_sttus_cd"]
diag_datasets = rules[has_diagnosed_cond]


# 과제 번호 추출
def except_extract_task_id(text):
    try:
        return extract_task_id(text)
    except AttributeError as e:
        print(e)
        return


diag_datasets['group_id'] = diag_datasets['group_nm'].apply(
    except_extract_task_id)
diag_datasets['task_id'] = diag_datasets['dgnss_nm'].apply(
    except_extract_task_id)
