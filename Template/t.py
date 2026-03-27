def merge_intervals(intervals):
    if not intervals:
        return []

    intervals.sort()  # Sort by start time
    merged = [intervals[0]]

    for current in intervals[1:]:
        last = merged[-1]

        # If overlapping, merge them
        if current[0] <= last[1]:
            last[1] = max(last[1], current[1])
        else:
            merged.append(current)

    return merged
