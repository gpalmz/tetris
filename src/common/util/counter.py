def create_counter():
    count = 0

    def inc():
        nonlocal count  # python is really fucked isn't it?
        count += 1
        return count

    return inc