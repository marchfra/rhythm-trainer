# Rhythm Trainer

Randomly pick an exercise number from a list. The probability of an exercise being picked increases when the exercise is played badly, and decreases otherwise.

This application is designed to be used with the book "[Ritmiche e stili della chitarra moderna](https://www.crehathor.com/web/ita/store-prodotto.asp?IDprd=637K22098)". This is reflected in the exercise number being capped at 90 by default and in the expected folder structure of the backing tracks.

Should you want to use this tool with other books, edit the [config file](#config-file) accordingly, making sure you omit the `backing_tracks_dir` field.

## Usage

#### Random Mode

When you open the app, you will automatically be in **Random mode**. In this mode, the application will randomly pick an exercise number from the range defined in the config file.

#### Manual Mode

You can switch to **Manual mode** by pressing the "Manual mode" tab. In this mode, you can manually enter an exercise number in the input field. The application will validate the input against your config file.

In either mode, you can play the backing track for the exercise by pressing the "Play backing track" button. If that button is not enabled, it means that the backing track for that exercise is not available in the backing tracks folder and you should probably check that your config file has all the correct settings. If you did not set the `backing_tracks_dir` field in the config file, the button will always be disabled.

After playing the backing track, you can mark the exercise as "Good" or "Bad" by pressing the respective buttons. The application will then adjust the probability of that exercise being picked in Random mode based on your feedback.

### Keyboard Shortcuts

| Shortcut                                      | Description             |
|-----------------------------------------------|-------------------------|
| <kbd>Enter</kbd>                              | Play backing track      |
| <kbd>+</kbd>                                  | Mark exercise as "Good" |
| <kbd>-</kbd>                                  | Mark exercise as "Bad"  |
| <kbd>Ctrl</kbd>/<kbd>Cmd</kbd> + <kbd>1</kbd> | Switch to Random mode   |
| <kbd>Ctrl</kbd>/<kbd>Cmd</kbd> + <kbd>2</kbd> | Switch to Manual mode   |

**Note:** On macOS, use <kbd>Cmd</kbd>. On Windows/Linux, use <kbd>Ctrl</kbd>.

## Config file

In order to use the application you need a config file. This file **must** be placed in the same folder as the script and **must** be named `.config.yaml`. You can edit this file with any common text editor.

``` yaml
backing_tracks_dir: /path/to/backing-tracks/
csv_path: /path/to/database.csv
file_format: mp3        # If omitted defaults to wav
first_exercise: 12      # If omitted defaults to 1
last_exercise: 83       # If omitted defaults to 90
naming_scheme: logical  # If omitted defaults to default
```

Here is an explanation of how it works:

* `backing_tracks_dir` is the path to the backing tracks folder (it can be downloaded from inside your personal area of the [Crehathor website](https://www.crehathor.com/web/ita/store-prodotto.asp?IDprd=A594290LQ)). Unless your book's backing tracks follow the *exact* same structure as this book, this field must be omitted.
* `csv_path` is the path to the database. **This is the only field that must be present**. Note that the filename of your database **must** end with `.csv`. *Hint: if you're a teacher you can have one database for each student.*
* `file_format` is the file extension of the backing tracks. Unless you converted the backing tracks to another format, this field should be omitted. Accepted values are `wav` and `mp3`.
* `first_exercise` and `last_exercise` define the range of exercises to be picked. If you're using this tool with another book, please run the application once with `last_exercise` set to the total number of exercises in your book, then quit and now you can run again with any value of `last_exercise` you want. This should be done once for every database.
* `naming_scheme` is the pattern according to which the backing tracks are named. Unless you renamed the files in the backing tracks folder, this field should be omitted. Accepted values are `default` and `logical`. `default` corresponds to the naming scheme "[chapter] [exercise number] BK.[extension]" (e.g., "Soul 82 BK.wav"). `logical` corresponds to the naming scheme "BK [chapter] [exercise number].[extension]" (e.g., "BK Soul 82.wav").
