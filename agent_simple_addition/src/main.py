def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b


def main() -> None:
    """Read two numbers from the user and print their sum."""
    first_number = float(input("Enter first number: "))
    second_number = float(input("Enter second number: "))
    print(add(first_number, second_number))


if __name__ == "__main__":
    main()