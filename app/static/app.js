// 탭 전환
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    const target = tab.dataset.tab;
    document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t === tab));
    document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("active", p.id === target));
  });
});

// 각 엔드포인트의 입력을 모아 요청 body를 만든다.
function buildRequest(endpoint) {
  if (endpoint === "summarize") {
    const file = document.getElementById("summarize-file").files[0];
    const text = document.getElementById("summarize-text").value;
    const form = new FormData();
    if (file) form.append("file", file);
    if (text) form.append("text", text);
    return { body: form }; // multipart — Content-Type은 브라우저가 설정
  }
  const json = {
    project: () => ({
      members: val("project-members"),
      tasks: val("project-tasks"),
      deadline: val("project-deadline"),
    }),
    planner: () => ({
      exams: val("planner-exams"),
      timetable: val("planner-timetable"),
      hours: val("planner-hours"),
    }),
    search: () => ({ query: val("search-query") }),
  }[endpoint]();
  return { body: JSON.stringify(json), headers: { "Content-Type": "application/json" } };
}

function val(id) {
  return document.getElementById(id).value.trim();
}

// 실행 버튼
document.querySelectorAll(".run").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const endpoint = btn.dataset.endpoint;
    const result = document.getElementById(`${endpoint}-result`);
    const { body, headers } = buildRequest(endpoint);

    btn.disabled = true;
    result.textContent = "⏳ 생성 중...";
    try {
      const res = await fetch(`/api/${endpoint}`, { method: "POST", body, headers });
      const data = await res.json();
      if (!res.ok) {
        result.textContent = `⚠️ 오류: ${data.detail || res.status}`;
      } else {
        result.textContent = data.result;
      }
    } catch (err) {
      result.textContent = `⚠️ 요청 실패: ${err.message}`;
    } finally {
      btn.disabled = false;
    }
  });
});
