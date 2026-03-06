# musicdb – My Music Search Tool

A small command-line program for searching a local music database.

I built this project while learning Python and Git. The goal was to practice writing simple programs that follow the Unix idea of **doing one thing well**. In this case, the program simply loads a small music database and lets you search it from the terminal.

The project is intentionally simple so that the code is easy to read and modify.

---

## What it does

* Loads a small JSON music database
* Lets you search songs by **title**, **artist**, or **genre**
* Prints results in a simple table format in the terminal

Example search:

```
python3 musicdb.py
: Drake
```

Example output:

```
Title                          Artist                    Year   Genre
--------------------------------------------------------------------------------
Imagine                        John Lennon               1971   Rock
Smells Like Teen Spirit        Nirvana                   1991   Rock
```

---

## Requirements

* Python 3.x
* A JSON file containing the music database

No external libraries are required.

---

## Project Structure

```
musicdb/
├── musicdb.py
├── music.json
├── README.md
└── .gitignore
```

**musicdb.py**
Main program that loads the database and performs the search.

**music.json**
Example database file containing songs.

---

## Example Database Format

```
[
  {
    "title": "Imagine",
    "artist": "John Lennon",
    "year": 1971,
    "genre": "Rock"
  },
  {
    "title": "Levels",
    "artist": "Avicii",
    "year": 2011,
    "genre": "EDM"
  }
]
```

---

## Running the Program

From the project folder:

```
python3 musicdb.py edm
```

You can also specify a different database file:

```
python3 musicdb.py rock --file mymusic.json
```

---

## Why I built this

This repository is part of my practice while learning:

* Python
* Command line tools
* Git and GitHub workflows
* Writing small programs that are easy to understand

Instead of building one large application, I'm focusing on smaller tools that each solve a single problem.

---

## Notes

This project is still a work in progress as I continue learning. Improvements and refactoring will happen as I gain more experience.

---

## License

MIT

