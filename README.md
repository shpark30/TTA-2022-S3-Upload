# TTA-2022-S3-Upload
TTA 사업 중 품질 검사 결과물(산출물) S3 저장소에 자동 업로드하는 프로그램


- [x] 파일명 끝에 (\d)가 붙어있으면 파일은 보존, 파일명만 수정
    - 수정 후 동일한 파일명 뜨면 에러 -> 복사본인 경우 체크할 수 있음(
- [x] docType이 중복으로 사용된 경우 제거 (CorrectBody)
- [x] dunder 제거
- [x] 파일명은 완전히 동일한데, 날짜만 다른 경우 filtering 해야 함


# 추가 기능 목록
[ ] 체크리스트: 해당 날짜에 새로 완료된 체크리스트만 EDIT
[ ] 검사 규칙: 해당 날짜에 새로 완료된 검사 규칙만 생성