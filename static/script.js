const form = document.getElementById("task-form");
const titleInput = document.getElementById("title");
const descInput = document.getElementById("description");
const listEl = document.getElementById("tasks-list");

const PRIORITY_LABEL = {
  high: "اولویت بالا",
  medium: "اولویت متوسط",
  low: "اولویت پایین",
};

async function fetchTasks() {
  const res = await fetch("/api/tasks");
  const tasks = await res.json();
  renderTasks(tasks);
}

function renderTasks(tasks) {
  listEl.innerHTML = "";

  if (tasks.length === 0) {
    listEl.innerHTML = `<div class="empty-state">هنوز کاری اضافه نکرده‌اید ✨</div>`;
    return;
  }

  tasks.forEach((task) => {
    const card = document.createElement("div");
    card.className = "task-card" + (task.done ? " done" : "");

    card.innerHTML = `
      <input type="checkbox" class="task-checkbox" ${task.done ? "checked" : ""}>
      <div class="task-body">
        <div class="task-title"></div>
        <div class="task-desc"></div>
        <span class="priority-badge priority-${task.priority}">
          ${PRIORITY_LABEL[task.priority] || task.priority}
        </span>
      </div>
      <button class="delete-btn" title="حذف">✕</button>
    `;

    card.querySelector(".task-title").textContent = task.title;
    card.querySelector(".task-desc").textContent = task.description || "";

    card.querySelector(".task-checkbox").addEventListener("change", (e) => {
      toggleDone(task.id, e.target.checked);
    });

    card.querySelector(".delete-btn").addEventListener("click", () => {
      deleteTask(task.id);
    });

    listEl.appendChild(card);
  });
}

async function toggleDone(id, done) {
  await fetch(`/api/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ done }),
  });
  fetchTasks();
}

async function deleteTask(id) {
  await fetch(`/api/tasks/${id}`, { method: "DELETE" });
  fetchTasks();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = titleInput.value.trim();
  const description = descInput.value.trim();
  if (!title) return;

  await fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description }),
  });

  titleInput.value = "";
  descInput.value = "";
  fetchTasks();
});

fetchTasks();
