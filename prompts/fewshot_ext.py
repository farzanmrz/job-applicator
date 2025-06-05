"""
Fewshot examples of extractor agents
"""

# Resume: Education
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

# LinkedIn: Education
fsExtLkdEdu = """
================================= EXAMPLE 1 START ==================================
Task:
"Please extract the education details from the markdown file:

Kanpur, Uttar Pradesh, India

- · Engineered a distinct Network Monitoring Tool on the robust LAMP architecture, optimizing backend performance with PHP connecting to a MySQL database hosted on an Apache web server. Strategically deployed on AWS RDS and EC2 instances, bolstering network management capabilities.
- · Crafted an engaging user experience with HTML, CSS, and JavaScript, enhancing the tool's front-end functionality for seamless navigation and data visualization.

- · Instrumental in providing critical support to IIT network administrators, the Network Monitoring Tool significantly streamlined network management tasks and operations

## Education

Drexel University College of Computing &amp; Informatics

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
