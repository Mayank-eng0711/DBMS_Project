const $ = (id) => document.getElementById(id);

function showMessage(text, type = "success") {
    const box = $("message");
    box.textContent = text;
    box.className = `message show ${type}`;
    window.clearTimeout(showMessage.timer);
    showMessage.timer = window.setTimeout(() => box.className = "message", 5000);
}

async function api(url, options = {}) {
    let response;
    try {
        response = await fetch(url, {
            ...options,
            headers: { "Content-Type": "application/json", ...(options.headers || {}) }
        });
    } catch {
        throw new Error("Cannot reach the server. Check that Flask is running.");
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Something went wrong.");
    return data;
}

function cell(text) {
    const td = document.createElement("td");
    td.textContent = text == null ? "" : String(text);
    return td;
}
function fillTable(id, rows, columns, emptyText = "No records found.") {
    const body = $(id);
    body.replaceChildren();
    if (!rows.length) {
        const tr = document.createElement("tr");
        const td = cell(emptyText);
        td.colSpan = columns;
        td.className = "empty";
        tr.append(td);
        body.append(tr);
    }
    return body;
}
function addCell(row, value) { row.append(cell(value)); }
function actionButton(label, callback) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "small-btn";
    button.textContent = label;
    button.addEventListener("click", callback);
    return button;
}

async function loadDashboard() {
    try {
        const data = await api("/dashboard");
        $("studentCount").textContent = data.students;
        $("subjectCount").textContent = data.subjects;
        $("attendanceCount").textContent = data.attendance;
    } catch (error) { showMessage(error.message, "error"); }
}

async function loadStudents() {
    try {
        const students = await api("/students");
        const body = fillTable("studentTable", students, 7);
        const dropdown = $("attendanceStudent");
        dropdown.replaceChildren(new Option("Choose student", ""));
        students.forEach(student => {
            const row = document.createElement("tr");
            [student.student_id, student.roll_no, student.name, student.branch, student.semester, student.email || ""].forEach(v => addCell(row, v));
            const td = document.createElement("td");
            td.append(actionButton("Edit", () => {
                $("studentId").value = student.student_id;
                $("rollNo").value = student.roll_no;
                $("studentName").value = student.name;
                $("branch").value = student.branch;
                $("semester").value = student.semester;
                $("email").value = student.email || "";
                $("saveStudentBtn").textContent = "Update student";
                $("studentForm").scrollIntoView({ behavior: "smooth", block: "start" });
            }));
            row.append(td);
            body.append(row);
            dropdown.add(new Option(`${student.roll_no} — ${student.name}`, student.student_id));
        });
    } catch (error) { showMessage(error.message, "error"); }
}

$("studentForm").addEventListener("submit", async event => {
    event.preventDefault();
    const id = $("studentId").value;
    const data = {
        roll_no: $("rollNo").value.trim(),
        name: $("studentName").value.trim(),
        branch: $("branch").value.trim(),
        semester: Number($("semester").value),
        email: $("email").value.trim()
    };
    if (!data.roll_no || !data.name || !data.branch || !Number.isInteger(data.semester) || data.semester < 1 || data.semester > 12) {
        showMessage("Enter roll number, name, branch and a semester from 1 to 12.", "error"); return;
    }
    try {
        const result = await api(id ? `/students/${id}` : "/students", { method: id ? "PUT" : "POST", body: JSON.stringify(data) });
        showMessage(result.message);
        $("studentForm").reset(); $("studentId").value = ""; $("saveStudentBtn").textContent = "Add student";
        await Promise.all([loadStudents(), loadDashboard()]);
    } catch (error) { showMessage(error.message, "error"); }
});
$("clearStudentBtn").addEventListener("click", () => {
    $("studentForm").reset(); $("studentId").value = ""; $("saveStudentBtn").textContent = "Add student";
});
$("refreshStudents").addEventListener("click", loadStudents);

async function loadSubjects() {
    try {
        const subjects = await api("/subjects");
        const body = fillTable("subjectTable", subjects, 3);
        const dropdown = $("attendanceSubject");
        dropdown.replaceChildren(new Option("Choose subject", ""));
        subjects.forEach(subject => {
            const row = document.createElement("tr");
            [subject.subject_id, subject.subject_name, subject.subject_code].forEach(v => addCell(row, v));
            body.append(row);
            dropdown.add(new Option(`${subject.subject_code} — ${subject.subject_name}`, subject.subject_id));
        });
    } catch (error) { showMessage(error.message, "error"); }
}
$("subjectForm").addEventListener("submit", async event => {
    event.preventDefault();
    const data = { subject_name: $("subjectName").value.trim(), subject_code: $("subjectCode").value.trim() };
    if (!data.subject_name || !data.subject_code) { showMessage("Enter subject name and subject code.", "error"); return; }
    try {
        const result = await api("/subjects", { method: "POST", body: JSON.stringify(data) });
        showMessage(result.message); $("subjectForm").reset();
        await Promise.all([loadSubjects(), loadDashboard()]);
    } catch (error) { showMessage(error.message, "error"); }
});
$("refreshSubjects").addEventListener("click", loadSubjects);

async function loadAttendance() {
    try {
        const records = await api("/attendance");
        const body = fillTable("attendanceTable", records, 7);
        records.forEach(record => {
            const row = document.createElement("tr");
            [record.attendance_id, record.roll_no, record.name, record.subject_name, record.attendance_date, record.status].forEach(v => addCell(row, v));
            const td = document.createElement("td");
            td.append(actionButton("Edit", async () => {
                const newDate = prompt("Enter attendance date (YYYY-MM-DD):", record.attendance_date);
                if (newDate === null) return;
                const newStatus = prompt("Enter status: Present or Absent", record.status);
                if (newStatus === null) return;
                const status = newStatus.trim();
                if (!/^\d{4}-\d{2}-\d{2}$/.test(newDate) || !["Present", "Absent"].includes(status)) {
                    showMessage("Use a valid date (YYYY-MM-DD) and status Present or Absent.", "error"); return;
                }
                try {
                    const result = await api(`/attendance/${record.attendance_id}`, { method: "PUT", body: JSON.stringify({ attendance_date: newDate, status }) });
                    showMessage(result.message); await Promise.all([loadAttendance(), loadDashboard()]);
                } catch (error) { showMessage(error.message, "error"); }
            }));
            row.append(td); body.append(row);
        });
    } catch (error) { showMessage(error.message, "error"); }
}
$("attendanceForm").addEventListener("submit", async event => {
    event.preventDefault();
    const data = {
        student_id: $("attendanceStudent").value,
        subject_id: $("attendanceSubject").value,
        attendance_date: $("attendanceDate").value,
        status: $("attendanceStatus").value
    };
    if (!data.student_id || !data.subject_id || !data.attendance_date) { showMessage("Choose a student, subject and date.", "error"); return; }
    try {
        const result = await api("/attendance", { method: "POST", body: JSON.stringify(data) });
        showMessage(result.message); await Promise.all([loadAttendance(), loadDashboard()]);
    } catch (error) { showMessage(error.message, "error"); }
});
$("refreshAttendance").addEventListener("click", loadAttendance);

$("searchForm").addEventListener("submit", async event => {
    event.preventDefault();
    const rollNo = $("searchRoll").value.trim();
    if (!rollNo) { showMessage("Enter a roll number.", "error"); return; }
    try {
        const results = await api(`/search?roll_no=${encodeURIComponent(rollNo)}`);
        const body = fillTable("searchTable", results, 6);
        results.forEach(item => {
            const row = document.createElement("tr");
            [item.roll_no, item.name, item.subject_name, item.total_classes, item.present_classes, `${Number(item.attendance_percentage).toFixed(2)}%`].forEach(v => addCell(row, v));
            body.append(row);
        });
        if (!results.length) showMessage("No attendance records found for that roll number.", "error");
        else showMessage("Attendance report loaded.");
    } catch (error) { showMessage(error.message, "error"); }
});

function switchSection(id) {
    document.querySelectorAll(".section").forEach(section => section.classList.toggle("active", section.id === id));
    document.querySelectorAll(".nav-btn").forEach(button => button.classList.toggle("active", button.dataset.section === id));
    if (id === "dashboard") loadDashboard();
    if (id === "students") loadStudents();
    if (id === "subjects") loadSubjects();
    if (id === "attendance") { loadStudents(); loadSubjects(); loadAttendance(); }
}
document.querySelectorAll(".nav-btn").forEach(button => button.addEventListener("click", () => switchSection(button.dataset.section)));
$("refreshDashboard").addEventListener("click", loadDashboard);

window.addEventListener("DOMContentLoaded", async () => {
    $("attendanceDate").value = new Date().toLocaleDateString("en-CA");
    await Promise.all([loadDashboard(), loadStudents(), loadSubjects(), loadAttendance()]);
});
