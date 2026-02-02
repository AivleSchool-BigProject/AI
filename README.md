# github_study_group

깃허브 공부 스터디 그룹

main <- dev <- feature-*

## Branch Roles
### main
- 배포 가능한 최종 안정 브랜치
- 모든 테스트 및 검증 완료 상태
- 직접 커밋 금지
- dev 브랜치에서 PR을 통해서만 병합

### dev
- 개발 완료된 기능들이 모이는 통합 브랜치
- 배포 직전 단계
- feature 브랜치들이 병합되는 대상

### feature/*
- 기능 단위 개발 브랜치
- 각 개발자는 자신의 기능을 feature 브랜치에서 작업
- 작업 완료 후 dev 브랜치로 PR 생성

## git Command
```
git fetch origin
```
- 원격 저장소(GitHub)의 최신 정보를 로컬 임시 저장소에만 업데이트
- 현재 브랜치에는 영향 없음
- 안전하게 변경 사항을 확인할 때 사용

```
git pull origin dev
```
- git fetch + git merge를 한 번에 수행
- 원격 브랜치의 변경 사항을 로컬 브랜치에 바로 반영
- 충돌 가능성이 있으므로 작업 중일 때는 주의

```
git checkout 브랜치명
```
- 해당 브랜치로 이동
- 로컬에 브랜치가 없을 시에는 원격 기준으로 생성함

```
git checkout -b 브랜치명 origin/브랜치명
```
- 새로운 feature 브랜치를 생성하고 바로 이동 단 우측에 있는 origin/브랜치명은 source 브랜치를 잡아줄 때 사용

```
git branch -a
```
- 로컬 + 원격 브랜치 리스트 전체 확인


## 커밋 메시지 규칙

feat	새로운 기능에 대한 커밋
fix	버그 수정에 대한 커밋
build	빌드 관련 파일 수정 / 모듈 설치 또는 삭제에 대한 커밋
chore	그 외 자잘한 수정에 대한 커밋
ci	ci 관련 설정 수정에 대한 커밋
docs	문서 수정에 대한 커밋
style	코드 스타일 혹은 포맷 등에 관한 커밋
refactor	코드 리팩토링에 대한 커밋
test	테스트 코드 수정에 대한 커밋
perf	성능 개선에 대한 커밋