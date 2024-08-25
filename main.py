#!/usr/bin/env python3
from datetime import datetime, timedelta
import argparse
import sys

def main():
    parser, args = help_maker()
    if len(sys.argv) == 1:  # No arguments provided
        parser.print_help()
        sys.exit(1)

    # Event management operations
    if getattr(args, 'add_event', None):
        add_event(args.add_event, args.category, args.start_time, args.duration)

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
    parser.add_argument('--view-events', action='store_true', help='Display all events.')
    parser.add_argument('--report', action='store_true', help='Generate a report of all events.')

    # Event specifics
    parser.add_argument('--category', type=str, choices=['Work', 'Exercise', 'Leisure'], help='Category of the event.')
    parser.add_argument('--start-time', type=str, help='Start time of the event in YYYY-MM-DD HH:MM format.')
    parser.add_argument('--duration', type=int, help='Duration of the event in minutes.')

    return parser, parser.parse_args()

#--------------------------------------------------------------------------------------------------------------------------

# Define event management functions
def add_event(name, category, start_time, duration):
    print(f"Adding event: {name}, Category: {category}, Starts at: {start_time}, Duration: {duration} minutes")

def update_event(name, category, start_time, duration):
    print(f"Updating event: {name}, Category: {category}, Starts at: {start_time}, Duration: {duration} minutes")

def delete_event(name):
    print(f"Deleting event: {name}")

# Define viewing and reporting functions
def view_events():
    print("Viewing all scheduled events.")

def generate_report():
    print("Generating event report.")

#--------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
