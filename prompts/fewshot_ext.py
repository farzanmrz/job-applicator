####################### 1. Resume #######################

# 1a. Edu
fsExtResEdu = """
================================= EXAMPLE 1 START ==================================
Task:
"Please extract the education details from the markdown file:

farzan.mirza@drexel.edu · Philadelphia, PA 19104 · 215-498-6165 linkedin.com/in/farzan-mirza13 · github.com/Farzanmrz

## Farzan Mirza

## EDUCATION

## Drexel University, Philadelphia, PA

June 2025 (Expected) Current GPA: 4.0

Master of Science in Artificial Intelligence and Machine Learning

## Virginia Tech, Blacksburg, VA

May 2022

Bachelor of Science in Computational Modelling and Data Analytics, (Minor: CS and Mathematics)

## TECHNICAL SKILLS

• Programming Languages: Python, R, MATLAB, SQL, Java, C
• Databases and Cloud Platforms: MySQL, AWS EC2, RDS, S3, Route 53
• Machine Learning: TensorFlow, PyTorch, Numpy,
"
Output:
```json
{
  "education": [
    {
      "ed_lvl": "Postgraduate",
      "ed_org": "Drexel University",
      "ed_degree": "Master of Science",
      "ed_startdate": null,
      "ed_enddate": "06/25",
      "ed_status": "Ongoing",
      "ed_majors": [
        "Artificial Intelligence and Machine Learning"
      ],
      "ed_minors": [],
      "ed_location": "Philadelphia, PA",
      "ed_gpa": 4.0
    },
    {
      "ed_lvl": "Undergraduate",
      "ed_org": "Virginia Tech",
      "ed_degree": "Bachelor of Science",
      "ed_startdate": null,
      "ed_enddate": "05/22",
      "ed_status": "Complete",
      "ed_majors": [
        "Computational Modelling and Data Analytics"
      ],
      "ed_minors": [
        "Computer Science",
        "Mathematics"
      ],
      "ed_location": "Blacksburg, VA",
      "ed_gpa": null
    }
  ]
}
```
================================= EXAMPLE 1 END ==================================
"""

# 1b. Exp
fsExtResExp = """
================================= EXAMPLE 1 START ==================================
Task:
"
## WORKEXPERIENCE

## Optium Data Solutions LLP - Lead System Architect,

## New Delhi, India: June 2022 - August 2023

- · Implemented a cross-platform ERP system, by leading a team of 10+ developers to streamline modules across procurement, manufacturing, HR, accounting, and sales.
- · Integrated Laravel backend with Angular web and Android frontends in AGILE manner, leveraging a MySQL stack and AWS services (EC2, RDS, S3) with GitLab CI/CD pipelines for a dynamic deployment system.
- · Conducted daily client check-ins to align team deliverables with their expectations and adapt system functionalities accordingly, effectively bridging the client-team gap and elevating client satisfaction

"
Output:
```json
{
  "experience": [
    {
      "exp_org": "Optium Data Solutions LLP",
      "exp_role": "Lead System Architect",
      "exp_startdate": "06/22",
      "exp_enddate": "08/23",
      "exp_location": "New Delhi, India",
      "exp_modality": "In-Person",
      "exp_type": "Full-time",
      "exp_desc": [
        "Implemented a cross-platform ERP system, by leading a team of 10+ developers to streamline modules across procurement, manufacturing, HR, accounting, and sales.",
        "Integrated Laravel backend with Angular web and Android frontends in AGILE manner, leveraging a MySQL stack and AWS services (EC2, RDS, S3) with GitLab CI/CD pipelines for a dynamic deployment system.",
        "Conducted daily client check-ins to align team deliverables with their expectations and adapt system functionalities accordingly, effectively bridging the client-team gap and elevating client satisfaction."
      ],
      "exp_skills_soft": [
        "Team Leadership",
        "Client Communication",
        "Agile Methodology"
      ],
      "exp_skills_hard": [
        "ERP System Implementation",
        "System Integration"
      ],
      "exp_skills_tech": [
        "Laravel",
        "Angular",
        "Android",
        "MySQL",
        "AWS EC2",
        "AWS RDS",
        "AWS S3",
        "GitLab CI/CD"
      ],
      "exp_action_words": [
        "Implemented",
        "Leading",
        "Integrated",
        "Leveraging",
        "Conducted",
        "Align",
        "Adapt",
        "Bridging",
        "Elevating"
      ]
    }
  ]
}
```
================================= EXAMPLE 1 END ==================================
"""

####################### 2. Linkedin #######################

# 2a. Edu
fsExtLkdEdu = """
================================= EXAMPLE 1 START ==================================
Task:
"Please extract the education details from the markdown file:

Kanpur, Uttar Pradesh, India

- · Engineered a distinct Network Monitoring Tool on the robust LAMP architecture, optimizing backend performance with PHP connecting to a MySQL database hosted on an Apache web server. Strategically deployed on AWS RDS and EC2 instances, bolstering network management capabilities.
- · Crafted an engaging user experience with HTML, CSS, and JavaScript, enhancing the tool's front-end functionality for seamless navigation and data visualization.

- · Instrumental in providing critical support to IIT network administrators, the Network Monitoring Tool significantly streamlined network management tasks and operations

## Education

Drexel University College of Computing & Informatics

Master's degree, Artificial Intelligence and Machine Learning · (September 2023 - May 2025)

Virginia Tech College of Science

Bachelors in Computational Modelling and Data Analytics , Data

Science · (August 2018 - May 2022)

## UWC South East Asia

IB Diploma, Computer Science · (August 2015 - May 2018)
"
Output:
```json
{
  "education": [
    {
      "ed_lvl": "Postgraduate",
      "ed_org": "Drexel University, College of Computing and Informatics",
      "ed_degree": "Masters",
      "ed_startdate": 09/23,
      "ed_enddate": "05/25",
      "ed_status": "Ongoing",
      "ed_majors": [
        "Artificial Intelligence and Machine Learning"
      ],
      "ed_minors": [],
      "ed_location": "Philadelphia, PA",
      "ed_gpa": 4.0
    },
    {
      "ed_lvl": "Undergraduate",
      "ed_org": "Virginia Tech, College of Science",
      "ed_degree": "Bachelor of Science",
      "ed_startdate": 08/18,
      "ed_enddate": "05/22",
      "ed_status": "Complete",
      "ed_majors": [
        "Computational Modelling and Data Analytics"
      ],
      "ed_minors": [
        "Computer Science",
        "Mathematics"
      ],
      "ed_location": "Blacksburg, VA",
      "ed_gpa": null
    },
    {
      "ed_lvl": "Highschool",
      "ed_org": "UWC South East Asia",
      "ed_degree": "Bachelor of Science",
      "ed_startdate": 08/15,
      "ed_enddate": "05/18",
      "ed_status": "Complete",
      "ed_majors": ["IB Diploma"],
      "ed_minors": [],
      "ed_location": "South East Asia",
      "ed_gpa": null
    }
  ]
}
```
================================= EXAMPLE 1 END ==================================
"""

# 2b. Exp
fsExtLkdExp = """
================================= EXAMPLE 1 START ==================================
Task:
"On the entrepreneurial front, I pioneered a startup that crafts a unique AI-driven Enterprise Resource Planning system. Beyond just code, this tool is a beacon for businesses aiming to harness the potential of data-driven decision-making.

Armed with a BS in Computational Modeling and Data Analytics from Virginia Tech, I've complemented hands-on experiences with robust academic grounding. As the AI landscape evolves, I commit to harness its vast potential for the greater good.

If you share this passion or have a perspective on AI's future, let's connect and build on those ideas together.

## Experience

Optium Data Solutions LLP CEO & Founder June 2022 - August 2023 (1 year 3 months)

New Delhi, Delhi, India

- · Championed the creation and rollout of an ERP for web and Android, optimizing modules across procurement, manufacturing, HR, and sales.

- · Seamlessly blended Angular for front-end development with PHP's Laravel for robust API connectivity.

Architected a dynamic RDBMS through MySQL, bolstered by an enhanced AWS cloud infrastructure harnessing AWS EC2, RDS, and efficient storage via S3.

- · Seamlessly integrated the AGILE methodology with CI/CD pipelines on GitLab, utilizing both npm and Docker to ensure swift and dependable software deployments for Angular and Laravel platforms, respectively.
- · Infused advanced decision-support mechanics into the software by integrating RandomForest and DecisionTree algorithms.
- · Oversaw organizational facets ranging from recruitment to logistics, fostering cohesion among a team of 10+ developers adept in Angular, Laravel, and Java.
- · Acted as the crucial liaison between our esteemed clients and the dedicated development team, ensuring the alignment of visions and surpassing expectations.

Martian Subsurface Analysis Team Treasurer & Programming Team Member January 2019 - May 2021 (2 years 5 months) Blacksburg, Virginia, United States

- · Collaborated with a cross-disciplinary team of 40+ engineers to design an autonomous robot for NASA's Moon to Mars Ice Challenge.
- · Employed Machine Learning techniques in Python to enable autonomous robot functions through real-time sensor data processing.
- · Led fundraising efforts to secure resources for a functional robot prototype for NASA's Langley Space Research Center competition.

Postdoctoral Scientist Dr. Aamir Abbasi Research Intern

October 2020 - December 2020 (3 months)

- · Spearheaded the development of a highly optimized Python-based linear regression model aimed at illuminating the relationship between average neuronal firing rates and the average Fourier power of Local Field Potentials (LFPs) within specific frequency bands.
- · Employed Numpy and Pandas for comprehensive data preprocessing, coupled with the transparency of Matplotlib and Seaborn for insightful data visualization.
- · Masterminded the model's optimization through Scipy's stepwise regression techniques, ultimately attaining a remarkable accuracy rate exceeding 90%

## Indian Institute of Technology, Roorkee

AIML Research Intern

August 2020 - September 2020 (2 months)

- · Conducted a rigorous time series analysis in Python to forecast fluctuations in COVID-19 cases within Uttarakhand.
- · Employed Pandas and Numpy extensively for the preprocessing and storing of sequential data, encompassing daily reported cases, patient vitals, and symptoms.
- · Trained recurrent neural networks, leveraging simple RNN and LSTM models with TensorFlow. This choice was driven by the task's inherent temporal dependencies and LSTM's ability to address the vanishing gradient problem, ultimately resulting in accurate predictions of daily case changes, achieving an impressive 82% accuracy rate.

## Ogmat

Founder

May 2017 - June 2018 (1 year 2 months)

Kanpur

- · Created a web platform connecting underprivileged students to online teachers, providing affordable study materials and support. Grew to 200+ users, 30+ teachers, and 270+ students.
- · Developed technical infrastructure with MySQL, PHP APIs, and HTML/CSS/ JavaScript for an intuitive interface.
- · Implemented AWS deployment, utilizing EC2 and RDS instances while optimizing file management through the S3 bucket, bolstering network management capabilities.
- · Secured partnerships with schools, enabling the platform to support underprivileged students.

Indian Institute of Technology, Kanpur Programmer & Summer Intern May 2017 - July 2017 (3 months)

Kanpur, Uttar Pradesh, India

- · Engineered a distinct Network Monitoring Tool on the robust LAMP architecture, optimizing backend performance with PHP connecting to a MySQL database hosted on an Apache web server. Strategically deployed on AWS RDS and EC2 instances, bolstering network management capabilities.
- · Crafted an engaging user experience with HTML, CSS, and JavaScript, enhancing the tool's front-end functionality for seamless navigation and data visualization.

- · Instrumental in providing critical support to IIT network administrators, the Network Monitoring Tool significantly streamlined network management tasks and operations

## Education

Drexel University College of Computing & Informatics
"
Output:
```json
{
  "experience": [
    {
      "exp_org": "Optium Data Solutions LLP",
      "exp_role": "CEO & Founder",
      "exp_startdate": "06/22",
      "exp_enddate": "08/23",
      "exp_location": "New Delhi, Delhi, India",
      "exp_modality": "In-Person",
      "exp_type": "Full-time",
      "exp_desc": [
        "Championed the creation and rollout of an ERP for web and Android, optimizing modules across procurement, manufacturing, HR, and sales.",
        "Seamlessly blended Angular for front-end development with PHP's Laravel for robust API connectivity.",
        "Architected a dynamic RDBMS through MySQL, bolstered by an enhanced AWS cloud infrastructure harnessing AWS EC2, RDS, and efficient storage via S3.",
        "Seamlessly integrated the AGILE methodology with CI/CD pipelines on GitLab, utilizing both npm and Docker to ensure swift and dependable software deployments for Angular and Laravel platforms, respectively.",
        "Infused advanced decision-support mechanics into the software by integrating RandomForest and DecisionTree algorithms.",
        "Oversaw organizational facets ranging from recruitment to logistics, fostering cohesion among a team of 10+ developers adept in Angular, Laravel, and Java.",
        "Acted as the crucial liaison between our esteemed clients and the dedicated development team, ensuring the alignment of visions and surpassing expectations."
      ],
      "exp_skills_soft": [
        "Agile Methodology",
        "Client Communication",
        "Team Leadership",
        "Recruitment",
        "Logistics"
      ],
      "exp_skills_hard": [
        "ERP System Implementation",
        "System Integration",
        "Decision Support"
      ],
      "exp_skills_tech": [
        "Angular",
        "PHP",
        "Laravel",
        "MySQL",
        "AWS EC2",
        "AWS RDS",
        "AWS S3",
        "GitLab",
        "npm",
        "Docker",
        "RandomForest",
        "DecisionTree",
        "Java"
      ],
      "exp_action_words": [
        "Championed",
        "Blended",
        "Architected",
        "Integrated",
        "Infused",
        "Oversaw",
        "Acted"
      ]
    },
    {
      "exp_org": "Martian Subsurface Analysis Team",
      "exp_role": "Treasurer & Programming Team Member",
      "exp_startdate": "01/19",
      "exp_enddate": "05/21",
      "exp_location": "Blacksburg, Virginia, United States",
      "exp_modality": "In-Person",
      "exp_type": "Full-time",
      "exp_desc": [
        "Collaborated with a cross-disciplinary team of 40+ engineers to design an autonomous robot for NASA's Moon to Mars Ice Challenge.",
        "Employed Machine Learning techniques in Python to enable autonomous robot functions through real-time sensor data processing.",
        "Led fundraising efforts to secure resources for a functional robot prototype for NASA's Langley Space Research Center competition."
      ],
      "exp_skills_soft": [
        "Collaboration",
        "Fundraising"
      ],
      "exp_skills_hard": [
        "Autonomous Robot Design",
        "Sensor Data Processing"
      ],
      "exp_skills_tech": [
        "Python",
        "Machine Learning"
      ],
      "exp_action_words": [
        "Collaborated",
        "Employed",
        "Led"
      ]
    },
    {
      "exp_org": "Dr. Aamir Abbasi Research",
      "exp_role": "Postdoctoral Scientist Intern",
      "exp_startdate": "10/20",
      "exp_enddate": "12/20",
      "exp_location": null,
      "exp_modality": "In-Person",
      "exp_type": "Research",
      "exp_desc": [
        "Spearheaded the development of a highly optimized Python-based linear regression model aimed at illuminating the relationship between average neuronal firing rates and the average Fourier power of Local Field Potentials (LFPs) within specific frequency bands.",
        "Employed Numpy and Pandas for comprehensive data preprocessing, coupled with the transparency of Matplotlib and Seaborn for insightful data visualization.",
        "Masterminded the model's optimization through Scipy's stepwise regression techniques, ultimately attaining a remarkable accuracy rate exceeding 90%"
      ],
      "exp_skills_soft": [],
      "exp_skills_hard": [
        "Linear Regression",
        "Data Preprocessing",
        "Data Visualization",
        "Model Optimization"
      ],
      "exp_skills_tech": [
        "Python",
        "Numpy",
        "Pandas",
        "Matplotlib",
        "Seaborn",
        "Scipy"
      ],
      "exp_action_words": [
        "Spearheaded",
        "Employed",
        "Masterminded"
      ]
    },
    {
      "exp_org": "Indian Institute of Technology, Roorkee",
      "exp_role": "AIML Research Intern",
      "exp_startdate": "08/20",
      "exp_enddate": "09/20",
      "exp_location": null,
      "exp_modality": "In-Person",
      "exp_type": "Intern",
      "exp_desc": [
        "Conducted a rigorous time series analysis in Python to forecast fluctuations in COVID-19 cases within Uttarakhand.",
        "Employed Pandas and Numpy extensively for the preprocessing and storing of sequential data, encompassing daily reported cases, patient vitals, and symptoms.",
        "Trained recurrent neural networks, leveraging simple RNN and LSTM models with TensorFlow. This choice was driven by the task's inherent temporal dependencies and LSTM's ability to address the vanishing gradient problem, ultimately resulting in accurate predictions of daily case changes, achieving an impressive 82% accuracy rate."
      ],
      "exp_skills_soft": [],
      "exp_skills_hard": [
        "Time Series Analysis",
        "Data Preprocessing"
      ],
      "exp_skills_tech": [
        "Python",
        "Pandas",
        "Numpy",
        "RNN",
        "LSTM",
        "TensorFlow"
      ],
      "exp_action_words": [
        "Conducted",
        "Employed",
        "Trained"
      ]
    },
    {
      "exp_org": "Ogmat",
      "exp_role": "Founder",
      "exp_startdate": "05/17",
      "exp_enddate": "06/18",
      "exp_location": "Kanpur",
      "exp_modality": "In-Person",
      "exp_type": "Full-time",
      "exp_desc": [
        "Created a web platform connecting underprivileged students to online teachers, providing affordable study materials and support. Grew to 200+ users, 30+ teachers, and 270+ students.",
        "Developed technical infrastructure with MySQL, PHP APIs, and HTML/CSS/ JavaScript for an intuitive interface.",
        "Implemented AWS deployment, utilizing EC2 and RDS instances while optimizing file management through the S3 bucket, bolstering network management capabilities.",
        "Secured partnerships with schools, enabling the platform to support underprivileged students."
      ],
      "exp_skills_soft": [
        "Partnership"
      ],
      "exp_skills_hard": [
        "Web Platform Development",
        "Technical Infrastructure",
        "AWS Deployment"
      ],
      "exp_skills_tech": [
        "MySQL",
        "PHP",
        "HTML",
        "CSS",
        "JavaScript",
        "AWS EC2",
        "AWS RDS",
        "AWS S3"
      ],
      "exp_action_words": [
        "Created",
        "Developed",
        "Implemented",
        "Secured"
      ]
    },
    {
      "exp_org": "Indian Institute of Technology, Kanpur",
      "exp_role": "Programmer & Summer Intern",
      "exp_startdate": "05/17",
      "exp_enddate": "07/17",
      "exp_location": "Kanpur, Uttar Pradesh, India",
      "exp_modality": "In-Person",
      "exp_type": "Intern",
      "exp_desc": [
        "Engineered a distinct Network Monitoring Tool on the robust LAMP architecture, optimizing backend performance with PHP connecting to a MySQL database hosted on an Apache web server. Strategically deployed on AWS RDS and EC2 instances, bolstering network management capabilities.",
        "Crafted an engaging user experience with HTML, CSS, and JavaScript, enhancing the tool's front-end functionality for seamless navigation and data visualization.",
        "Instrumental in providing critical support to IIT network administrators, the Network Monitoring Tool significantly streamlined network management tasks and operations"
      ],
      "exp_skills_soft": [
        "Critical Support"
      ],
      "exp_skills_hard": [
        "Network Monitoring",
        "Backend Performance Optimization",
        "User Experience"
      ],
      "exp_skills_tech": [
        "LAMP",
        "PHP",
        "MySQL",
        "Apache",
        "AWS RDS",
        "AWS EC2",
        "HTML",
        "CSS",
        "JavaScript"
      ],
      "exp_action_words": [
        "Engineered",
        "Crafted",
        "Instrumental"
      ]
    }
  ]
}
```
================================= EXAMPLE 1 END ==================================
"""
