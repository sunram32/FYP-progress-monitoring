// toggling sidebar for mobile view
const sidebarToggler = document.querySelector('.nav-button');
const rightArrow = sidebarToggler.querySelector('.fa-angle-right');
const leftArrow = sidebarToggler.querySelector('.fa-angle-left');
const sidebar = document.querySelector('.sidebar');
sidebarToggler.addEventListener('click', () => {
    if (sidebar.classList.contains('hidden')) {
        sidebar.classList.remove('hidden');
        leftArrow.classList.remove('d-none');
        rightArrow.classList.add('d-none');
    }
    else {
        sidebar.classList.add('hidden');
        leftArrow.classList.add('d-none');
        rightArrow.classList.remove('d-none');
    }
})

// sidebar navigation state
const homeLink = document.querySelector('#home-link');
const projectsLink = document.querySelector('#projects-link');
const notificationsLink = document.querySelector('#notifications-link');
const isHomePage = window.location.pathname.slice(1,5) == "home";
const isProjectPage = window.location.pathname.slice(1,8) == "project";
const isNotificationPage = window.location.pathname.slice(1,14) == "notifications";

if (isHomePage) homeLink.classList.add('bg-secondary');
else if (isProjectPage) projectsLink.classList.add('bg-secondary');
else if (isNotificationPage) notificationsLink.classList.add('bg-secondary');

// function to navigate to project page
function navigateToProject(project_id, task_id="") {
    window.location.href = `/project/${project_id}/tasks?task=${task_id}`;
}