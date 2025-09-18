import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def create_tables(): # Создание всех необходимых таблиц в базе данных и добавление начальных данных
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor() # Создаем объект cursor для выполнения SQL-запросов
    # Выполняем SQL-скрипт, создающий таблицы, если они не существуют
    cursor.executescript(""" 
    CREATE TABLE IF NOT EXISTS languages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS countries (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS directors (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS genres (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS movies (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      director TEXT,
      release_year INTEGER,
      genre TEXT,
      duration INTEGER,
      rating REAL,
      language_id INTEGER,
      country_id INTEGER,
      description TEXT,
      FOREIGN KEY (language_id) REFERENCES languages(id),
      FOREIGN KEY (country_id) REFERENCES countries(id)
    );
    """)
    # Изначальные данные для языков и стран
    cursor.executemany("INSERT OR IGNORE INTO languages (name) VALUES (?)", 
                       [("English",), ("French",), ("Estonian",), ("German",), ("Spanish",)])
    cursor.executemany("INSERT OR IGNORE INTO countries (name) VALUES (?)", 
                       [("USA",), ("France",), ("Estonia",), ("Germany",), ("Spain",)])
    # Изначальные данные для режиссёров и жанров
    cursor.executemany("INSERT OR IGNORE INTO directors (name) VALUES (?)",
                       [("Andrei Tarkovsky",), ("Alexander Nevzorov",), ("Quentin Tarantino",)])
    cursor.executemany("INSERT OR IGNORE INTO genres (name) VALUES (?)",
                       [("Actionfilm",), ("Dokfilm",), ("Draama",)])
    conn.commit()
    conn.close()
    
def get_id(table, name): #Получение id по названию из указанной таблицы
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table} WHERE name=?", (name,))  # Получаем id по имени
    res = cursor.fetchone() # Извлекаем одну строку результата
    conn.close()
    return res[0] if res else None

def load_list(table):    # Функция загружает список всех названий (name) из указанной таблицы (table), отсортированных по алфавиту.
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM {table} ORDER BY name")  # SQL-запрос для получения всех значений из столбца name, отсортированных по алфавиту
    items = [row[0] for row in cursor.fetchall()]  # Получаем все строки результата и извлекаем только значения name в список
    conn.close()
    return items

def load_movies(search=None): #Загружает фильмы из базы данных
    for item in tree.get_children():
        tree.delete(item)
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    # SQL-запрос для получения информации о фильмах, включая названия языка и страны
    query = """
    SELECT
        id, title, director, release_year, genre, duration, rating,
        (SELECT name FROM languages WHERE id = language_id) AS language,
        (SELECT name FROM countries WHERE id = country_id) AS country,
        description
    FROM movies
    """
    params = ()
    if search:
        query += " WHERE title LIKE ?"
        params = (f"%{search}%",)
    cursor.execute(query, params) # Выполнение запроса
    rows = cursor.fetchall() # Получение всех строк результата запроса
    for idx, row in enumerate(rows):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        tree.insert("", tk.END, values=row, tags=(tag,))  # Добавление строки в таблицу
    conn.close()

def search_movies():  # Получает текст из поля поиска и вызывает загрузку фильмов
    query = search_var.get().strip()
    load_movies(query if query else None)

def open_form(movie_data=None): # Открывает форму для добавления или редактирования фильма
    form = tk.Toplevel(root) # Создает новое окно поверх основного
    form.title("Uuenda filmi" if movie_data else "Lisa uus film") # Заголовок окна
    form.configure(bg="#f0f0f0") 

    labels = ["Pealkiri", "Režissöör", "Aasta", "Žanr", "Kestus", "Reiting", "Keel", "Riik", "Kirjeldus"] # Метки для полей ввода
    entries = {}
     
    def load_dropdown_values(): # Загружает значения для выпадающих списков из базы данных
        languages = load_list("languages")
        countries = load_list("countries")
        directors = load_list("directors")
        genres = load_list("genres")
        return directors, genres, languages, countries 

    directors, genres, languages, countries = load_dropdown_values() 

    def validate_year(text): # Проверяет, что введенный текст является годом (четыре цифры или пусто)
        return text.isdigit() and len(text) <= 4 or text == "" 

    vcmd_year = form.register(validate_year) 

    def add_new_value(field): # Функция для добавления нового значения в выпадающий список
        def save_new():  #будет вызвана, когда пользователь нажмёт кнопку "Lisa" в новом окне. Она сохраняет новое значение в базу данных.
            new_val = entry.get().strip()
            if not new_val: # Проверка, что значение не пустое
                messagebox.showerror("Viga", "Sisesta väärtus!")
                return
            conn = sqlite3.connect('movies.db') 
            cursor = conn.cursor()
            try:
                if field == "Keel":
                    cursor.execute("INSERT INTO languages (name) VALUES (?)", (new_val,))
                elif field == "Riik":
                    cursor.execute("INSERT INTO countries (name) VALUES (?)", (new_val,))
                elif field == "Režissöör":
                    cursor.execute("INSERT INTO directors (name) VALUES (?)", (new_val,))
                elif field == "Žanr":
                    cursor.execute("INSERT INTO genres (name) VALUES (?)", (new_val,))
                conn.commit()
            except sqlite3.IntegrityError: # Если значение уже существует, выводим сообщение об ошибке
                messagebox.showerror("Viga", f"See {field.lower()} on juba olemas.")
                conn.close()
                return
            conn.close()
            # Обновляем выпадающий список
            #Проверка, в какую таблицу добавить:
            if field == "Keel": 
                entries[field]['values'] = load_list("languages")
            elif field == "Riik":
                entries[field]['values'] = load_list("countries")
            elif field == "Režissöör":
                entries[field]['values'] = load_list("directors")
            elif field == "Žanr":
                entries[field]['values'] = load_list("genres")
            messagebox.showinfo("Edu", f"Lisatud uus {field.lower()}: {new_val}")
            add_window.destroy()

        add_window = tk.Toplevel(form) # Создает новое окно для добавления нового значения
        add_window.title(f"Lisa uus {field}")
        add_window.geometry("300x100")
        add_window.grab_set()

        tk.Label(add_window, text=f"Sisesta uus {field.lower()}:").pack(pady=5) # Метка с инструкцией для пользователя
        entry = tk.Entry(add_window) # Поле ввода для нового значения
        entry.pack(pady=5, padx=10, fill=tk.X) 

        btn_save = tk.Button(add_window, text="Lisa", command=save_new, bg="#5a5a5a", fg="white")
        btn_save.pack(pady=5)

    for i, label in enumerate(labels): # форма для ввода информации о фильме
        tk.Label(form, text=label, bg="#f0f0f0").grid(row=i, column=0, padx=10, pady=5, sticky='e') 
        if label == "Keel":
            combo = ttk.Combobox(form, state="readonly", values=languages)
            combo.grid(row=i, column=1, padx=10, pady=5, sticky="we")
            entries[label] = combo
            btn_add = tk.Button(form, text="+", width=2, command=lambda f=label: add_new_value(f))
            btn_add.grid(row=i, column=2, padx=5, pady=5)
        elif label == "Riik":
            combo = ttk.Combobox(form, state="readonly", values=countries)
            combo.grid(row=i, column=1, padx=10, pady=5, sticky="we")
            entries[label] = combo
            btn_add = tk.Button(form, text="+", width=2, command=lambda f=label: add_new_value(f))
            btn_add.grid(row=i, column=2, padx=5, pady=5)
        elif label == "Režissöör":
            combo = ttk.Combobox(form, state="readonly", values=directors)
            combo.grid(row=i, column=1, padx=10, pady=5, sticky="we")
            entries[label] = combo
            btn_add = tk.Button(form, text="+", width=2, command=lambda f=label: add_new_value(f))
            btn_add.grid(row=i, column=2, padx=5, pady=5)
        elif label == "Žanr":
            combo = ttk.Combobox(form, state="readonly", values=genres)
            combo.grid(row=i, column=1, padx=10, pady=5, sticky="we")
            entries[label] = combo
            btn_add = tk.Button(form, text="+", width=2, command=lambda f=label: add_new_value(f))
            btn_add.grid(row=i, column=2, padx=5, pady=5)
        elif label == "Aasta":
            entry = tk.Entry(form, validate="key", validatecommand=(vcmd_year, "%P"))
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="we")
            entries[label] = entry
        else:
            entry = tk.Entry(form)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="we")
            entries[label] = entry

    if movie_data:
        entries["Pealkiri"].insert(0, movie_data[1])
        entries["Režissöör"].set(movie_data[2] or "")
        entries["Aasta"].insert(0, movie_data[3] or "")
        entries["Žanr"].set(movie_data[4] or "")
        entries["Kestus"].insert(0, movie_data[5] or "")
        entries["Reiting"].insert(0, movie_data[6] or "")
        entries["Keel"].set(movie_data[7] or "")
        entries["Riik"].set(movie_data[8] or "")
        entries["Kirjeldus"].insert(0, movie_data[9] or "")

    def save():
        title = entries["Pealkiri"].get().strip()
        director = entries["Režissöör"].get().strip()
        year = entries["Aasta"].get().strip()
        genre = entries["Žanr"].get().strip()
        duration = entries["Kestus"].get().strip()
        rating = entries["Reiting"].get().strip()
        language = entries["Keel"].get().strip()
        country = entries["Riik"].get().strip()
        description = entries["Kirjeldus"].get().strip()

        if not all([title, director, year, genre, duration, rating, language, country]):
            messagebox.showerror("Viga", "Kõik väljad peale kirjelduse peavad olema täidetud!")
            return

        if not year.isdigit() or len(year) != 4:
            messagebox.showerror("Viga", "Aasta peab koosnema neljast numbrist!")
            return

        try:
            rating_value = float(rating)
            if not (1 <= rating_value <= 10):
                raise ValueError
        except ValueError:
            messagebox.showerror("Viga", "Reiting peab olema arv vahemikus 1 kuni 10!")
            return

        if not duration.isdigit():
            messagebox.showerror("Viga", "Kestus peab olema täisarv (minutites)!")
            return

        language_id = get_id("languages", language)
        country_id = get_id("countries", country)

        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        if movie_data:
            cursor.execute("""
                UPDATE movies SET title=?, director=?, release_year=?, genre=?, duration=?, rating=?, language_id=?, country_id=?, description=?
                WHERE id=?
            """, (title, director, year, genre, int(duration), rating_value, language_id, country_id, description, movie_data[0]))
        else:
            cursor.execute("""
                INSERT INTO movies (title, director, release_year, genre, duration, rating, language_id, country_id, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, director, year, genre, int(duration), rating_value, language_id, country_id, description))
        conn.commit()
        conn.close()
        load_movies()
        form.destroy()

    btn_text = "Uuenda" if movie_data else "Lisa"
    tk.Button(form, text=btn_text, command=save, bg="#5a5a5a", fg="white", padx=10, pady=5).grid(row=len(labels), column=0, columnspan=3, pady=10)

def delete_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Viga", "Vali tabelist rida, mida kustutada!")
        return
    item = tree.item(selected[0])
    movie_id = item['values'][0]
    if messagebox.askyesno("Kinnita", "Kas oled kindel, et soovid kustutada valitud filmi?"):
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        conn.commit()
        conn.close()
        load_movies()

def open_update():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Viga", "Vali tabelist rida, mida uuendada!")
        return
    item = tree.item(selected[0])
    data = item['values']
    open_form(movie_data=data)

root = tk.Tk()
root.title("Filmi andmete haldamine")
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white", font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#4a90e2", foreground="white")
style.map("Treeview", background=[("selected", "#3399ff")])

search_var = tk.StringVar()

search_frame = tk.Frame(root, bg="#f0f0f0")
search_frame.pack(pady=5, fill=tk.X)

tk.Label(search_frame, text="Otsi pealkirja:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, textvariable=search_var)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
search_entry.bind("<Return>", lambda e: search_movies())

def styled_button(parent, text, command):
    return tk.Button(parent, text=text, command=command, bg="#5a5a5a", fg="white", padx=10, pady=5)

button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=5)

btn_search = styled_button(button_frame, "Otsi", search_movies)
btn_search.pack(side=tk.LEFT, padx=5)
btn_add = styled_button(button_frame, "Lisa uus", lambda: open_form())
btn_add.pack(side=tk.LEFT, padx=5)
btn_update = styled_button(button_frame, "Uuenda", open_update)
btn_update.pack(side=tk.LEFT, padx=5)
btn_delete = styled_button(button_frame, "Kustuta", delete_selected)
btn_delete.pack(side=tk.LEFT, padx=5)

columns = ("ID", "Pealkiri", "Režissöör", "Aasta", "Žanr", "Kestus", "Reiting", "Keel", "Riik", "Kirjeldus")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.pack(fill=tk.BOTH, expand=True)

for col in columns:
    tree.heading(col, text=col)
    if col == "Kirjeldus":
        tree.column(col, width=200)
    elif col == "Pealkiri":
        tree.column(col, width=150)
    else:
        tree.column(col, width=100)

tree.tag_configure('oddrow', background="#ffffff")
tree.tag_configure('evenrow', background="#f9f9f9")

create_tables()
load_movies()

root.mainloop()
