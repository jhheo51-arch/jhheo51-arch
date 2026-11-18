# Not Sent 원인 분류 로컬 검토

## 문제와 대상

MC 채용 과제에서 정한 `Not Sent` 처리 기준을 면접관이 입력과 결과로 확인할 수 있게 만든 가상 데이터 검토입니다. 실제 Marketing Cloud 계정에 연결하거나 메일을 보내지 않습니다.

## 사용 방법

Python 표준 라이브러리만 사용합니다. 이 폴더에서 실행합니다.

```powershell
python not_sent_review.py --input sample_not_sent.csv --job-id JOB-CASE-001 --out-dir results
python -m unittest -v test_not_sent_review.py
```

`results/reviewed_rows.csv`에는 선택한 발송의 각 Reason과 다음 확인이, `results/summary.json`에는 분류별 건수가 기록됩니다. 다른 JobID의 행은 선택 결과에 넣지 않습니다. 필수 열 누락과 같은 발송의 중복 SubscriberKey는 정상 결과로 처리하지 않고 오류로 멈춥니다.

## 자료와 계산 범위

입력 8행은 모두 가상입니다. `JOB-CASE-001`의 7행 중 보호 유지 4건, 원천 확인 1건, 콘텐츠 확인 1건, 사람 확인 1건입니다. 자동 재발송은 0건입니다. 이 건수는 실제 발송 누락 건수나 MC에서 계산한 지표가 아닙니다.

Reason 예시는 [Salesforce의 Not Sent 확인 안내](https://help.salesforce.com/s/articleView?id=000392619&language=en_US&type=1)와 [발송 문제 해결 안내](https://help.salesforce.com/s/articleView?id=000389518&language=en_US&type=1)를 기준으로 삼았습니다. 문서에 없는 `Unexpected Account Policy`는 알 수 없는 Reason을 임의로 처리하지 않는지 보려고 넣은 가상 값입니다.

## 확인과 사용 제한

자동 검사 4개는 보호 대상의 자동 재발송 방지, JobID 필터, 중복 고객 및 필수 열 누락 시 중단을 확인합니다. 규칙이 실제 MC의 모든 Reason이나 발송 분류를 대표하지 않습니다. 실제 운영에 쓰려면 계정별 Reason, 발송 분류, 구독자 상태와 제외 정책을 확인하고 권한이 있는 환경에서 다시 시험해야 합니다.

## 앞으로 추진

실제 MC 계정 접근이 허용되면 개인 정보가 없는 시험 발송의 추출 파일을 사용해 Reason 값과 분류 기준을 대조합니다. 기대 결과와 실제 결과가 다르면 규칙을 수정하고, 보호 대상이 재발송되지 않는지 확인해야 완료로 판단합니다.
