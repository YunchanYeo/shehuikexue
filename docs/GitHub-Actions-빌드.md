# GitHub Actions로 설치 파일 만들기 (Mac만 있어도 OK)

Windows PC 없이 **Mac에서 코드를 push**하면, GitHub 클라우드에서 자동으로:

- `SpeechEval.dmg` (macOS)
- `SpeechEval-Setup.exe` (Windows)

를 빌드합니다.

---

## 1. GitHub에 올리기

```bash
cd /path/to/shehuikexue
git init   # 아직 없다면
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

---

## 2. 빌드 실행 (수동, 가장 쉬움)

1. GitHub 저장소 페이지 → **Actions** 탭  
2. 왼쪽 **「Build installers」** 클릭  
3. 오른쪽 **「Run workflow」** → **Run workflow**  
4. 약 **30~60분** 대기 (Windows 쪽이 더 오래 걸릴 수 있음)  
5. 완료된 실행 클릭 → 아래 **Artifacts** 에서 다운로드:
   - `SpeechEval-macOS` → `.dmg`
   - `SpeechEval-Windows` → `SpeechEval-Setup.exe`

이 파일을 사용자에게내면 됩니다.

---

## 3. 태그로 Release 만들기 (선택)

버전을 붙여 배포할 때:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Actions가 돌아간 뒤 **Releases** 탭에 dmg / exe가 자동으로 올라갑니다.  
사용자에게 Release 페이지 링크만 공유하면 됩니다.

---

## 4. 자주 묻는 것

**Q：Mac에서 exe를 직접 못 만드는데 이건 되나요?**  
A：네. Windows 빌드는 GitHub의 `windows-latest` 가상 머신에서 돌아갑니다.

**Q：비용?**  
A：공개(public) 저장소는 Actions 무료 한도가 넉넉합니다. Private는 월 한도 확인.

**Q：빌드 실패 시**  
A：Actions 로그에서 빨간 단계 클릭 → 오류 메시지 확인. 대부분 의존성/타임아웃 문제입니다.

**Q：코드 수정 후 다시 받으려면?**  
A：`git push` 후 Actions에서 **Run workflow** 다시 실행.

---

## 5. 로컬 Mac에서 dmg만 만들 때

GitHub 없이 Mac 설치 파일만 필요하면:

```bash
./scripts/build_mac.sh
```

Windows exe는 Actions Artifacts 또는 Windows PC / 위 2번 방법을 사용하세요.
