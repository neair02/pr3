from flask import Flask, render_template, request, redirect
from datetime import date
import json
import os

app = Flask(__name__)

TASKS_FILE = 'tasks.json'

def load_tasks():
    """Загружает задачи из JSON-файла"""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tasks(tasks):
    """Сохраняет задачи в JSON-файл"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

tasks = load_tasks()

@app.route('/')
def index():
    """Главная страница - показывает все задачи"""
    filter_type = request.args.get('filter', 'all')
    
    if filter_type == 'active':
        filtered_tasks = [task for task in tasks if not task.get('done', False)]
    elif filter_type == 'completed':
        filtered_tasks = [task for task in tasks if task.get('done', False)]
    else:
        filtered_tasks = tasks
    
    return render_template('index.html', tasks=filtered_tasks, current_filter=filter_type)

@app.route('/add', methods=['POST'])
def add_task():
    """Добавляет новую задачу"""
    new_task = request.form.get('task')
    if new_task and new_task.strip():
        today = date.today().strftime('%Y-%m-%d')
        tasks.append({'text': new_task.strip(), 'date': today, 'done': False})
        save_tasks(tasks)
    return redirect('/')

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    """Переключает статус выполнения задачи"""
    if 0 <= task_id < len(tasks):
        tasks[task_id]['done'] = not tasks[task_id].get('done', False)
        save_tasks(tasks)
    return redirect(request.referrer or '/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Удаляет задачу"""
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect(request.referrer or '/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Редактирует задачу"""
    if 0 <= task_id < len(tasks):
        if request.method == 'POST':
            new_text = request.form.get('task')
            if new_text and new_text.strip():
                tasks[task_id]['text'] = new_text.strip()
                save_tasks(tasks)
            return redirect('/')
        return render_template('edit.html', task=tasks[task_id], task_id=task_id)
    return redirect('/')

@app.route('/active')
def active_tasks():
    """Показывает только активные (невыполненные) задачи"""
    return redirect('/?filter=active')

@app.route('/completed')
def completed_tasks():
    """Показывает только выполненные задачи"""
    return redirect('/?filter=completed')

@app.route('/complete-all')
def complete_all():
    """Отмечает все задачи как выполненные"""
    for task in tasks:
        task['done'] = True
    save_tasks(tasks)
    return redirect(request.referrer or '/')

@app.route('/uncomplete-all')
def uncomplete_all():
    """Снимает отметку выполнения со всех задач"""
    for task in tasks:
        task['done'] = False
    save_tasks(tasks)
    return redirect(request.referrer or '/')

if __name__ == '__main__':
    app.run(debug=True)
