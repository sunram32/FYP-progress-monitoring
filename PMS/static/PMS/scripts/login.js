const supervisorLoginButton = document.querySelector('#select-supervisor-login');
const studentLoginButton = document.querySelector('#select-student-login');
const userSelection = document.querySelector('.user-selection');
const supervisorLoginForm = document.querySelector('.supervisor-login');
const studentLoginForm = document.querySelector('.student-login');
const backButton = document.querySelector('#back-button');

supervisorLoginButton.addEventListener('click', () => {
    userSelection.classList.add('d-none');
    supervisorLoginForm.classList.remove('d-none');
    backButton.classList.remove('d-none');
})

studentLoginButton.addEventListener('click', () => {
    userSelection.classList.add('d-none');
    studentLoginForm.classList.remove('d-none');
    backButton.classList.remove('d-none');
})

backButton.addEventListener('click', () => {
    userSelection.classList.remove('d-none');
    studentLoginForm.classList.add('d-none');
    supervisorLoginForm.classList.add('d-none')
    backButton.classList.add('d-none');
})