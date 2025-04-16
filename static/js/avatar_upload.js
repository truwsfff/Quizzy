document.getElementById("avatar-form").addEventListener("submit", async function(e) {
    e.preventDefault();  // не даём форме перезагрузить страницу

    const formData = new FormData();
    const fileInput = document.getElementById("avatar-input");
    formData.append("avatar", fileInput.files[0]);

    const response = await fetch("/upload_avatar/42", {
        method: "POST",
        body: formData
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById("avatar-preview").src = data.new_avatar_url + "?t=" + new Date().getTime(); // обновляем аватар, добавляем ?t=... чтобы избежать кеша
    } else {
        alert("Ошибка при загрузке!");
    }
});
