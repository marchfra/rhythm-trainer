def get_valid_input(prompt: str, valid_responses: list[str]) -> str:
    """Validate user input against a list of valid responses."""
    while True:
        response = input(prompt).strip().lower()
        if response in valid_responses:
            return response
        print(
            "Invalid input. Please enter one of the following: "
            f"{', '.join(valid_responses)}.",
        )


def get_number_input(
    prompt: str,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Prompt the user for a number input."""
    while True:
        response = input(prompt).strip()
        if response.isdigit():
            response = int(response)
            if (min_value is None or response >= min_value) and (
                max_value is None or response <= max_value
            ):
                return response
        print("Invalid input.", end=" ")
        if min_value is not None and max_value is not None:
            print(f"Please enter a number between {min_value} and {max_value}.")
        elif min_value is not None:
            print(f"Please enter a number greater than or equal to {min_value}.")
        elif max_value is not None:
            print(f"Please enter a number less than or equal to {max_value}.")
        else:
            print("Please enter a valid number.")
