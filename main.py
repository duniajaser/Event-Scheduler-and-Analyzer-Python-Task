#!/usr/bin/env python3
from datetime import datetime, timedelta
import argparse
import sys
import json


# Dictionary to store events
events = {}

def validate_date(date_str):
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

    if date_time <= datetime.now():
        print(f"Error: The date '{date_str}' must be in the future.")
        sys.exit(1)
    return date_time

#--------------------------------------------------------------------------------------------------------------------------

def load_events():
    try:
        with open('events.json', 'r') as file:
            global events
            events = json.load(file)
            # Convert keys from string to datetime objects
            events = {datetime.strptime(k, '%Y-%m-%d %H:%M'): v for k, v in events.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        events = {}

#--------------------------------------------------------------------------------------------------------------------------

def save_events():
    with open('events.json', 'w') as file:
        # Convert datetime keys to string for JSON serialization
        json.dump({k.strftime('%Y-%m-%d %H:%M'): v for k, v in events.items()}, file)


#--------------------------------------------------------------------------------------------------------------------------

def main():
    parser, args = help_maker()
    if len(sys.argv) == 1:  # No arguments provided
        parser.print_help()
        sys.exit(1)

    load_events()

    # Event management operations
    # Checking required arguments for adding an event
    if getattr(args, 'add_event', None):
        # Check if all required fields are provided
        if not all([args.category, args.start_time, args.duration]):
            missing_args = [arg for arg, value in [('category', args.category), ('start-time', args.start_time), ('duration', args.duration)] if not value]
            print(f"Missing argument(s) for adding an event: {', '.join(missing_args)}")
            sys.exit(1)
        # If all required arguments are provided, attempt to add the event
        success = add_event(args.add_event, args.category, args.start_time, args.duration)
        if not success:
            print("Failed to add the event. Check details and try again.")
            sys.exit(1)  # Exit if adding the event fails
        view_events()

    if getattr(args, 'free_times', None):
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


    if getattr(args, 'update_event', None):
        update_event(args.update_event, args.category, args.start_time, args.duration)

    if getattr(args, 'delete_event', None):
        delete_event(args.delete_event)

    # Event viewing and analytics
    if getattr(args, 'view_events', False):
        view_events()

    if getattr(args, 'report', False):
        generate_report()

    sys.exit(0)

#--------------------------------------------------------------------------------------------------------------------------

def help_maker():
    parser = argparse.ArgumentParser(
        description="Event Scheduler and Analyzer",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-a', '--add-event', type=str, metavar='<EVENT_NAME>', 
                        help='Add a new event. Requires --category, --start-time, and --duration.')
    parser.add_argument('-u', '--update-event', type=str, metavar='<EVENT_NAME>',
                        help='Update an existing event. Requires --category, --start-time, and --duration.')
    parser.add_argument('-d', '--delete-event', type=str, metavar='<EVENT_NAME>',
                        help='Delete an event.')
    parser.add_argument('-v', '--view-events', action='store_true', help='Display all events.')
    parser.add_argument('-r', '--report', action='store_true', help='Generate a report of all events.')

    # Event specifics
    parser.add_argument('-c', '--category', type=str, choices=['Work', 'Exercise', 'Leisure'], help='Category of the event.')
    parser.add_argument('-s', '--start-time', type=str, help='Start time of the event in "YYYY-MM-DD HH:MM" format.')
    parser.add_argument('-t', '--duration', type=int, help='Duration of the event in minutes.')
    parser.add_argument('-f', '--free-times', type=str, metavar='<DATE>', help='Check free times for a specified date in "YYYY-MM-DD HH:MM" format.')

    return parser, parser.parse_args()

#--------------------------------------------------------------------------------------------------------------------------

# Function to check for time conflicts
def is_time_conflict(new_start, new_duration):
    new_end = new_start + timedelta(minutes=new_duration)
    for start_time, details in events.items():
        end_time = start_time + timedelta(minutes=details['duration'])
        if new_start < end_time and new_end > start_time:
            return True
    return False

#--------------------------------------------------------------------------------------------------------------------------

def add_event(name, category, start_time, duration):
    print(f"Adding event: {name}, Category: {category}, Starts at: {start_time}, Duration: {duration} minutes")
    start_datetime = validate_date(start_time)
    if is_time_conflict(start_datetime, duration):
        print("Time conflict detected. Please choose a different time.")
        return False
    events[start_datetime] = {"name": name, "category": category, "duration": duration}
    print(f"Event added: {name} at {start_datetime}")
    save_events()
    return True


#--------------------------------------------------------------------------------------------------------------------------

def update_event(name, category, start_time, duration):
    print(f"Updating event: {name}, Category: {category}, Starts at: {start_time}, Duration: {duration} minutes")

#--------------------------------------------------------------------------------------------------------------------------

def delete_event(name):
    print(f"Deleting event: {name}")

#--------------------------------------------------------------------------------------------------------------------------

def view_events():
    if not events:
        print("No scheduled events.")
        return

    print("Viewing all scheduled events:")
    # Headers
    print(f"{'Start Time':<20} {'Name':<25} {'Category':<15} {'Duration (min)':<15}")
    print("-" * 75)

    # Sorted events by start time
    for start_time, details in sorted(events.items()):
        # Extract event details
        name = details['name']
        category = details['category']
        duration = details['duration']
        # Format the start time
        start_str = start_time.strftime('%Y-%m-%d %H:%M')
        # Print each event in a formatted row
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
        current_end_time = start_time + timedelta(minutes=details['duration'])
        last_end_time = max(last_end_time, current_end_time)

    end_of_day = datetime.combine(date, datetime.max.time().replace(second=0, microsecond=0))
    if last_end_time < end_of_day:
        free_times.append((last_end_time, end_of_day))

    return free_times

#--------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
