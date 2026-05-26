(function () {
  const ua = navigator.userAgent.toLowerCase();
  const isMac = /mac|iphone|ipad|ipod/.test(ua);
  const isWin = /win/.test(ua);

  const hint = document.getElementById("os-hint");
  const cardMac = document.getElementById("card-mac");
  const cardWin = document.getElementById("card-win");

  if (isMac) {
    hint.textContent = "检测到您可能在使用 Mac，推荐下载 macOS 版。";
    cardMac.classList.add("recommended");
  } else if (isWin) {
    hint.textContent = "检测到您可能在使用 Windows，推荐下载 Windows 版。";
    cardWin.classList.add("recommended");
  } else {
    hint.textContent = "请根据您的电脑系统选择对应安装包。";
  }

  async function checkFile(url, btnId, missingId) {
    try {
      const res = await fetch(url, { method: "HEAD" });
      if (!res.ok) throw new Error("missing");
    } catch {
      const btn = document.getElementById(btnId);
      const msg = document.getElementById(missingId);
      if (btn) {
        btn.classList.add("disabled");
        btn.removeAttribute("download");
        btn.href = "#";
        btn.textContent = btnId === "btn-mac" ? "暂未提供 Mac 版" : "暂未提供 Windows 版";
      }
      if (msg) msg.hidden = false;
    }
  }

  checkFile("releases/SpeechEval.dmg", "btn-mac", "mac-missing");
  checkFile("releases/SpeechEval-Setup.exe", "btn-win", "win-missing");

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      const name = tab.dataset.tab;
      document.getElementById("steps-mac").classList.toggle("hidden", name !== "mac");
      document.getElementById("steps-win").classList.toggle("hidden", name !== "win");
    });
  });
})();
