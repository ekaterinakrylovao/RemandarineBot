import json
import uuid
import os

DATA_FILE = 'reminders.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"current": [], "completed": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_reminder(reminder):
    data = load_data()
    data["current"].append(reminder)
    save_data(data)

def get_current_reminders():
    data = load_data()
    return data["current"]

def get_completed_reminders():
    data = load_data()
    return data["completed"]

def update_reminder(reminder_id, new_reminder):
    data = load_data()
    data["current"] = [r if r["id"] != reminder_id else new_reminder for r in data["current"]]
    save_data(data)

def mark_reminder_completed(reminder_id):
    data = load_data()
    reminder = next(r for r in data["current"] if r["id"] == reminder_id)
    data["current"] = [r for r in data["current"] if r["id"] != reminder_id]
    reminder["completed_at"] = "now"  # For simplicity, using a placeholder
    data["completed"].append(reminder)
    save_data(data)

def move_reminder_to_current(reminder_id, new_date):
    data = load_data()
    reminder = next(r for r in data["completed"] if r["id"] == reminder_id)
    data["completed"] = [r for r in data["completed"] if r["id"] != reminder_id]
    reminder["date"] = new_date
    data["current"].append(reminder)
    save_data(data)
