def deduplicate_list(input_list) -> list[any]:
    seen = set()  # Create a set to keep track of seen elements
    deduplicated_list = []  # List to hold deduplicated elements
    for item in input_list:
        if item not in seen:  # Check if the item is already seen
            seen.add(item)  # Add the item to the seen set
            deduplicated_list.append(item)  # Append it to the result list
    return deduplicated_list
