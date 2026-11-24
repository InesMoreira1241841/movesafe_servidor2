// Só corre quando o HTML estiver carregado
document.addEventListener("DOMContentLoaded", function () {

    const SESSAO = window.SESSAO || 1;
    const NOMES = { segura: "SEGURA", limite: "LIMITE", sobrecarga: "SOBRECARGA" };

    let somAtivo = false;
    let audioCtx = null;
    let ultimoBip = 0;

    /* ============ 1. GRÁFICOS ============ */
    function criarGrafico(id, series) {
        const canvas = document.getElementById(id);
        if (!canvas) return null;

        return new Chart(canvas, {
            type: "line",
            data: {
                labels: [],
                datasets: series.map(s => ({
                    label: s.nome, data: [], borderColor: s.cor, backgroundColor: s.cor,
                    pointRadius: 0, borderWidth: 2, tension: 0.3, yAxisID: s.eixo || "y"
                }))
            },
            options: {
                animation: false,
                plugins: { legend: { display: series.length > 1 } },
                scales: {
                    x: { ticks: { maxTicksLimit: 6 } },
                    y: {},
                    y2: {
                        position: "right",
                        display: series.some(s => s.eixo === "y2"),
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }

    const gTemp = criarGrafico("gTemp", [{ nome: "Temp", cor: "#ea580c" }]);
    const gFc = criarGrafico("gFc", [{ nome: "FC", cor: "#dc2626" }]);
    const gRmssd = criarGrafico("gRmssd", [{ nome: "RMSSD", cor: "#2563eb" }]);
    const gEmg = criarGrafico("gEmg", [
        { nome: "sEMG RMS", cor: "#16a34a" },
        { nome: "Fadiga %", cor: "#9333ea", eixo: "y2" }
    ]);

    function preencher(g, labels, ...series) {
        if (!g) return;
        g.data.labels = labels;
        series.forEach((s, i) => g.data.datasets[i].data = s);
        g.update("none");
    }

    /* ============ 2. SOM DO ALERTA ============ */
    const btnSom = document.getElementById("btnSom");

    function bip() {
        if (!audioCtx) return;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.frequency.value = 880;
        gain.gain.value = 0.2;
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.4);
    }

    if (btnSom) {
        btnSom.addEventListener("click", function () {
            // O browser só permite som depois de um clique do utilizador
            audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
            somAtivo = !somAtivo;

            if (somAtivo) {
                btnSom.className = "btn btn-success btn-sm rounded-pill px-3 fw-medium";
                btnSom.innerHTML = '<i class="fa-solid fa-bell-slash me-1"></i>Desativar som';
                bip();
            } else {
                btnSom.className = "btn btn-outline-success btn-sm rounded-pill px-3 fw-medium";
                btnSom.innerHTML = '<i class="fa-solid fa-bell me-1"></i>Ativar som';
            }
        });
    }

    /* ============ 3. ESTADO DA LIGAÇÃO ============ */
    function mostrarEstado(ligado) {
        const el = document.getElementById("estado");
        if (!el) return;
        if (ligado) {
            el.className = "badge bg-success-subtle text-success border rounded-pill px-3 py-2";
            el.textContent = "Ligado";
        } else {
            el.className = "badge bg-danger-subtle text-danger border rounded-pill px-3 py-2";
            el.textContent = "Sem ligação";
        }
    }

    /* ============ 4. ATUALIZAÇÃO EM TEMPO REAL ============ */
    async function atualizar() {
        // Só corre nas páginas que têm o dashboard
        if (!document.getElementById("zona")) return;

        try {
            const resposta = await fetch("/api/ultimos/" + SESSAO);
            const dados = await resposta.json();
            mostrarEstado(true);
            if (!dados.length) return;

            const u = dados[dados.length - 1];
            const horas = dados.map(d => d.timestamp.slice(11));

            // Valores atuais
            document.getElementById("vTemp").textContent = u.temperatura;
            document.getElementById("vFc").textContent = u.fc;
            document.getElementById("vRmssd").textContent = u.rmssd;
            document.getElementById("vEmg").textContent = u.emg_rms;
            document.getElementById("vFadiga").textContent = u.fadiga_pct;

            // Cartão da zona (verde / amarelo / vermelho)
            const zona = document.getElementById("zona");
            zona.className = "p-4 border rounded-3 text-center h-100 d-flex flex-column justify-content-center zona-" + u.zona;
            document.getElementById("zonaNome").textContent = NOMES[u.zona] || u.zona;

            // Alerta visual e sonoro
            const alerta = document.getElementById("alerta");
            alerta.classList.toggle("d-none", !u.alerta_ativo);
            if (u.alerta_ativo && somAtivo && Date.now() - ultimoBip > 3000) {
                bip();
                ultimoBip = Date.now();
            }

            // Gráficos
            preencher(gTemp, horas, dados.map(d => d.temperatura));
            preencher(gFc, horas, dados.map(d => d.fc));
            preencher(gRmssd, horas, dados.map(d => d.rmssd));
            preencher(gEmg, horas, dados.map(d => d.emg_rms), dados.map(d => d.fadiga_pct));

        } catch (erro) {
            mostrarEstado(false);
        }
    }

    setInterval(atualizar, 1000);
    atualizar();
});