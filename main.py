#!/usr/bin/env python3
from datetime import datetime, timedelta
import argparse
import sys
import json


# Dictionary to store events
events = {}

def validate_date(date_str, test_time=1):
    """Validate datetime format and ensure the date is not past. Default time to start of day if not provided."""
    try:
        # Attempt to parse the datetime with time
        date_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            # If initial parsing fails, assume only the date is provided and append "00:00" for start of the day
            date_time = datetime.strptime(date_str + " 00:00", "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Error: Invalid date format. Please use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'. Provided date: {date_str}")
            sys.exit(1)
    if test_time == 1:
        if date_time <= datetime.now():
            print(f"Error: The date '{date_str}' must be in the future.")
            sys.exit(1)
    return date_time

#--------------------------------------------------------------------------------------------------------------------------


def load_events():
    try:
        with open('events.json', 'r') as file:
            loaded_events = json.load(file)
            events.clear()
            for k, v in loaded_events.items():
                start_datetime = datetime.strptime(k, '%Y-%m-%d %H:%M')
                events[start_datetime] = (v['name'], v['category'], v['duration'])
    except (FileNotFoundError, json.JSONDecodeError):
        pass  # Handle errors or initialize an empty events dictionary

#--------------------------------------------------------------------------------------------------------------------------

def save_events():
    with open('events.json', 'w') as file:
        json.dump({k.strftime('%Y-%m-%d %H:%M'): {"name": v[0], "category": v[1], "duration": v[2]} for k, v in events.items()}, file)


#--------------------------------------------------------------------------------------------------------------------------

def main():
    parser, args = help_maker()
    if len(sys.argv) == 1:  # No arguments provided
        parser.print_help()
        sys.exit(1)

    load_events()

    # Event management operations
    if args.add:
        # Check if all required fields for adding an event are provided
        if not all([args.name, args.category, args.start_time, args.duration]):
            missing_args = [arg for arg, value in [('name', args.name), ('category', args.category), ('start-time', args.start_time), ('duration', args.duration)] if not value]
            print(f"Missing argument(s) for adding an event: {', '.join(missing_args)}")
            sys.exit(1)
        # If all required arguments are provided, attempt to add the event
        success = add_event(args.name, args.category, args.start_time, args.duration)
        if not success:
            print("Failed to add the event. Check details and try again.")
            sys.exit(1)

    if args.update:
        # Check if all required fields for updating are referenced
        if not args.start_time:
            print("Missing start-time for the update.")
            sys.exit(1)
        # Attempt to update the event
        success = update_event(args.start_time, args.name, args.category, args.duration)
        if not success:
            print("Failed to update the event. Check details and try again.")
            sys.exit(1)

    if args.delete:
        delete_event(args.delete)

    # Event viewing and analytics
    if args.view_events:
        view_events()

    if args.report:
        generate_report()

    if args.filter_category:
        filter_events_by_category(args.filter_category)

    if args.free_times:
        try:
            specified_date = validate_date(args.free_times)  
            free_times = find_free_times(specified_date)
            if free_times:
                for start, end in free_times:
                    print(f"Free from {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')}")
            else:
                print("No free times available on this day.")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")

    sys.exit(0)


#--------------------------------------------------------------------------------------------------------------------------

def help_maker():
    parser = argparse.ArgumentParser(
        description="Event Scheduler and Analyzer",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # General flags for event manipulation
    parser.add_argument('-n', '--name', type=str, help='Name of the event.')
    parser.add_argument('-c', '--category', type=str, choices=['Work', 'Exercise', 'Leisure'], help='Category of the event.')
    parser.add_argument('-s', '--start-time', type=str, help='Start time of the event in "YYYY-MM-DD HH:MM" format for adding or reference for update.')
    parser.add_argument('-t', '--duration', type=int, help='Duration of the event in minutes.')

    # Specific actions
    parser.add_argument('-a', '--add', action='store_true', help='Flag to add a new event. Requires --name, --category, --start-time, and --duration.')
    parser.add_argument('-u', '--update', action='store_true', help='Flag to update an existing event. Use --start-time to specify the event to update.')
    parser.add_argument('-d', '--delete', type=str, metavar='<START_TIME>', help='Delete an event. Requires specifying the start time of the event in "YYYY-MM-DD HH:MM" format.')
    parser.add_argument('-v', '--view-events', action='store_true', help='Display all events.')
    parser.add_argument('-r', '--report', action='store_true', help='Generate a report of all events.')
    parser.add_argument('-f', '--free-times', type=str, metavar='<DATE>', help='Check free times for a specified date in "YYYY-MM-DD HH:MM" format.')
    parser.add_argument('-fc', '--filter-category', type=str, choices=['Work', 'Exercise', 'Leisure'], help='Filter events by category.')

    return parser, parser.parse_args()


#--------------------------------------------------------------------------------------------------------------------------

# Function to check for time conflicts
def is_time_conflict(new_start, new_duration):
    new_end = new_start + timedelta(minutes=new_duration)
    for start_time, details in events.items():
        event_duration = details[2]  # Access the duration from the tuple
        end_time = start_time + timedelta(minutes=event_duration)
        if new_start < end_time and new_end > start_time:
            return True
    return False
#--------------------------------------------------------------------------------------------------------------------------
# Function to add events using tuples
def add_event(name, category, start_time, duration):
    # print(f"Adding event: {name}, Category: {category}, Starts at: {start_time}, Duration: {duration} minutes")
    try:
        start_datetime = validate_date(start_time) 
    except ValueError as e:
        print(str(e))  
        return False
    
    if is_time_conflict(start_datetime, duration):
        print("Time conflict detected. Please choose a different time.")
        # Optionally, find and suggest free times directly here
        free_times = find_free_times(start_datetime)
        if free_times:
            for start, end in free_times:
                print(f"Free from {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("No free times available on this day.")
        return False
    
    # Store the event if no conflicts are found
    events[start_datetime] = (name, category.lower(), duration)
    print(f"Event added: {name} at {start_datetime.strftime('%Y-%m-%d %H:%M')}")
    save_events()
    return True



#--------------------------------------------------------------------------------------------------------------------------

def update_event(original_start_time, new_name=None, new_category=None, new_duration=None):
    try:
        # Convert the original start time to a datetime object
        event_datetime = validate_date(original_start_time)
    except ValueError as e:
        print(f"Error: {str(e)}")
        return False

    if event_datetime not in events:
        print(f"No event found at {original_start_time}.")
        return False

    current_event = events[event_datetime]
    updated_name = new_name if new_name else current_event[0]
    updated_category = new_category.lower() if new_category else current_event[1]
    updated_duration = new_duration if new_duration else current_event[2]

    # If the duration is being changed, check for conflicts before updating
    if new_duration and is_time_conflict(event_datetime, new_duration):
        print("Failed to update due to a time conflict with another event.")
        return False

    # Update the event in the dictionary
    events[event_datetime] = (updated_name, updated_category, updated_duration)
    print(f"Event updated: {updated_name}, Category: {updated_category}, Duration: {updated_duration} minutes")
    save_events()
    return True

#--------------------------------------------------------------------------------------------------------------------------

def delete_event(start_time):
    """Delete an event based on its start time, after printing all current events."""
    # Validate the input date format and convert to datetime
    try:
        start_datetime = validate_date(start_time,test_time=0)
    except ValueError as e:
        print(f"Error: {str(e)}")
        return

    # Attempt to delete the event
    if start_datetime in events:
        del events[start_datetime]
        print(f"Event scheduled to start at {start_datetime.strftime('%Y-%m-%d %H:%M')} has been deleted.")
        save_events()
    else:
        print(f"No event found starting at {start_datetime.strftime('%Y-%m-%d %H:%M')}.")

#--------------------------------------------------------------------------------------------------------------------------

# Function to view events with tuple format
def view_events():
    if not events:
        print("No scheduled events.")
        return
    print("Viewing all scheduled events:")
    print(f"{'Start Time':<20} {'Name':<25} {'Category':<15} {'Duration (min)':<15}")
    print("-" * 75)
    for start_time, (name, category, duration) in sorted(events.items()):
        start_str = start_time.strftime('%Y-%m-%d %H:%M')
        print(f"{start_str:<20} {name:<25} {category:<15} {duration:<15d}")

#--------------------------------------------------------------------------------------------------------------------------

def generate_report():
    print("Generating event report.")

#--------------------------------------------------------------------------------------------------------------------------
def find_free_times(date):
    day_events = [(start_time, details) for start_time, details in events.items() if start_time.date() == date.date()]
    day_events.sort()
    free_times = []
    last_end_time = datetime.combine(date, datetime.min.time())

    for start_time, details in day_events:
        if start_time > last_end_time:
            free_times.append((last_end_time, start_time))
        current_end_time = start_time + timedelta(minutes=details[2])
        last_end_time = max(last_end_time, current_end_time)

    end_of_day = datetime.combine(date, datetime.max.time().replace(second=0, microsecond=0))
    if last_end_time < end_of_day:
        free_times.append((last_end_time, end_of_day))

    return free_times

#--------------------------------------------------------------------------------------------------------------------------

def filter_events_by_category(category):
    filtered_events = {time: details for time, details in events.items() if details[1].lower() == category.lower() }
    if not filtered_events:
        print(f"No events found in category '{category}'.")
    else:
        print(f"Events in category '{category}':")
        print(f"{'Start Time':<20} {'Name':<25} {'Category':<15} {'Duration (min)':<15}")
        print("-" * 75)
        for start_time, (name, cat, duration) in sorted(filtered_events.items()):
            start_str = start_time.strftime('%Y-%m-%d %H:%M')
            print(f"{start_str:<20} {name:<25} {cat:<15} {duration:<15d}")

#--------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
