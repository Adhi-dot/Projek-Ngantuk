"""Solution for array sum assignment."""


def main():
    try:
        line1 = input().strip()
        if not line1:
            return
        n = int(line1)
        nums = list(map(int, input().split()))
        print(sum(nums))
    except (EOFError, ValueError):
        pass


if __name__ == "__main__":
    main()
