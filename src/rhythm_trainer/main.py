def main() -> None:
    ...
    # config = parse_config()

    # exercises, weights = get_exercises_and_weights(
    #     config.csv_path,
    #     config.first_exercise,
    #     config.last_exercise,
    #     verbose=True,
    # )

    # buffer: list[int] = []

    # while True:
    #     if config.random_mode:
    #         exercise = pick_random_exercise(exercises, weights, buffer)
    #     else:
    #         exercise = get_number_input(
    #             "Enter the exercise number to play: ",
    #             config.first_exercise,
    #             config.last_exercise,
    #         )
    #         print()

    #     print(f"Play exercise {exercise}")
    #     if config.backing_tracks_dir:
    #         input("Press Enter to play the backing track for this exercise...")
    #         play_backing_track(
    #             exercise,
    #             config.backing_tracks_dir,
    #             NamingScheme.LOGICAL,
    #             "mp3",
    #         )

    #     response = get_valid_input("Did you play it well? (y/n/q): ", ["y", "n", "q"])

    #     if response == "q":
    #         save_exercises_and_weights(
    #             config.csv_path,
    #             exercises,
    #             weights,
    #             verbose=True,
    #         )
    #         sys.exit(0)

    #     print()
    #     if response == "y":
    #         if weights[exercise - config.first_exercise] > 1:
    #             weights[exercise - config.first_exercise] -= 1
    #     elif response == "n":
    #         weights[exercise - config.first_exercise] += 1
    #     else:
    #         raise ValueError("Unexpected response.")

    #     save_exercises_and_weights(config.csv_path, exercises, weights)


if __name__ == "__main__":
    main()
