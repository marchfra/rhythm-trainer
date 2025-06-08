# Rhythm Trainer

Randomly pick an exercise number from a list. The probability of an exercise being picked increases when the exercise is played badly, and decreases otherwise.

This application is meant to be used with the book "[Ritmiche e stili della chitarra moderna](https://www.crehathor.com/web/ita/store-prodotto.asp?IDprd=637K22098)". This is reflected in the exercise number being capped at 90 by default and in the expected folder structure of the backing tracks.

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

* `csv_path` is the path to the database. Note that the filename of your database **must** end with `.csv`. If omitted, no data will be saved. *Hint: if you're a teacher you can have one database for each student.*
* `first_esercise` and `last_exercise` define the range of exercises to be picked. If you're using this tool with another book, please run the application once with `last_exercise` set to the total number of exercises in your book, then quit and now you can run again with any value of `last_exercise` you want. This should be done once for every database.
* `backing_tracks_dir` is the path to the backing tracks folder (can be downloaded from inside your personal area of the [Crehathor website](https://www.crehathor.com/web/ita/store-prodotto.asp?IDprd=A594290LQ)). Unless your book's backing tracks follow the *exact* same structure as this book, this field must be omitted.

### Tips for teachers

If you have multiple students, each with their own exercise range and weaker exercises, you can approach the problem in two ways:

1. download the executable in one folder and have one `.csv` file per student; you then need to edit `config.yaml` for every student, pointing to the correct database and updating it with the correct exercise range. This is rather cumbersome and is discouraged.

2. since the executable is fairly light, a much more streamlined approach would be to create a directory for every student and copy the executable in every direcotry. Then, for each student, you can have one `config.yaml` pointing to the correct `.csv` file, and with the correct exercise range. This way the only time you should need to update the configuration file is when the student moves on to play new exercises.
