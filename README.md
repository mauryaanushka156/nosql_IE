# Employee Skill Graph & Job Recommendation System

This project is built using **Neo4j**, **Cypher**, **Python**, and **Streamlit**.  
It models employees, skills, projects, job roles, and courses as a graph database and uses relationships to provide intelligent recommendations.

## Features

- Recommend the best employees for a project
- Identify missing skills for a target job role
- Suggest suitable job roles for an employee
- Recommend courses for missing skills
- Display results in a simple Streamlit dashboard

## Technologies Used

- Neo4j AuraDB
- Cypher Query Language
- Python
- Streamlit

## Graph Model

### Nodes
- Employee
- Skill
- Project
- JobRole
- Course

### Relationships
- `HAS_SKILL`
- `REQUIRES`
- `NEEDS`
- `TEACHES`
- `WORKED_ON`

## Project Structure

```bash
employee_skill_graph/
│
├── config.py
├── main.py
├── app.py
├── requirements.txt
└── README.md