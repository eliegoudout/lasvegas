""" Some shared utilitary functions.

Exported Functions:
-------------------
    prompt_integers: Prompts user for integers under unary conditions.
"""

__all__ = ['prompt_integers']

from typing import Callable
import itertools


def prompt_integers(
        message: str,
        num: int,
        *conditions: Callable[[int], bool]) -> list[int]:
    """ Prompts the user to give `num` integers under unary conditions.

    Arguments:
    ----------
        message (str): Message for the user.
        num (int): Number of expected integers.
        *conditions (Condition): Unary conditions that should be met by
            every user input.

    Returns:
    --------
        inputs (list[int]): The list of inputs from the user.
    """
    while True:
        # Prompt integers
        try:
            inputs = list(map(int, input(message).split()))
        except ValueError:
            print("Expected integer inputs!")
            continue
        # Check the number of inputs
        if len(inputs) != num:
            print(f"Expected {num} inputs (got {len(inputs)})!")
            continue
        # Check if conditions are met
        for condition, value in itertools.product(conditions, inputs):
            if not condition(value):
                print(f"Invalid input: {value}!")
                break
        # All good
        else:
            return inputs
