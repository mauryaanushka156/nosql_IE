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


def print_results(title, results):
    print(f"\n--- {title} ---")
    if not results:
        print("No results found")
        return

    for row in results:
        print(row)


graph = EmployeeSkillGraph(URI, USERNAME, PASSWORD)

while True:
    print("\n1. Recommend employees for project")
    print("2. Find missing skills for role")
    print("3. Suggest job roles")
    print("4. Recommend courses")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        project_name = input("Enter project name: ")
        results = graph.recommend_employees_for_project(project_name)
        print_results("Recommended Employees", results)

    elif choice == "2":
        employee_name = input("Enter employee name: ")
        role_title = input("Enter target role: ")
        results = graph.find_missing_skills_for_role(employee_name, role_title)
        print_results("Missing Skills", results)

    elif choice == "3":
        employee_name = input("Enter employee name: ")
        results = graph.suggest_job_roles(employee_name)
        print_results("Suggested Job Roles", results)

    elif choice == "4":
        employee_name = input("Enter employee name: ")
        role_title = input("Enter target role: ")
        results = graph.recommend_courses_for_role(employee_name, role_title)
        print_results("Recommended Courses", results)

    elif choice == "5":
        print("Exiting...")
        break

    else:
        print("Invalid choice. Try again.")

graph.close()