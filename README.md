# Rhythm Trainer

Randomly pick an exercise number from a list. The probability of an exercise being picked increases when the exercise is played badly, and decreases otherwise.

This application is meant to be used with the book "[Ritmiche e stili della chitarra moderna](https://www.crehathor.com/web/ita/store-prodotto.asp?IDprd=637K22098)". This is reflected in the exercise number being capped at 90 and in the expected folder structure of the backing tracks.

Should you want to use this tool with other books, edit the [config file](#config-file) accordingly, making sure you omit the `backing_tracks_dir` field.

## Usage

## Config file

In order to use the application you need a config file. This file **must** be placed in the same folder as the script and **must** be named `config.yaml`. You can edit this file with any common text editor.

``` yaml
csv_path: /path/to/database.csv
first_exercise: 15  # If omitted defaults to 1
last_exercise: 23   # If omitted defaults to 90
backing_tracks_dir: /path/to/backing-tracks/
```

Here is an explanation of how it works:

* `csv_path` is the path to the database. Note that the filename of your database **must** end with `.csv`. *Hint: if you're a teacher you can have one database for each student.*
* `first_esercise` and `last_exercise` define the range of exercises to be extracted. If you're using this tool with another book, please run the application once with `last_exercise` set to the total number of exercises in your book, then quit and now you can run again with any value of `last_exercise` you want. This should be done once for every database.
* `backing_tracks_dir` is the path to the backing tracks folder (can be downloaded from inside your personal area of the [Crehathor website](https://www.crehathor.com/web/ita/store-prodotto.asp?IDprd=A594290LQ)). Unless your book's backing tracks follow the *exact* same structure as this book, this field must be omitted.
