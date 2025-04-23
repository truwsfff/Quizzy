document.addEventListener("DOMContentLoaded", function () {
    const avatarInput = document.getElementById("avatarInput");
    const avatarForm = document.getElementById("avatarForm");
    const avatarPreview = avatarForm.querySelector("img");

    const messageDiv = document.createElement("div");
    messageDiv.className = "mt-2 text-success";
    messageDiv.style.display = "none";
    avatarForm.appendChild(messageDiv);

    avatarInput.addEventListener("change", () => {
        if (avatarInput.files.length > 0) {
            messageDiv.textContent = "Аватарка выбрана, нажмите 'Загрузить'";
            messageDiv.style.display = "block";
        }
    });

    avatarForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(avatarForm);

        try {
            const response = await fetch(avatarForm.action, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
    const data = await response.json();
    if (data.avatar_url) {
        avatarPreview.src = data.avatar_url + "?t=" + new Date().getTime();
        messageDiv.textContent = "Аватарка успешно загружена!";
        messageDiv.style.color = "green";
        messageDiv.style.display = "block";
    } else {
        throw new Error("Формат ответа не содержит avatar_url");
    }
} else {
    const errorData = await response.json();
    const errorMessage = errorData.error || "Неизвестная ошибка";
    messageDiv.textContent = errorMessage;
    messageDiv.style.color = "red";
    messageDiv.style.display = "block";
}
        } catch (error) {
            console.error("Ошибка:", error);
            messageDiv.textContent = "Произошла ошибка.";
            messageDiv.style.color = "red";
            messageDiv.style.display = "block";
        }
    });
});

