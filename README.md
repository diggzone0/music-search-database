# musicdb

A tiny command-line program that searches a local music database.

This project was created as a learning exercise while studying Python and command-line tools.

## Features

* Search songs by title
* Search songs by artist
* Search songs by genre

## Example

```
python3 musicdb.py
```

```
Search for: rock
```

Output:

```
Imagine - John Lennon (1971)
Smells Like Teen Spirit - Nirvana (1991)
```

## File format

The database uses JSON.

Example:

```
[
  {"title": "Imagine", "artist": "John Lennon", "year": 1971, "genre": "Rock"}
]
```

## Goal

Practice writing simple programs that follow:

* Simple code
* Small tools
* Readable structure
