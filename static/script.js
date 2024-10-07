const jobTitles = {
    'Engineering': [
        'Software Engineer', 'Software Engineer Manager', 'Full Stack Engineer', 'Senior Software Engineer', 
        'Back end Developer', 'Front end Developer', 'Software Developer', 'Web Developer', 'Junior Software Developer', 
        'Junior Software Engineer', 'Junior Web Developer', 'Front End Developer'
    ],
    'Data & Analytics': [
        'Data Scientist', 'Data Analyst', 'Research Scientist', 'Senior Data Scientist', 'Junior Data Analyst', 
        'Director of Data Science', 'Financial Analyst'
    ],
    'Management': [
        'Product Manager', 'Operations Manager', 'Marketing Manager', 'Senior Project Engineer', 'Financial Manager', 
        'Human Resources Manager', 'Senior Human Resources Manager', 'Director of Marketing', 'Director of HR', 
        'Sales Manager', 'Senior Product Marketing Manager', 'Director of Operations', 'Research Director', 'Project Manager'
    ],
    'Marketing & Sales': [
        'Marketing Coordinator', 'Marketing Analyst', 'Sales Associate', 'Junior Sales Associate', 'Sales Representative', 
        'Sales Executive', 'Junior Sales Representative', 'Digital Marketing Manager', 'Marketing Director', 
        'Content Marketing Manager', 'Junior Marketing Manager', 'Sales Director', 'Social Media Manager', 'Digital Marketing Specialist'
    ],
    'HR & Operations Roles': [
        'Human Resources Coordinator', 'Senior HR Generalist', 'Junior HR Generalist', 'Junior HR Coordinator', 'Receptionist'
    ],
    'Creative Roles': [
        'Graphic Designer', 'Product Designer'
    ]
};

const jobTitleSelect = document.getElementById('job-title');
const jobRoleSelect = document.getElementById('job-role');
const submitButton = document.getElementById('submit');
const selectedJobDisplay = document.getElementById('selected-job');

// Event listener for job role selection
jobRoleSelect.addEventListener('change', function () {
    const selectedRole = this.value;
    jobTitleSelect.innerHTML = '<option value="" disabled selected>Select a job title</option>'; // Reset job titles

    if (selectedRole && jobTitles[selectedRole]) {
        const titles = jobTitles[selectedRole];
        titles.forEach(title => {
            const option = document.createElement('option');
            option.value = title;
            option.textContent = title;
            jobTitleSelect.appendChild(option);
        });
        jobTitleSelect.disabled = false; // Enable job title select
    } else {
        jobTitleSelect.disabled = true; // Disable job title select if no role is selected
    }
});

// Event listener for submit button
submitButton.addEventListener('click', function () {
    const selectedTitle = jobTitleSelect.value;
    const selectedRole = jobRoleSelect.value;

    if (selectedTitle && selectedRole) {
        selectedJobDisplay.textContent = `You selected: ${selectedTitle} - ${selectedRole}`;
    } else {
        selectedJobDisplay.textContent = 'Please select both a job title and a job role.';
    }
});
