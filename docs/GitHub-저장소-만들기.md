# GitHub 저장소 만들기 (YunchanYeo)

로컬 코드는 이미 커밋되어 있습니다. 아래만 하면 됩니다.

---

## 1. GitHub에서 빈 저장소 만들기

1. 브라우저에서 로그인: https://github.com/YunchanYeo  
2. 오른쪽 위 **+** → **New repository**  
3. 설정:
   - **Repository name:** `shehuikexue`（원하면 다른 이름도 가능）
   - **Public** 推荐（Actions 무료 한도 넉넉）
   - **不要**勾选 “Add a README” / “Add .gitignore”（로컬에 이미 있음）
4. **Create repository**

---

## 2. Mac 터미널에서 push

```bash
cd /Users/yeoyunchan/Desktop/shehuikexue
git remote set-url origin https://github.com/YunchanYeo/shehuikexue.git
git push -u origin main
```

- 저장소 이름을 `shehuikexue` 가 아니게 만들었다면, URL의 마지막 부분만 본인 저장소 이름으로 바꾸세요.
- 처음 push 시 GitHub 로그인 창이 뜹니다（浏览器或 Personal Access Token）.

---

## 3. Actions로 설치 파일 빌드

push 가 끝난 뒤:

1. https://github.com/YunchanYeo/shehuikexue  
2. **Actions** → **Build installers** → **Run workflow**  
3. 완료 후 **Artifacts** 에서 `SpeechEval.dmg` / `SpeechEval-Setup.exe` 다운로드

자세한 설명: [GitHub-Actions-빌드.md](GitHub-Actions-빌드.md)

---

## （선택）gh CLI 로 한 번에 만들기

터미널에 `gh` 가 있고 로그인되어 있다면:

```bash
cd /Users/yeoyunchan/Desktop/shehuikexue
gh auth login
gh repo create shehuikexue --public --source=. --remote=origin --push
```

`gh auth login` 은 브라우저로 한 번만 하면 됩니다.
