---
version: alpha
name: JH Personal Evidence
description: 개인 설명 자료와 시제품을 위한 제안 기본값. 회사 공식 브랜드가 아님.
colors:
  primary: "#17232F"
  secondary: "#50606E"
  accent: "#006B5E"
  surface: "#FFFFFF"
  background: "#F6F8FA"
  border: "#CCD5DD"
typography:
  h1:
    fontFamily: "Noto Sans KR, Malgun Gothic, sans-serif"
    fontSize: 2rem
    fontWeight: 700
    lineHeight: 1.35
  h2:
    fontFamily: "Noto Sans KR, Malgun Gothic, sans-serif"
    fontSize: 1.5rem
    fontWeight: 700
    lineHeight: 1.45
  body:
    fontFamily: "Noto Sans KR, Malgun Gothic, sans-serif"
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.7
rounded:
  sm: 4px
  md: 8px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  button-primary-hover:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
  body-text:
    backgroundColor: "{colors.background}"
    textColor: "{colors.primary}"
    typography: "{typography.body}"
  secondary-text:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.secondary}"
    typography: "{typography.body}"
  table-header:
    backgroundColor: "{colors.border}"
    textColor: "{colors.primary}"
    typography: "{typography.body}"
---

## Overview

이 파일은 개인 설명 자료와 시제품에서 출처, 비교 기준과 다음 행동을 읽기 쉽게 보여주기 위한 제안 시작점입니다. 기존 이력서나 PDF에서 추출한 공식 스타일이 아니며, 이번 작업으로 기존 결과물의 디자인을 바꾸지 않습니다.

색과 크기는 개인 자료용 제안입니다. 사용자의 별도 지시, 프로젝트의 기존 토큰, 확인한 회사 브랜드 키트가 있으면 해당 작업에서 그 기준을 우선합니다. 회사별 값은 그 지원 폴더의 `brand/DESIGN.md`에 따로 기록합니다. 공통 파일에 회사별 색이나 미확인 로고를 넣지 않습니다.

형식은 Google의 DESIGN.md 공개 규격을 따릅니다. 값의 문법과 검사 방법은 실제 사용한 CLI 버전에서 재확인합니다.

## Colors

`primary`는 제목과 본문, `secondary`는 보조 설명에 씁니다. `accent`는 중요한 행동 한 가지에 제한해서 사용합니다. `surface`와 `background`는 읽기 영역과 바탕을 구분하며, `border`는 표 머리글과 구획 구분에 씁니다. 구분이 중요한 실제값, 목표값, 예측값과 미검증 값은 색에만 의존하지 않고 글자와 선 모양도 달리합니다.

이 팔레트는 제안값이며 특정 회사의 공식 HEX 값을 주장하지 않습니다. 브랜드 조사에서 가져온 값에는 원문 URL, 확인 날짜와 사용 권한을 별도 브랜드 키트에 남깁니다.

## Typography

웹 본문 기본은 1rem입니다. Noto Sans KR가 없으면 Malgun Gothic, 일반 sans-serif 순서로 대체합니다. 실제 폰트 설치와 파일 사용 권한은 작업 환경에서 확인하며, 문서 내보내기 때 글꼴 대체와 줄바꿈을 검사합니다. 외부 폰트를 자동 다운로드하거나 탑재하지 않습니다.

PDF와 인쇄 자료 본문은 원칙적으로 12pt 이상으로 검토하고, 발표 슬라이드는 실제 표시 크기에서 읽을 수 있는지 검사합니다. 표가 길면 글자를 무리하게 줄이기보다 여러 쪽이나 상세 자료로 나눕니다.

## Layout

화면을 만들기 전에 사용자가 감시, 조작, 비교, 설정, 학습, 탐색, 상세 확인 중 무엇을 하는지 정합니다. 모니터링 화면에 홍보용 큰 제목과 동일한 카드 세 개를 무조건 배치하지 않습니다.

문제와 판단 근거, 실행할 행동 순서를 우선합니다. 표에는 단위와 기간을, 차트 가까이에는 출처와 관찰을 둡니다. 간격은 8px 배수를 기본으로 하되 기존 화면 규칙과 접근성을 우선합니다.

## Elevation & Depth

기본은 평면 배치와 구분선입니다. 그림자는 실제로 겹치는 팝업처럼 깊이를 설명할 때만 씁니다. 흐림 효과나 발광으로 정보의 위계를 대신하지 않습니다.

## Shapes

기본 모서리는 4px 또는 8px입니다. 둥근 상자와 아이콘을 장식 목적으로 반복하지 않습니다. 모바일의 조작 대상은 원칙적으로 44px 이상을 확보하고 키보드 초점 표시를 유지합니다.

## Components

한 화면에서 강조 버튼은 중요한 다음 행동에 사용합니다. 일반 표와 보조 설명은 대비를 확보하고, 실패, 빈 상태, 진행 중과 성공을 글자로 구분합니다.

상태값과 가격, 수하물, 취소 조건 등 의사결정에 필요한 정보는 태그나 색으로만 숨기지 않습니다. 긴 내용과 출처 링크는 상세 영역이나 내보내기에서도 확인할 수 있게 합니다.

## Do's and Don'ts

- 확인한 사실, 가정, 제안과 가상 예시를 구분합니다.
- ELI5 그림은 관계 이해에 필요할 때 만들고, 장식 그림으로 내용을 늘리지 않습니다.
- 회사 로고나 상표를 넣어 공식 제작물처럼 보이게 하지 않습니다.
- 토큰 검사, 색 대비 검사, 모바일 화면 확인과 PDF 전체 쪽 검사를 구분해서 기록합니다.
- 새 토큰을 바꾸면 관련 참조와 생성한 내보내기 파일도 함께 검증합니다.

## Sources

- DESIGN.md 규격: https://github.com/google-labs-code/design.md
- Hermes 공식 선택 스킬: https://hermes-agent.nousresearch.com/docs/reference/optional-skills-catalog
- 개인 작업 원칙: [AGENTS.md](./AGENTS.md)
