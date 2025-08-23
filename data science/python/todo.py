import json
import time
import threading
from datetime import datetime, timedelta

todo = []  # list of dicts: {"task": str, "time": datetime, "state": str}


# ---------------------- Persistence ----------------------

def save_tasks():
    with open("todo.json", "w") as f:
        json.dump(
            [
                {
                    "task": t["task"],
                    "time": t["time"].strftime("%Y-%m-%d %H:%M") if t["time"] else None,
                    "state": t["state"],
                }
                for t in todo
            ],
            f,
            indent=4,
        )


def load_tasks():
    global todo
    try:
        with open("todo.json", "r") as f:
            data = json.load(f)
            todo = [
                {
                    "task": d["task"],
                    "time": datetime.strptime(d["time"], "%Y-%m-%d %H:%M") if d["time"] else None,
                    "state": d["state"],
                }
                for d in data
            ]
    except FileNotFoundError:
        todo = []


# ---------------------- Display ----------------------

def loop_list():
    if not todo:
        print("\t🗑️ Your To Do is Empty\n")
        return
    for index, t in enumerate(todo, 1):
        due = t["time"].strftime("%Y-%m-%d %H:%M") if t["time"] else "No time set"
        print(f"\t{index}. {t['task']}  | State: {t['state']} | Due: {due}")
    print()


# ---------------------- CRUD ----------------------

def add_task():
    task = input("Enter the task: ")
    time_input = input("Enter schedule time (YYYY-MM-DD HH:MM) or leave blank: ").strip()
    schedule_time = None
    if time_input:
        try:
            schedule_time = datetime.strptime(time_input, "%Y-%m-%d %H:%M")
        except ValueError:
            print("⚠️ Invalid time format. Task will have no schedule.")
    todo.append({"task": task, "time": schedule_time, "state": "Pending"})
    print(f"✅ Task '{task}' added.")
    save_tasks()


def show_task():
    loop_list()
    input("Press Enter to return...")


def modify_task():
    loop_list()
    try:
        user_index = int(input("Enter task number to modify: ")) - 1
        if 0 <= user_index < len(todo):
            todo[user_index]["task"] = input("Modify the task to: ")
            print("✅ Task modified.")
            save_tasks()
        else:
            print("❌ Invalid index.")
    except ValueError:
        print("❌ Invalid input.")


def delete_task():
    loop_list()
    try:
        user_index = int(input("Enter task number to delete: ")) - 1
        if 0 <= user_index < len(todo):
            removed = todo.pop(user_index)
            print(f"🗑️ Task '{removed['task']}' deleted.")
            save_tasks()
        else:
            print("❌ Invalid index.")
    except ValueError:
        print("❌ Invalid input.")


def mark_done():
    loop_list()
    try:
        user_index = int(input("Enter task number to mark as done: ")) - 1
        if 0 <= user_index < len(todo):
            todo[user_index]["state"] = "Done"
            print("✅ Task marked as done.")
            save_tasks()
        else:
            print("❌ Invalid index.")
    except ValueError:
        print("❌ Invalid input.")


# ---------------------- Reminders ----------------------

def reminder_worker():
    while True:
        now = datetime.now()
        for t in todo:
            if t["time"] and t["state"] == "Pending":
                if now >= t["time"]:
                    print(f"\n⏰ Reminder: Task '{t['task']}' is due now!\n")
                    t["state"] = "Overdue"
                    save_tasks()
                elif now + timedelta(minutes=5) >= t["time"]:  # 5 min warning
                    print(f"\n⚠️ Upcoming Task: '{t['task']}' at {t['time'].strftime('%H:%M')}\n")
        time.sleep(60)  # check every minute


# ---------------------- Main ----------------------

def main():
    load_tasks()

    # Start reminder thread
    threading.Thread(target=reminder_worker, daemon=True).start()

    while True:
        print("\n🥳🥳 Welcome to the Python To Do Program 🥳🥳\n")
        print("You can\n",
              "\t1. Add Task\n",
              "\t2. Show Available Tasks\n",
              "\t3. Modify Task\n",
              "\t4. Delete Task\n",
              "\t5. Mark Task as Done\n",
              "\t6. Close the program\n")

        try:
            choice = int(input("Enter your Choice: "))
        except ValueError:
            print("❌ Invalid input.")
            continue

        match choice:
            case 1: add_task()
            case 2: show_task()
            case 3: modify_task()
            case 4: delete_task()
            case 5: mark_done()
            case 6:
                print("👋 Goodbye!")
                save_tasks()
                break
            case _: print("❌ Invalid choice.")


if __name__ == "__main__":
    main()
