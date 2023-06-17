// new resource
const addResourceButton = document.querySelector("#add-resource");
const addResourceForm = document.querySelector("#new-resource-form");
const closeModalButton = document.querySelector("#close-modal");
const failedAddResource = new bootstrap.Toast(document.querySelector('.failed-add-resource'));
const addedNewResource = new bootstrap.Toast(document.querySelector('.added-new-resource'));

addResourceButton.addEventListener('click', (e) => {
    if (addResourceForm.checkValidity()) {
        e.preventDefault();
        form = new FormData(addResourceForm);
        fetch("/project/resources/add_resource", {
            method: "POST",
            body: form,
            credentials: "same-origin"
        })
        .then(response => {
            if (response.ok) {
                closeModalButton.click();
                addResourceForm.reset();
                addedNewResource.show();
                return response.text();
            }
        })
        .then((data) => {
            console.log(data);
        })
        .catch(e => {
            failedAddResource.show();
        })
    }
});

// toggle resource details
const allResourceRows = document.querySelectorAll('.resource-table tr');
const allResourceDetails = document.querySelectorAll('.resource-details-container');

function hideAllResourceDetails() {
    allResourceDetails.forEach(resourceDetail => {
        resourceDetail.classList.add('d-none');
    })
}

allResourceRows.forEach(
    resourceRow => resourceRow.addEventListener('click', () => {
        hideAllResourceDetails();
        let resourceId = resourceRow.dataset.resourceId;
        let resourceDetails = document.querySelector(`#resource-${resourceId}-details`);
        resourceDetails.classList.remove('d-none');
}))

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

function sendResourceMessage(e) {
    let messageFormElement = e.target.parentElement;
    let form = new FormData(messageFormElement);
    if (messageFormElement.checkValidity()) {
        fetch("/project/resources/send_message", {
            method: "POST",
            body: form,
            credentials: "same-origin"
        })
        .then(response => {
            if (response.ok) {
                messageFormElement.reset();
                e.target.classList.add("text-muted");
                e.target.setAttribute("role", "");
                let messageContainer = document.querySelector(`#message-container-${e.target.dataset.resourceId}`);
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
    icon.addEventListener("click", sendResourceMessage)
});

// open resource details if get param is present
const paramString = window.location.href.split('?')[1];
const params = new URLSearchParams(paramString);
const resourceId = params.get("resource");
const paramResourceRow = document.querySelector(`#resource-${resourceId}-row`);
paramResourceRow.click();