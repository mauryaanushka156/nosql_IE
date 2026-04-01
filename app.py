import streamlit as st
from neo4j import GraphDatabase
from config import URI, USERNAME, PASSWORD


class EmployeeSkillGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def recommend_employees_for_project(self, project_name):
        query = """
        MATCH (p:Project {name: $project_name})-[:REQUIRES]->(req:Skill)
        WITH p, collect(req) AS requiredSkills, count(req) AS totalRequired
        MATCH (e:Employee)
        OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
        WHERE s IN requiredSkills
        WITH e, totalRequired, count(s) AS matchedSkills
        RETURN e.name AS employee,
               matchedSkills,
               totalRequired,
               round((toFloat(matchedSkills) / totalRequired) * 100, 2) AS match_percentage
        ORDER BY match_percentage DESC
        """
        return self.run_query(query, {"project_name": project_name})

    def find_missing_skills_for_role(self, employee_name, role_title):
        query = """
        MATCH (r:JobRole {title: $role_title})-[:NEEDS]->(s:Skill)
        WHERE NOT EXISTS {
            MATCH (:Employee {name: $employee_name})-[:HAS_SKILL]->(s)
        }
        RETURN s.name AS missing_skill
        """
        return self.run_query(query, {
            "employee_name": employee_name,
            "role_title": role_title
        })

    def suggest_job_roles(self, employee_name):
        query = """
        MATCH (e:Employee {name: $employee_name})-[:HAS_SKILL]->(s:Skill)<-[:NEEDS]-(r:JobRole)
        RETURN r.title AS role, count(s) AS matched_skills
        ORDER BY matched_skills DESC
        """
        return self.run_query(query, {"employee_name": employee_name})

    def recommend_courses_for_role(self, employee_name, role_title):
        query = """
        MATCH (r:JobRole {title: $role_title})-[:NEEDS]->(s:Skill)
        WHERE NOT EXISTS {
            MATCH (:Employee {name: $employee_name})-[:HAS_SKILL]->(s)
        }
        MATCH (c:Course)-[:TEACHES]->(s)
        RETURN s.name AS missing_skill, c.name AS recommended_course, c.provider AS provider
        """
        return self.run_query(query, {
            "employee_name": employee_name,
            "role_title": role_title
        })


st.set_page_config(page_title="Employee Skill Graph", layout="wide")
st.title("Employee Skill & Job Recommendation System")
st.write("Built using Neo4j, Cypher, Python, and Streamlit")

graph = EmployeeSkillGraph(URI, USERNAME, PASSWORD)

menu = st.sidebar.selectbox(
    "Choose Feature",
    [
        "Recommend Employees for Project",
        "Find Missing Skills",
        "Suggest Job Roles",
        "Recommend Courses"
    ]
)

if menu == "Recommend Employees for Project":
    st.subheader("Recommend Employees for a Project")
    project_name = st.text_input("Enter project name", "Fraud Detection System")

    if st.button("Get Recommendations"):
        results = graph.recommend_employees_for_project(project_name)
        if results:
            st.table(results)
        else:
            st.warning("No results found")

elif menu == "Find Missing Skills":
    st.subheader("Find Missing Skills for a Target Role")
    employee_name = st.text_input("Enter employee name", "Anushka Maurya")
    role_title = st.text_input("Enter target role", "Data Scientist")

    if st.button("Find Missing Skills"):
        results = graph.find_missing_skills_for_role(employee_name, role_title)
        if results:
            st.table(results)
        else:
            st.success("No missing skills found")

elif menu == "Suggest Job Roles":
    st.subheader("Suggest Suitable Job Roles")
    employee_name = st.text_input("Enter employee name", "Anushka Maurya")

    if st.button("Suggest Roles"):
        results = graph.suggest_job_roles(employee_name)
        if results:
            st.table(results)
        else:
            st.warning("No role suggestions found")

elif menu == "Recommend Courses":
    st.subheader("Recommend Courses for Missing Skills")
    employee_name = st.text_input("Enter employee name", "Anushka Maurya")
    role_title = st.text_input("Enter target role", "Data Scientist")

    if st.button("Recommend Courses"):
        results = graph.recommend_courses_for_role(employee_name, role_title)
        if results:
            st.table(results)
        else:
            st.success("No course recommendations needed")

graph.close()