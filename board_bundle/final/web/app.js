document.addEventListener("DOMContentLoaded", () => {
  const SAMPLE_PASSAGE = "Temperature is a physical quantity that expresses the degree of hotness or coldness of a substance. The SI unit of temperature is Kelvin (K). In everyday life, temperature is commonly measured in degrees Celsius (°C) or Fahrenheit (°F). Absolute zero is 0 K or -273.15 °C. Heat is energy in transit that flows from a higher temperature body to a lower temperature body until thermal equilibrium is reached.";

  const passageInput = document.getElementById("passage-input");
  const wordCount = document.getElementById("word-count");
  const btnSample = document.getElementById("btn-sample");
  const btnAnalyze = document.getElementById("btn-analyze");
  const btnClear = document.getElementById("btn-clear");
  const btnRetry = document.getElementById("btn-retry");
  const presetButtons = document.getElementById("preset-buttons");
  const langToggle = document.getElementById("lang-toggle");
  const judgeToggle = document.getElementById("judge-toggle");
  const btnCloseJudge = document.getElementById("btn-close-judge");
  const judgeDrawer = document.getElementById("judge-drawer");

  const workingSec = document.getElementById("working-section");
  const workingTimer = document.getElementById("working-timer");
  const workingHost = document.getElementById("working-host");
  const queueNotice = document.getElementById("queue-notice");
  const errorSec = document.getElementById("error-section");
  const errorMsg = document.getElementById("error-msg");
  const resultsSec = document.getElementById("results-section");

  const sentenceList = document.getElementById("sentence-list");
  const origHardText = document.getElementById("orig-hard-text");
  const simpleText = document.getElementById("simple-text");
  const summaryList = document.getElementById("summary-list");
  const glossaryTbody = document.getElementById("glossary-tbody");
  const exampleText = document.getElementById("example-text");
  const quizContainer = document.getElementById("quiz-container");
  const quizScoreBanner = document.getElementById("quiz-score-banner");
  const quizScoreText = document.getElementById("quiz-score-text");

  let timerInterval = null;
  let currentHost = "Laptop";
  let quizAnswers = {};

  // Word counter
  function updateWordCount() {
    const txt = passageInput.value.trim();
    const words = txt ? txt.split(/\s+/).length : 0;
    const isTa = document.body.classList.contains("lang-ta");
    wordCount.textContent = isTa ? `${words} சொற்கள்` : `${words} words`;
  }
  passageInput.addEventListener("input", updateWordCount);

  // Sample Button Handler: Instantly pastes sample passage
  btnSample.addEventListener("click", () => {
    passageInput.value = SAMPLE_PASSAGE;
    updateWordCount();
    passageInput.focus();
    passageInput.scrollIntoView({ behavior: "smooth", block: "center" });
  });

  // Clear button
  btnClear.addEventListener("click", () => {
    passageInput.value = "";
    updateWordCount();
    resultsSec.classList.add("hidden");
    errorSec.classList.add("hidden");
  });

  // Language toggle
  langToggle.addEventListener("click", () => {
    if (document.body.classList.contains("lang-ta")) {
      document.body.classList.remove("lang-ta");
      document.body.classList.add("lang-en");
    } else {
      document.body.classList.remove("lang-en");
      document.body.classList.add("lang-ta");
    }
    updateWordCount();
  });

  // Judge Drawer Toggle
  judgeToggle.addEventListener("click", () => {
    judgeDrawer.classList.toggle("hidden");
    loadJudgeReport();
  });
  btnCloseJudge.addEventListener("click", () => {
    judgeDrawer.classList.add("hidden");
  });

  // Load Status
  function loadStatus() {
    fetch("/api/status")
      .then(r => r.json())
      .then(st => {
        currentHost = st.host || "Local Device";
        workingHost.textContent = currentHost;

        // Offline Chip
        const offChip = document.getElementById("offline-chip");
        if (st.offline) {
          offChip.className = "status-chip chip-offline";
          offChip.querySelector(".chip-label").innerHTML = '<span class="ta-text">இணையம் இன்றி இயங்கும் (OFFLINE)</span><span class="en-text">Works Offline</span>';
        } else {
          offChip.className = "status-chip chip-online";
          offChip.querySelector(".chip-label").innerHTML = '<span class="ta-text">இணையம் இணைப்பில் (ONLINE)</span><span class="en-text">Online</span>';
        }

        // Host Badge
        const devLabel = document.getElementById("device-label");
        if (st.is_pi) {
          devLabel.textContent = "Live on Raspberry Pi 5";
        } else {
          devLabel.textContent = "Laptop Run";
        }

        // Judge Telemetry
        document.getElementById("j-host").textContent = st.host;
        document.getElementById("j-model").textContent = st.model;
        document.getElementById("j-pte-size").textContent = `${(st.pte_size_bytes / (1024*1024)).toFixed(2)} MB (${st.pte_size_bytes.toLocaleString()} bytes)`;
        document.getElementById("j-threads").textContent = `${st.threads} cores`;
        document.getElementById("j-offline").textContent = st.offline_status;
        document.getElementById("j-route").textContent = st.offline ? "None (Offline mode active)" : "Default route present";

        if (st.last_run) {
          document.getElementById("j-latency").textContent = `${st.last_run.elapsed_s} s`;
          document.getElementById("j-rss").textContent = `${st.last_run.rss_mb} MiB`;
        }
      })
      .catch(() => {});
  }
  loadStatus();

  // Load Demo Passages
  fetch("/api/passages")
    .then(r => r.json())
    .then(passages => {
      presetButtons.innerHTML = "";
      passages.forEach(p => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn-secondary btn-sm preset-btn";
        btn.textContent = `${p.subj_ta || p.subj_en}: ${p.title_ta || p.title_en}`;
        btn.addEventListener("click", () => {
          passageInput.value = p.text;
          updateWordCount();
          passageInput.focus();
        });
        presetButtons.appendChild(btn);
      });
    })
    .catch(() => {});

  // Load Judge Report
  function loadJudgeReport() {
    fetch("/api/report")
      .then(r => r.json())
      .then(d => {
        if (d.report) {
          document.getElementById("judge-report-content").textContent = d.report;
        } else {
          document.getElementById("judge-report-content").textContent = "Evaluation report not generated yet.";
        }
      })
      .catch(() => {
        document.getElementById("judge-report-content").textContent = "No report available.";
      });
  }

  // Highlight Sentence in Reading View
  function highlightSentence(idx) {
    document.querySelectorAll(".sentence-item").forEach(el => {
      el.classList.remove("sentence-cited-highlight");
    });
    const target = document.getElementById(`sent-${idx}`);
    if (target) {
      target.classList.add("sentence-cited-highlight");
      target.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }

  // Run Pipeline
  btnAnalyze.addEventListener("click", () => {
    const text = passageInput.value.trim();
    if (!text) {
      alert("Please paste or select a passage first.");
      return;
    }

    resultsSec.classList.add("hidden");
    errorSec.classList.add("hidden");
    workingSec.classList.remove("hidden");
    workingTimer.textContent = "0.0";
    queueNotice.classList.add("hidden");

    const tStart = Date.now();
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      const elapsed = ((Date.now() - tStart) / 1000).toFixed(1);
      workingTimer.textContent = elapsed;
    }, 200);

    fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonPostSafe({ text })
    })
      .then(r => r.json())
      .then(data => {
        if (data.error) {
          throw new Error(data.error);
        }
        pollJob(data.job);
      })
      .catch(err => {
        clearInterval(timerInterval);
        workingSec.classList.add("hidden");
        errorSec.classList.remove("hidden");
        errorMsg.textContent = err.message || "Failed to start processing.";
      });
  });

  btnRetry.addEventListener("click", () => {
    btnAnalyze.click();
  });

  function jsonPostSafe(obj) {
    return JSON.stringify(obj);
  }

  function pollJob(jid) {
    const pollInterval = setInterval(() => {
      fetch(`/api/job/${jid}`)
        .then(r => r.json())
        .then(job => {
          if (job.stage === "queued") {
            queueNotice.classList.remove("hidden");
          } else if (job.stage === "working") {
            queueNotice.classList.add("hidden");
          } else if (job.stage === "done") {
            clearInterval(pollInterval);
            clearInterval(timerInterval);
            workingSec.classList.add("hidden");
            renderResults(job.result);
            loadStatus();
          } else if (job.stage === "error") {
            clearInterval(pollInterval);
            clearInterval(timerInterval);
            workingSec.classList.add("hidden");
            errorSec.classList.remove("hidden");
            errorMsg.textContent = job.err || "Model run failed.";
          }
        })
        .catch(err => {
          clearInterval(pollInterval);
          clearInterval(timerInterval);
          workingSec.classList.add("hidden");
          errorSec.classList.remove("hidden");
          errorMsg.textContent = "Connection to local server lost.";
        });
    }, 500);
  }

  // Render Results
  function renderResults(res) {
    if (!res) return;

    // 1. Sentences
    sentenceList.innerHTML = "";
    const sents = res.sents || [];
    const hardIdx = res.hard || 1;
    sents.forEach((s, i) => {
      const sid = i + 1;
      const isHard = (sid === hardIdx);
      const row = document.createElement("div");
      row.id = `sent-${sid}`;
      row.className = `sentence-item ${isHard ? "sentence-hard" : ""}`;
      row.innerHTML = `
        <span class="sentence-num">[S${sid}]</span>
        <span class="sentence-text">${escapeHtml(s)}</span>
        ${isHard ? '<span class="hard-badge"><span class="ta-text">கடின வாக்கியம்</span><span class="en-text">Hardest Sentence</span></span>' : ''}
      `;
      sentenceList.appendChild(row);
    });

    // 2. Simplification
    const origTxt = sents[hardIdx - 1] || "";
    origHardText.textContent = origTxt;
    simpleText.textContent = res.simple || origTxt;

    // 3. Summary
    summaryList.innerHTML = "";
    const summ = res.summary || [];
    summ.forEach(pt => {
      const li = document.createElement("li");
      li.className = "summary-item";
      const cites = (pt.cite || []).map(c => `<span class="summary-cite" data-cite="${c}">[S${c}]</span>`).join(" ");
      li.innerHTML = `
        <span class="summary-bullet">•</span>
        <span class="summary-txt">${escapeHtml(pt.txt)}</span>
        ${cites}
      `;
      li.querySelectorAll(".summary-cite").forEach(el => {
        el.addEventListener("click", () => {
          const cid = parseInt(el.getAttribute("data-cite"), 10);
          highlightSentence(cid);
        });
      });
      summaryList.appendChild(li);
    });

    // 4. Glossary
    glossaryTbody.innerHTML = "";
    const terms = res.terms || [];
    if (terms.length === 0) {
      glossaryTbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#64748b;">இப்பகுதியில் குறிப்பிட்ட கலைச்சொற்கள் இல்லை / No terms found</td></tr>';
    } else {
      terms.forEach(t => {
        const tr = document.createElement("tr");
        const taVal = t.ta || '<em style="color:#94a3b8;">no Tamil entry yet</em>';
        tr.innerHTML = `
          <td><strong>${escapeHtml(t.en)}</strong></td>
          <td class="term-ta">${taVal}</td>
          <td>${t.def ? escapeHtml(t.def) : 'Class 9 Glossary Term'}</td>
        `;
        glossaryTbody.appendChild(tr);
      });
    }

    // 5. Example
    const ex = res.example || {};
    exampleText.textContent = ex.txt || "No everyday example found.";

    // 6. Interactive Quiz
    renderQuiz(res.quiz || [], sents);

    resultsSec.classList.remove("hidden");
    resultsSec.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderQuiz(quizList, sents) {
    quizContainer.innerHTML = "";
    quizAnswers = {};
    quizScoreBanner.classList.add("hidden");

    if (quizList.length === 0) {
      quizContainer.innerHTML = "<p>No quiz questions available.</p>";
      return;
    }

    quizList.forEach((q, qIdx) => {
      const qDiv = document.createElement("div");
      qDiv.className = "quiz-item";
      const opts = q.opts || [q.a || "Option A", "Option B", "Option C", "Option D"];
      const correctIdx = typeof q.ans === "number" ? q.ans : 0;
      const citeId = q.cite || 1;

      let optsHtml = "";
      opts.forEach((opt, optIdx) => {
        optsHtml += `<button type="button" class="quiz-opt-btn" data-q="${qIdx}" data-opt="${optIdx}">${escapeHtml(opt)}</button>`;
      });

      qDiv.innerHTML = `
        <div class="quiz-question">${qIdx + 1}. ${escapeHtml(q.q)}</div>
        <div class="quiz-options">${optsHtml}</div>
        <div id="quiz-fb-${qIdx}" class="quiz-feedback hidden"></div>
      `;

      qDiv.querySelectorAll(".quiz-opt-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          handleQuizAnswer(qIdx, parseInt(btn.getAttribute("data-opt"), 10), correctIdx, citeId, qDiv, opts[correctIdx], sents);
        });
      });

      quizContainer.appendChild(qDiv);
    });
  }

  function handleQuizAnswer(qIdx, selectedOpt, correctIdx, citeId, qDiv, correctText, sents) {
    if (quizAnswers[qIdx] !== undefined) return;
    quizAnswers[qIdx] = (selectedOpt === correctIdx);

    const buttons = qDiv.querySelectorAll(".quiz-opt-btn");
    buttons.forEach((btn, idx) => {
      btn.disabled = true;
      if (idx === correctIdx) {
        btn.classList.add("correct");
      } else if (idx === selectedOpt) {
        btn.classList.add("incorrect");
      }
    });

    const fb = qDiv.querySelector(".quiz-feedback");
    fb.classList.remove("hidden");
    highlightSentence(citeId);

    const isTa = document.body.classList.contains("lang-ta");
    if (selectedOpt === correctIdx) {
      fb.className = "quiz-feedback correct-fb";
      fb.textContent = isTa ? `✓ சரியான விடை! (ஆதாரம் வாக்கியம் [S${citeId}])` : `✓ Correct! (Supported by sentence [S${citeId}])`;
    } else {
      fb.className = "quiz-feedback incorrect-fb";
      fb.textContent = isTa ? `✗ தவறான விடை. சரியான பதில்: "${correctText}" (ஆதாரம் [S${citeId}])` : `✗ Incorrect. Correct answer: "${correctText}" (Supported by [S${citeId}])`;
    }

    // Check if all questions answered
    const totalQ = qDiv.parentElement.querySelectorAll(".quiz-item").length;
    if (Object.keys(quizAnswers).length === totalQ) {
      const score = Object.values(quizAnswers).filter(Boolean).length;
      quizScoreBanner.classList.remove("hidden");
      quizScoreText.textContent = isTa ? `விடை சோதனை முடிவு: ${score} / ${totalQ} கேள்விகள் சரி` : `Final Quiz Score: ${score} / ${totalQ} correct`;
    }
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
