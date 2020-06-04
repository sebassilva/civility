def calculate_average(average, votes, last):
    average = float(average)
    votes = int(votes)
    last = int(last)
    return ((average * votes) + last) / (votes + 1)