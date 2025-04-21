let questionCount = 0;
const maxQuestions = 50;

function createQuestionBlock() {
    if (questionCount >= maxQuestions) {
        alert("Вы не можете добавить более 50 вопросов.");
        return;
    }

    const questionId = questionCount++;
    const container = document.createElement("div");
    container.className = "card mb-4 shadow-sm";
    container.innerHTML = `
        <div class="card-body">
            <div class="mb-3">
                <label class="form-label">Текст вопроса</label>
                <input type="text" name="questions[${questionId}][text]" class="form-control" required>
            </div>

            <div class="mb-3">
                <label class="form-label">Тип вопроса</label>
                <select name="questions[${questionId}][type]" class="form-select question-type" data-question-id="${questionId}">
                    <option value="single">Один верный ответ</option>
                    <option value="multiple">Несколько верных ответов</option>
                    <option value="text">Вписать ответ</option>
                </select>
            </div>

            <div class="answer-options" id="answers-${questionId}">
                <!-- варианты ответов появятся тут -->
            </div>

            <div class="mb-3 text-end">
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeQuestion(this)">Удалить вопрос</button>
            </div>
        </div>
    `;
    document.getElementById("questionsContainer").appendChild(container);
    updateAnswersUI(questionId, "single");
}

function removeQuestion(button) {
    const card = button.closest(".card");
    card.remove();
    questionCount--;  // уменьшаем счётчик при удалении
}

function updateAnswersUI(questionId, type) {
    const answersDiv = document.getElementById(`answers-${questionId}`);
    answersDiv.innerHTML = "";

    if (type === "text") {
        answersDiv.innerHTML = `
            <div class="mb-3">
                <label class="form-label">Верный ответ</label>
                <input type="text" name="questions[${questionId}][text_answer]" class="form-control">
            </div>
        `;
    } else {
        for (let i = 0; i < 2; i++) addAnswerOption(questionId, type);
        const addBtn = document.createElement("button");
        addBtn.type = "button";
        addBtn.className = "btn btn-sm btn-outline-secondary";
        addBtn.innerText = "Добавить вариант ответа";
        addBtn.onclick = () => addAnswerOption(questionId, type);
        answersDiv.appendChild(addBtn);
    }
}

function addAnswerOption(questionId, type) {
    const answersDiv = document.getElementById(`answers-${questionId}`);
    const optionCount = answersDiv.querySelectorAll(".answer-row").length;
    const answerRow = document.createElement("div");
    answerRow.className = "mb-2 answer-row d-flex align-items-center gap-2";

    let inputType = type === "multiple" ? "checkbox" : "radio";
    answerRow.innerHTML = `
        <input type="${inputType}" name="questions[${questionId}][correct]${type === "multiple" ? '[]' : ''}" value="${optionCount}">
        <input type="text" name="questions[${questionId}][options][]" class="form-control" placeholder="Вариант ответа" required>
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.parentElement.remove()">✕</button>
    `;
    answersDiv.insertBefore(answerRow, answersDiv.lastElementChild);
}

document.getElementById("addQuestionBtn").addEventListener("click", createQuestionBlock);

document.addEventListener("change", function (e) {
    if (e.target.classList.contains("question-type")) {
        const questionId = e.target.getAttribute("data-question-id");
        updateAnswersUI(questionId, e.target.value);
    }
});

window.onload = createQuestionBlock;
