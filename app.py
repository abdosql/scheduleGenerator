from flask import Flask, request, jsonify
from ortools.sat.python import cp_model

app = Flask(__name__)

def create_and_solve_schedule(groups, teachers, classrooms, course_sessions):
    model = cp_model.CpModel()

    # Variables
    x = {}
    for group in groups:
        x[group] = {}
        for day in range(5):
            x[group][day] = {}
            for slot in range(4):
                x[group][day][slot] = {}
                for course in groups[group]:
                    x[group][day][slot][course] = {}
                    for teacher in teachers:
                        x[group][day][slot][course][teacher] = {}
                        for classroom in range(classrooms):
                            var_name = f"x_g{group}_d{day}_s{slot}_c{course}_t{teacher}_r{classroom}"
                            x[group][day][slot][course][teacher][classroom] = model.NewBoolVar(var_name)

    # Add constraints similar to your original code:
    for group in groups:
        for course in groups[group]:
            model.Add(sum(x[group][day][slot][course][teacher][classroom]
                          for day in range(5)
                          for slot in range(4)
                          for teacher in teachers if course in teachers[teacher]
                          for classroom in range(classrooms)) == course_sessions.get(course, 2))

    for teacher in teachers:
        for day in range(5):
            for slot in range(4):
                model.Add(sum(x[group][day][slot][course][teacher][classroom]
                              for group in groups
                              for course in groups[group] if course in teachers[teacher]
                              for classroom in range(classrooms)) <= 1)

    for classroom in range(classrooms):
        for day in range(5):
            for slot in range(4):
                model.Add(sum(x[group][day][slot][course][teacher][classroom]
                              for group in groups
                              for course in groups[group]
                              for teacher in teachers if course in teachers[teacher]) <= 1)

    for group in groups:
        for day in range(5):
            for slot in range(4):
                model.Add(sum(x[group][day][slot][course][teacher][classroom]
                              for course in groups[group]
                              for teacher in teachers if course in teachers[teacher]
                              for classroom in range(classrooms)) <= 1)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        solution = {}
        for group in groups:
            solution[group] = {}
            for day in range(5):
                solution[group][day] = {}
                for slot in range(4):
                    solution[group][day][slot] = None
                    for course in groups[group]:
                        for teacher in teachers:
                            for classroom in range(classrooms):
                                if solver.Value(x[group][day][slot][course][teacher][classroom]):
                                    solution[group][day][slot] = (course, teacher, classroom)
        return solution
    else:
        return None

@app.route('/schedule', methods=['POST'])
def schedule():
    # Extract data from the incoming JSON request
    data = request.json
    groups = data['groups']
    teachers = data['teachers']
    classrooms = data['classrooms']
    course_sessions = data['course_sessions']
    
    solution = create_and_solve_schedule(groups, teachers, classrooms, course_sessions)

    if solution:
        return jsonify({'status': 'success', 'schedule': solution}), 200
    else:
        return jsonify({'status': 'failure', 'message': 'No feasible solution found.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
