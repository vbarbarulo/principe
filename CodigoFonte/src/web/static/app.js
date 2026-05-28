$(document).ready(function () {
    // -------------------------------------------------------------
    // ★ CONFIGURAÇÕES & VARIÁVEIS GLOBAIS
    // -------------------------------------------------------------
    const API_TASKS = "/api/tasks";
    const API_HEALTH = "/api/health";
    const API_CHAT_PO = "/api/chat-po";
    const API_REORDER = "/api/tasks/reorder";
    
    let allTasks = [];
    let selectedTaskId = null;
    let poChatHistory = [];

    // -------------------------------------------------------------
    // ★ SISTEMA DE NAVEGAÇÃO ENTRE ABAS
    // -------------------------------------------------------------
    $(".nav-item").on("click", function (e) {
        e.preventDefault();
        const targetTab = $(this).data("tab");

        // Transição ativa no menu lateral
        $(".nav-item").removeClass("active");
        $(this).addClass("active");

        // Alterna exibição das abas
        $(".tab-content").removeClass("active");
        $("#" + targetTab).addClass("active");

        // Ajusta títulos do Header
        if (targetTab === "kanban-tab") {
            $("#tab-title").text("Esteira de Desenvolvimento");
            $("#tab-subtitle").text("Gerencie suas ideias de melhoria e acompanhe os pipelines dos agentes locais.");
            $("#btn-new-task").fadeIn();
            loadTasks();
        } else if (targetTab === "backlog-tab") {
            $("#tab-title").text("Gestão & Refinamento do Backlog");
            $("#tab-subtitle").text("Sequencie suas demandas prioritárias e detalhe requisitos interagindo diretamente com o Product Owner.");
            $("#btn-new-task").fadeIn();
            loadBacklogManager();
        } else {
            $("#tab-title").text("Saúde & Hábitos");
            $("#tab-subtitle").text("Últimos registros de sono, peso e bem-estar físico monitorados pelo Hórus.");
            $("#btn-new-task").fadeOut();
            loadHealthLogs();
        }
    });

    // -------------------------------------------------------------
    // ★ CONSUMO DA API E RENDERIZAÇÃO: KANBAN
    // -------------------------------------------------------------
    function loadTasks() {
        $.getJSON(API_TASKS, function (data) {
            allTasks = data;
            renderKanban();
        }).fail(function (err) {
            console.error("Erro ao carregar tarefas:", err);
        });
    }

    function renderKanban() {
        const columns = ["backlog", "refining", "developing", "testing", "blocked", "done"];
        columns.forEach(col => {
            $(`#cards-${col}`).empty();
            $(`#count-${col}`).text("0");
        });

        const counts = { backlog: 0, refining: 0, developing: 0, testing: 0, blocked: 0, done: 0 };

        allTasks.forEach(task => {
            const col = task.status || "backlog";
            counts[col]++;

            const branchLabel = task.branch_name ? `<span class="card-branch"><i class="fa-solid fa-code-branch"></i> ${task.branch_name}</span>` : "";
            
            const cardHtml = `
                <div class="kanban-card" draggable="true" data-id="${task.id}" id="card-${task.id}">
                    <span class="card-id">#${task.id.slice(-6).toUpperCase()}</span>
                    <h4 class="card-title">${task.titulo}</h4>
                    <div class="card-footer">
                        ${branchLabel}
                        <span class="card-id" style="font-size: 11px;"><i class="fa-regular fa-clock"></i> ${task.id.startsWith("task_") ? formatTaskIdDate(task.id) : "Recente"}</span>
                    </div>
                </div>
            `;

            $(`#cards-${col}`).append(cardHtml);
        });

        columns.forEach(col => {
            $(`#count-${col}`).text(counts[col]);
        });

        setupDragAndDrop();
    }

    function formatTaskIdDate(id) {
        try {
            const parts = id.split("_");
            if (parts.length >= 2) {
                const dateStr = parts[1];
                const y = dateStr.substring(0, 4);
                const m = dateStr.substring(4, 6);
                const d = dateStr.substring(6, 8);
                return `${d}/${m}/${y}`;
            }
        } catch (e) {}
        return "Ativo";
    }

    // -------------------------------------------------------------
    // ★ FLUXO DRAG AND DROP (HTML5 DRAG API)
    // -------------------------------------------------------------
    function setupDragAndDrop() {
        $(".kanban-card").on("dragstart", function (e) {
            e.originalEvent.dataTransfer.setData("text/plain", $(this).data("id"));
            $(this).css("opacity", "0.5");
        });

        $(".kanban-card").on("dragend", function () {
            $(this).css("opacity", "1");
        });

        $(".kanban-column").on("dragover", function (e) {
            e.preventDefault();
            $(this).addClass("drag-over");
        });

        $(".kanban-column").on("dragleave", function () {
            $(this).removeClass("drag-over");
        });

        $(".kanban-column").on("drop", function (e) {
            e.preventDefault();
            $(this).removeClass("drag-over");

            const taskId = e.originalEvent.dataTransfer.getData("text/plain");
            const newStatus = $(this).data("status");
            const card = $(`#card-${taskId}`);

            if (card.length && newStatus) {
                const currentStatus = card.parent().attr("id").replace("cards-", "");
                if (currentStatus !== newStatus) {
                    $(`#cards-${newStatus}`).append(card);
                    updateTaskStatus(taskId, newStatus);
                }
            }
        });
    }

    function updateTaskStatus(taskId, newStatus) {
        const updateData = { id: taskId, status: newStatus };
        $.ajax({
            url: API_TASKS,
            type: "PUT",
            contentType: "application/json",
            data: JSON.stringify(updateData),
            success: function () {
                loadTasks();
            },
            error: function (xhr, status, err) {
                console.error("Erro ao mover card no banco:", err);
                loadTasks();
            }
        });
    }

    // -------------------------------------------------------------
    // ★ GESTÃO DO BACKLOG & INTERAÇÃO COM O PRODUCT OWNER
    // -------------------------------------------------------------
    function loadBacklogManager() {
        $.getJSON(API_TASKS, function (data) {
            allTasks = data;
            renderBacklogList();
        }).fail(function (err) {
            console.error("Erro ao carregar backlog:", err);
        });
    }

    function renderBacklogList() {
        const backlogContainer = $("#backlog-items-list");
        backlogContainer.empty();

        // Filtra apenas tarefas em backlog ou refining
        const backlogTasks = allTasks.filter(t => t.status === "backlog" || t.status === "refining");

        if (backlogTasks.length === 0) {
            backlogContainer.append('<div style="text-align:center; padding: 20px; color: var(--text-muted);">Nenhuma demanda pendente no Backlog.</div>');
            return;
        }

        backlogTasks.forEach((task, idx) => {
            const isActive = selectedTaskId === task.id ? "active" : "";
            const statusBadge = task.status === "refining" 
                ? '<span style="font-size:10px; background: rgba(237, 137, 54, 0.2); color:#ed8936; padding: 2px 6px; border-radius:4px; font-weight:600;">Refining (PO)</span>' 
                : '<span style="font-size:10px; background: rgba(113, 128, 150, 0.2); color:#a0aec0; padding: 2px 6px; border-radius:4px; font-weight:600;">Backlog</span>';

            const cardHtml = `
                <div class="backlog-item-card ${isActive}" data-id="${task.id}">
                    <div class="backlog-card-header">
                        <span class="backlog-card-title">${task.titulo}</span>
                        <div class="backlog-card-actions">
                            <button class="backlog-arrow-btn btn-up" data-idx="${idx}"><i class="fa-solid fa-arrow-up"></i></button>
                            <button class="backlog-arrow-btn btn-down" data-idx="${idx}"><i class="fa-solid fa-arrow-down"></i></button>
                        </div>
                    </div>
                    <div class="backlog-card-footer">
                        ${statusBadge}
                        <button class="po-talk-btn" data-id="${task.id}"><i class="fa-solid fa-comments"></i> Refinar com PO</button>
                    </div>
                </div>
            `;
            backlogContainer.append(cardHtml);
        });

        // Configura handlers para reordenar
        $(".btn-up").on("click", function (e) {
            e.stopPropagation();
            const index = $(this).data("idx");
            if (index > 0) {
                swapBacklogItems(backlogTasks, index, index - 1);
            }
        });

        $(".btn-down").on("click", function (e) {
            e.stopPropagation();
            const index = $(this).data("idx");
            if (index < backlogTasks.length - 1) {
                swapBacklogItems(backlogTasks, index, index + 1);
            }
        });

        // Selecionar card para Refinamento
        $(".backlog-item-card").on("click", function () {
            const taskId = $(this).data("id");
            selectTaskForRefining(taskId);
        });

        $(".po-talk-btn").on("click", function (e) {
            e.stopPropagation();
            const taskId = $(this).data("id");
            selectTaskForRefining(taskId);
        });
    }

    function swapBacklogItems(tasksList, indexA, indexB) {
        // Troca posições
        const temp = tasksList[indexA];
        tasksList[indexA] = tasksList[indexB];
        tasksList[indexB] = temp;

        // Mapeia todos os IDs na nova sequência
        const orderedIds = tasksList.map(t => t.id);

        $.ajax({
            url: API_REORDER,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ ids: orderedIds }),
            success: function () {
                loadBacklogManager();
            },
            error: function (xhr, status, err) {
                console.error("Erro ao ordenar backlog:", err);
            }
        });
    }

    function selectTaskForRefining(taskId) {
        selectedTaskId = taskId;
        const task = allTasks.find(t => t.id === taskId);
        
        if (!task) return;

        // Atualiza a seleção visual
        $(".backlog-item-card").removeClass("active");
        $(`.backlog-item-card[data-id="${taskId}"]`).addClass("active");

        // Altera visualização do painel direito
        $("#no-task-selected-msg").hide();
        $("#active-refine-container").fadeIn();

        // Dados do cabeçalho
        $("#refine-task-id").text(`#${task.id.slice(-8).toUpperCase()}`);
        $("#refine-task-title").text(task.titulo);
        $("#refine-task-desc").text(task.descricao_original);

        // Inicializa o Chat do PO
        poChatHistory = [];
        $("#po-chat-messages").empty();
        
        appendChatBubble("po", `Olá! Sou o seu **Product Owner**. Recebi sua demanda: *"${task.titulo}"*.\n\nVamos refinar os requisitos e detalhar os critérios de aceitação para que fique 100% pronta para o time de desenvolvimento. O que você gostaria de detalhar ou mudar nela?`);

        // Renderiza requisitos refinados se existirem
        renderRefinedSpecs(task.requisitos_refinados || "*Nenhum requisito detalhado ainda pelo PO. Envie uma mensagem para iniciarmos o refinamento!*");
    }

    function renderRefinedSpecs(markdownText) {
        const target = $("#po-refined-specs-content");
        if (!markdownText) {
            target.html("<p><i>Ainda sem especificações.</i></p>");
            return;
        }

        // Conversor Markdown ultra simples e responsivo
        let html = markdownText
            .replace(/\r\n/g, "\n")
            .replace(/\n\n/g, "</p><p>")
            .replace(/\n- \[( |x)\] (.*)/g, function (match, checked, content) {
                const isChecked = checked.trim() === 'x' ? 'checked disabled' : 'disabled';
                return `<div class="spec-checkbox"><input type="checkbox" ${isChecked}> <span>${content}</span></div>`;
            })
            .replace(/\n- (.*)/g, "<li>$1</li>")
            .replace(/\n\* (.*)/g, "<li>$1</li>")
            .replace(/### (.*)/g, "<h3>$1</h3>")
            .replace(/## (.*)/g, "<h2>$1</h2>")
            .replace(/# (.*)/g, "<h1>$1</h1>")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>");

        // Adiciona tags de lista se houver itens isolados
        if (html.includes("<li>") && !html.includes("<ul>")) {
            html = html.replace(/<li>(.*?)<\/li>/g, "<ul><li>$1</li></ul>");
        }

        target.html("<p>" + html + "</p>");
    }

    function appendChatBubble(sender, text) {
        const messagesContainer = $("#po-chat-messages");
        
        // Conversor básico de quebra de linha para exibir no chat
        const cleanText = text.replace(/\n/g, "<br>");

        const bubbleHtml = `
            <div class="chat-bubble ${sender}">
                ${cleanText}
            </div>
        `;
        messagesContainer.append(bubbleHtml);
        
        // Scroll automático para o final do chat
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
    }

    // -------------------------------------------------------------
    // ★ ENVIO DE MENSAGENS CHAT PO
    // -------------------------------------------------------------
    $("#btn-po-send").on("click", function () {
        sendPoChatMessage();
    });

    $("#po-chat-input").on("keypress", function (e) {
        if (e.which === 13) {
            sendPoChatMessage();
        }
    });

    function sendPoChatMessage() {
        const input = $("#po-chat-input");
        const msgText = input.val().trim();
        
        if (!msgText || !selectedTaskId) return;

        // Exibe mensagem do usuário no chat
        appendChatBubble("user", msgText);
        input.val("");

        // Adiciona indicador de digitação do PO
        const messagesContainer = $("#po-chat-messages");
        const typingIndicator = $('<div class="chat-bubble po typing-indicator" id="po-typing"><i>O PO está analisando e refinando...</i></div>');
        messagesContainer.append(typingIndicator);
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);

        // Dispara requisição de refinamento
        const chatData = {
            id: selectedTaskId,
            message: msgText,
            history: poChatHistory
        };

        // Salva histórico local
        poChatHistory.push({ role: "user", content: msgText });

        $.ajax({
            url: API_CHAT_PO,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(chatData),
            success: function (res) {
                $("#po-typing").remove();
                
                // Exibe resposta
                appendChatBubble("po", res.reply);
                poChatHistory.push({ role: "assistant", content: res.reply });

                // Atualiza tela de especificações
                if (res.refined_requirements) {
                    renderRefinedSpecs(res.refined_requirements);
                }

                // Se avançou, exibe aviso e recarrega
                if (res.ready_to_advance) {
                    appendChatBubble("system", "🎉 Excelente! O Product Owner aprovou o refinamento técnico! O card foi promovido automaticamente para 'Developing' (Desenvolvimento).");
                    setTimeout(() => {
                        selectedTaskId = null;
                        loadBacklogManager();
                    }, 4000);
                }
            },
            error: function (xhr, status, err) {
                $("#po-typing").remove();
                appendChatBubble("system", "❌ Erro ao se conectar com a IA do Product Owner: " + err);
            }
        });
    }

    // Botão de Forçar Avanço
    $("#btn-force-advance").on("click", function () {
        if (!selectedTaskId) return;
        
        if (confirm("Você tem certeza de que deseja forçar o avanço deste card diretamente para a fase de Desenvolvimento (Developing)?")) {
            $.ajax({
                url: API_TASKS,
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify({ id: selectedTaskId, status: "developing" }),
                success: function () {
                    selectedTaskId = null;
                    $("#no-task-selected-msg").show();
                    $("#active-refine-container").hide();
                    loadBacklogManager();
                },
                error: function (xhr, status, err) {
                    alert("Erro ao avançar card: " + err);
                }
            });
        }
    });

    // -------------------------------------------------------------
    // ★ INTERAÇÕES DE DETALHES E EDIÇÃO DE CARDS (MODAL)
    // -------------------------------------------------------------
    $(document).on("click", ".kanban-card", function () {
        const taskId = $(this).data("id");
        const task = allTasks.find(t => t.id === taskId);

        if (task) {
            $("#modal-title-text").text("Detalhes da Demanda");
            $("#form-task-id").val(task.id);
            $("#form-title").val(task.titulo);
            $("#form-desc").val(task.descricao_original);
            $("#form-status").val(task.status);
            $("#form-branch").val(task.branch_name || "");

            if (task.requisitos_refinados) {
                $("#modal-refined-reqs").text(task.requisitos_refinados);
                $("#reqs-view-container").fadeIn();
            } else {
                $("#reqs-view-container").hide();
            }

            if (task.relatorio_qa) {
                $("#modal-qa-report").text(task.relatorio_qa);
                $("#qa-report-container").fadeIn();
            } else {
                $("#qa-report-container").hide();
            }

            $("#btn-delete-task").show();
            openModal();
        }
    });

    // -------------------------------------------------------------
    // ★ CRIAÇÃO DE NOVAS TAREFAS
    // -------------------------------------------------------------
    $("#btn-new-task").on("click", function () {
        $("#modal-title-text").text("Nova Demanda de Código");
        $("#form-task-id").val("");
        $("#task-form")[0].reset();
        $("#form-status").val("backlog");
        $("#form-branch").val("");
        
        $("#reqs-view-container").hide();
        $("#qa-report-container").hide();
        $("#btn-delete-task").hide();
        openModal();
    });

    // -------------------------------------------------------------
    // ★ OPERAÇÕES DO MODAL (SAVE / DELETE / CLOSE)
    // -------------------------------------------------------------
    function openModal() {
        $("#task-modal").addClass("active");
    }

    function closeModal() {
        $("#task-modal").removeClass("active");
    }

    $("#btn-close-modal, #btn-cancel-modal, .modal-overlay").on("click", function (e) {
        if (e.target === this || $(this).attr("id") === "btn-close-modal" || $(this).attr("id") === "btn-cancel-modal") {
            closeModal();
        }
    });

    $(".modal-card").on("click", function (e) {
        e.stopPropagation();
    });

    $("#btn-save-task").on("click", function (e) {
        e.preventDefault();
        
        const taskId = $("#form-task-id").val();
        const title = $("#form-title").val().trim();
        const desc = $("#form-desc").val().trim();
        const status = $("#form-status").val();
        const branch = $("#form-branch").val().trim();

        if (!title || !desc) {
            alert("Título e Descrição são obrigatórios!");
            return;
        }

        const taskData = {
            titulo: title,
            descricao_original: desc,
            status: status,
            branch_name: branch
        };

        if (taskId) {
            taskData.id = taskId;
            $.ajax({
                url: API_TASKS,
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(taskData),
                success: function () {
                    closeModal();
                    if ($("#backlog-tab").hasClass("active")) {
                        loadBacklogManager();
                    } else {
                        loadTasks();
                    }
                },
                error: function (xhr, status, err) {
                    alert("Erro ao salvar alterações: " + err);
                }
            });
        } else {
            $.ajax({
                url: API_TASKS,
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify(taskData),
                success: function () {
                    closeModal();
                    if ($("#backlog-tab").hasClass("active")) {
                        loadBacklogManager();
                    } else {
                        loadTasks();
                    }
                },
                error: function (xhr, status, err) {
                    alert("Erro ao criar demanda: " + err);
                }
            });
        }
    });

    $("#btn-delete-task").on("click", function () {
        const taskId = $("#form-task-id").val();
        if (!taskId) return;

        if (confirm("Você tem certeza que deseja excluir esta demanda definitivamente?")) {
            $.ajax({
                url: `${API_TASKS}?id=${taskId}`,
                type: "DELETE",
                success: function () {
                    closeModal();
                    if ($("#backlog-tab").hasClass("active")) {
                        loadBacklogManager();
                    } else {
                        loadTasks();
                    }
                },
                error: function (xhr, status, err) {
                    alert("Erro ao excluir demanda: " + err);
                }
            });
        }
    });

    // -------------------------------------------------------------
    // ★ CONSUMO DA API E RENDERIZAÇÃO: HISTÓRICO DE SAÚDE
    // -------------------------------------------------------------
    function loadHealthLogs() {
        $.getJSON(API_HEALTH, function (data) {
            renderHealthTable(data);
        }).fail(function (err) {
            console.error("Erro ao carregar histórico de saúde:", err);
        });
    }

    function renderHealthTable(logs) {
        const tbody = $("#health-table-body");
        tbody.empty();

        if (!logs.length) {
            tbody.append(`<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Nenhum check-in matinal realizado ainda.</td></tr>`);
            return;
        }

        logs.forEach(log => {
            const stars = Array(log.nota_sono || 0).fill('<i class="fa-solid fa-star"></i>').join("");
            const dataFmt = log.data.split("-").reverse().join("/");
            
            const tr = `
                <tr>
                    <td><strong>${dataFmt}</strong></td>
                    <td class="health-sono-cell"><i class="fa-solid fa-moon" style="color: var(--color-primary); margin-right: 8px;"></i> ${log.hora_dormiu || "--:--"} às ${log.hora_acordou || "--:--"}</td>
                    <td>
                        <div class="health-rating">
                            ${stars} <span style="font-size: 12px; font-weight:600; margin-left: 4px;">(${log.nota_sono || 0}/5)</span>
                        </div>
                    </td>
                    <td><i class="fa-solid fa-weight-scale" style="color: var(--color-accent); margin-right: 8px;"></i> ${log.peso ? log.peso + " kg" : "---"}</td>
                    <td>${log.relato_sono || "Sem relatos cadastrados"}</td>
                </tr>
            `;
            tbody.append(tr);
        });
    }

    // Inicialização
    loadTasks();
});
