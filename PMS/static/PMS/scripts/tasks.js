// new task
const addTaskButton = document.querySelector("#add-task");
const addTaskForm = document.querySelector("#new-task-form");
const startDateError = document.querySelector("#startDateError");
const closeModalButton = document.querySelector("#close-modal");
const failedAddTask = new bootstrap.Toast(document.querySelector('.failed-add-task'));
const addedNewTask = new bootstrap.Toast(document.querySelector('.added-new-task'));

addTaskButton.addEventListener('click', (e) => {
    if (addTaskForm.checkValidity()) {
        e.preventDefault();
        form = new FormData(addTaskForm);
        if (form.get("start_date") > form.get("due_date")) {
            startDateError.classList.remove("d-none");
        } 
        else {
            startDateError.classList.add("d-none")
            fetch("/project/tasks/add_task", {
                method: "POST",
                body: form,
                credentials: "same-origin"
            })
            .then(response => {
                if (response.ok) {
                    closeModalButton.click();
                    addTaskForm.reset();
                    addedNewTask.show();
                }
            })
            .catch(e => {
                failedAddTask.show();
            })
        }
    }
})

// toggle task details
const allTaskRows = document.querySelectorAll('.task-table tr');
const allTaskDetails = document.querySelectorAll('.task-details-container');

function hideAllTaskDetails() {
    allTaskDetails.forEach(taskDetail => {
        taskDetail.classList.add('d-none');
    })
}

allTaskRows.forEach(
    taskRow => taskRow.addEventListener('click', () => {
        hideAllTaskDetails();
        let taskId = taskRow.dataset.taskId;
        let taskDetails = document.querySelector(`#task-${taskId}-details`);
        taskDetails.classList.remove('d-none');
}))

// toggle task completion status
const allTaskCheckCircles = document.querySelectorAll('.fa-check-circle.task-completion');
const allCompleteButtons = document.querySelectorAll('.complete-button');

function toggleTaskCompletion(e) {
    e.preventDefault();
    let form = new FormData(e.target.parentElement);
    let taskId = e.target.dataset.taskId;
    fetch("/project/tasks/toggle_task_completion", {
        method: "POST",
        body: form,
        credentials: "same-origin"
    })
    .then(response => {
        if (response.ok) {
            let checkIcon = document.querySelector(`i[data-task-id='${taskId}']`)
            if (e.target.classList.contains("btn-success")) {
                e.target.classList.remove("btn-success");
                e.target.classList.add("btn-outline-success");
                e.target.innerHTML = "Mark as completed";
                checkIcon.classList.remove("text-success");
                checkIcon.classList.add("text-muted");
            }
            else {
                e.target.classList.remove("btn-outline-success");
                e.target.classList.add("btn-success");
                e.target.innerHTML = "Completed";
                checkIcon.classList.remove("text-muted");
                checkIcon.classList.add("text-success");
            }  
        }
    })
    .catch(e => {
        console.log(e);
    })
}

allTaskCheckCircles.forEach(icon => {
    icon.addEventListener("click", (e) => {
        e.stopPropagation();
        let taskId = e.target.dataset.taskId;
        let completionButton = document.querySelector(`#task-${taskId}-details .toggle-completion-form button`);
        completionButton.click();
    })
})

allCompleteButtons.forEach(button => {
    button.addEventListener("click", toggleTaskCompletion);
})

// new subtask
let submitSubtaskButtons = document.querySelectorAll(".submit-new-subtask");

submitSubtaskButtons.forEach(button => button.addEventListener("click", addNewSubtask));

function addNewSubtask(e) {
    let subTaskFormElement = document.querySelector(`#${e.target.getAttribute("form")}`);
    let subTaskForm = new FormData(subTaskFormElement);
    let closeModalButton = e.target.parentElement.querySelector(".close-modal");
    let subtaskTable = document.querySelector(`#subtask-table-${e.target.dataset.taskId} tbody`);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    if (subTaskFormElement.checkValidity()) {
        e.preventDefault();
        fetch("/project/tasks/add_subtask", {
            method: "POST",
            body: subTaskForm,
            credentials: "same-origin"
        })
        .then(response => {
            if (response.ok) {
                closeModalButton.click();
                subTaskFormElement.reset();
                addedNewTask.show();
            }
            else {
                throw new Error('Something went wrong');
            }
            return response.text();
        })
        .then((subtaskID) => {
            subtaskTable.innerHTML += `
                    <tr>
                        <td>
                            <form action="" method="post" class="d-inline">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <input type="hidden" name="subtask_id" value="${subtaskID}">
                                <i class="
                                fa 
                                fa-2x 
                                fa-check-circle
                                subtask-completion
                                text-muted" onclick="toggleSubtaskCompletion(event)">
                                </i>
                            </form>
                        </td>
                        <td>${subTaskForm.get("subtask_title")}</td>
                        <td>${subTaskForm.get("due_date").slice(5,7)}/${subTaskForm.get("due_date").slice(8,10)}</td>
                    </tr>
                `;
        })
        .catch(e => {
            console.log(e);
            failedAddTask.show();
        })
    }
}

// toggle subtask completion status
const allSubtaskCheckCircles = document.querySelectorAll('.fa-check-circle.subtask-completion');

function toggleSubtaskCompletion(e) {
    let form = new FormData(e.target.parentElement);
    fetch("/project/tasks/toggle_subtask_completion", {
        method: "POST",
        body: form,
        credentials: "same-origin"
    })
    .then(response => {
        if (response.ok) {
            if (e.target.classList.contains("text-success")) {
                e.target.classList.remove("text-success");
                e.target.classList.add("text-muted");
            }
            else {
                e.target.classList.remove("text-muted");
                e.target.classList.add("text-success");
            }  
        }
    })
    .catch(e => {
        console.log(e);
    })
}

allSubtaskCheckCircles.forEach(icon => {
    icon.addEventListener("click", toggleSubtaskCompletion)
});

// modify send message button state on input change 
const allMessageBoxes = document.querySelectorAll(".message-box");

function modifySendMessageButtonState(e) {
    let messageBox = e.target;
    let sendMessageButton = messageBox.nextElementSibling;
    if (messageBox.value.length == 0) {
        sendMessageButton.classList.add("text-muted");
        sendMessageButton.setAttribute("role", "");
    }
    else {
        sendMessageButton.classList.remove("text-muted");
        sendMessageButton.setAttribute("role", "button");
    }
}

allMessageBoxes.forEach(messageBox => messageBox.addEventListener("input",modifySendMessageButtonState));

// send message
const allSendMessageButtons = document.querySelectorAll(".submit-new-message");

function sendTaskMessage(e) {
    let messageFormElement = e.target.parentElement;
    let form = new FormData(messageFormElement);
    if (messageFormElement.checkValidity()) {
        fetch("/project/tasks/send_message", {
            method: "POST",
            body: form,
            credentials: "same-origin"
        })
        .then(response => {
            if (response.ok) {
                messageFormElement.reset();
                e.target.classList.add("text-muted");
                e.target.setAttribute("role", "");
                let messageContainer = document.querySelector(`#message-container-${e.target.dataset.taskId}`);
                let userPictureURL = document.querySelector(".user-picture").getAttribute("src");
                const date = new Date();
                let day = date.getDate();
                let month = date.getMonth() + 1;
                if (month.toString().length == 1) {
                    month = `0${month}`;
                }
                let time = date.toJSON().slice(11, 16);

                messageContainer.innerHTML += `
                    <div class="chat-item-self d-flex justify-content-end">
                        <p class="border rounded-start p-2 mb-2">
                            <span class="text-muted message-timestamp">${month}/${day} ${time}</span>
                            <br>
                            ${form.get("message")}
                        </p>
                        <img src="${userPictureURL}" alt="" width="40px" height="40px" class="border rounded-circle ms-3">
                    </div> 
                `;
            }
        })
        .catch(e => {
            console.log(e);
        })
    }
}

allSendMessageButtons.forEach(icon => {
    icon.addEventListener("click", sendTaskMessage)
});

// open task details if get param is present
const paramString = window.location.href.split('?')[1];
const params = new URLSearchParams(paramString);
const taskId = params.get("task");
const paramTaskRow = document.querySelector(`#task-${taskId}-row`);
paramTaskRow.click();