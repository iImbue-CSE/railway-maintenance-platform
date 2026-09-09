def solve_schedule(tasks: list):
    for idx, task in enumerate(tasks):
        task["block"] = idx % 7
        task["duration"] = 1
    return tasks
