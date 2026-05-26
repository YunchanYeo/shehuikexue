# Actions「워크플로우를 실행할 수 없음」해결

저장소: https://github.com/YunchanYeo/shehuikexue

---

## 1. Actions 켜기（가장 흔한 원인）

1. 저장소 **Settings**（설정）
2. 왼쪽 **Actions** → **General**
3. **Actions permissions** 에서  
   **「Allow all actions and reusable workflows」** 선택
4. 아래 **Workflow permissions** →  
   **「Read and write permissions」** 선택 → **Save**

처음 Actions 탭에 들어갔을 때 초록색  
**「I understand my workflows, go ahead and enable them」**  
버튼이 보이면 **반드시 클릭**하세요.

---

## 2. Run workflow 버튼 위치

「Run workflow」는 **목록 화면**이 아니라 **워크플로우 상세**에 있습니다.

1. **Actions** 탭
2. 왼쪽에서 **「Build installers」** 클릭（글씨를 눌러야 함）
3. 오른쪽 위 **「Run workflow」** ▼ → Branch: **main** → **Run workflow**

---

## 3. push 하면 자동 실행（버튼 없이）

`main` 브랜치에 push 하면 빌드가 **자동으로** 돌아가도록 설정되어 있습니다.

Mac 터미널:

```bash
cd /Users/yeoyunchan/Desktop/shehuikexue
git pull
# 아무 작은 수정 후
git commit --allow-empty -m "Trigger Actions build"
git push
```

push 후 **Actions** 탭에 노란색 ●（진행 중）이 보이면 성공입니다.

---

## 4. 그래도 안 될 때

| 증상 | 확인 |
|------|------|
| Actions 탭 자체가 없음 | 저장소가 Public 인지, 본인 계정으로 로그인했는지 |
| Run workflow 가 회색 | Settings → Actions 에서 비활성화 여부 |
| Fork 가 아닌 본인 저장소인지 | `YunchanYeo/shehuikexue` 맞는지 |
| 브랜치 | 반드시 **main**（workflow 파일이 있는 브랜치）|

---

## 5. 빌드가 끝나면

완료된 run 클릭 → 맨 아래 **Artifacts**:

- `SpeechEval-macOS` → `.dmg`
- `SpeechEval-Windows` → `SpeechEval-Setup.exe`
