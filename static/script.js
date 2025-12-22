// Use the same origin as the deployed backend, so it works locally and on Azure.
const API_BASE = `${window.location.origin}/api`;

const form = document.getElementById("student-form");
const idInput = document.getElementById("student-id");
const nameInput = document.getElementById("name");
const ageInput = document.getElementById("age");
const gradeInput = document.getElementById("grade");
const cancelBtn = document.getElementById("cancel-edit");
const tbody = document.getElementById("students-body");

async function fetchStudents() {
  try {
    const res = await fetch(`${API_BASE}/students`);
    const data = await res.json();
    renderTable(data);
  } catch (err) {
    console.error("Error fetching students", err);
    alert("Failed to load students. Is the API running?");
  }
}

function renderTable(students) {
  tbody.innerHTML = "";
  students.forEach((s) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${s.id}</td>
      <td>${s.name}</td>
      <td>${s.age}</td>
      <td>${s.grade}</td>
      <td class="actions">
        <button data-id="${s.id}" data-action="edit">Edit</button>
        <button data-id="${s.id}" data-action="delete" class="delete">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = idInput.value;
  const payload = {
    name: nameInput.value.trim(),
    age: Number(ageInput.value),
    grade: gradeInput.value.trim(),
  };

  if (!payload.name || !payload.age || !payload.grade) {
    alert("Please fill in all fields.");
    return;
  }

  try {
    if (id) {
      // Update
      await fetch(`${API_BASE}/students/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } else {
      // Create
      await fetch(`${API_BASE}/students`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }
    clearForm();
    fetchStudents();
  } catch (err) {
    console.error("Save error", err);
    alert("Failed to save student.");
  }
});

tbody.addEventListener("click", async (e) => {
  const target = e.target;
  if (!(target instanceof HTMLElement)) return;
  const action = target.dataset.action;
  const id = target.dataset.id;
  if (!action || !id) return;

  if (action === "edit") {
    const row = target.closest("tr");
    if (!row) return;
    const cells = row.querySelectorAll("td");
    idInput.value = id;
    nameInput.value = cells[1].textContent || "";
    ageInput.value = cells[2].textContent || "";
    gradeInput.value = cells[3].textContent || "";
  } else if (action === "delete") {
    if (!confirm("Delete this student?")) return;
    try {
      await fetch(`${API_BASE}/students/${id}`, { method: "DELETE" });
      fetchStudents();
    } catch (err) {
      console.error("Delete error", err);
      alert("Failed to delete student.");
    }
  }
});

cancelBtn.addEventListener("click", (e) => {
  e.preventDefault();
  clearForm();
});

function clearForm() {
  idInput.value = "";
  nameInput.value = "";
  ageInput.value = "";
  gradeInput.value = "";
}

// Initial load
fetchStudents();


