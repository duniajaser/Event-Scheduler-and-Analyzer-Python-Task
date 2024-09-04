# Event Scheduler and Analyzer

## Project Overview

The Event Scheduler and Analyzer is a command-line tool designed to help users efficiently manage their daily events. This tool allows users to schedule events, categorize them, detect conflicts, and generate insightful reports. It is ideal for individuals or teams looking to optimize their time management and planning processes.
---
## Features

### 1. Event Management
- **Add, Update, Delete Events**: Users can easily create, modify, or remove events.
- **Event Details**: Each event includes a name, category, start time, and duration.
- **Storage**: Events are stored in a JSON file, with the date and time as the key.

### 2. Conflict Detection
- **Overlapping Event Alerts**: The tool checks for any overlapping events and alerts the user.
- **Conflict Resolution Suggestions**: Provides options to adjust event times to resolve conflicts.

### 3. Event Categorization
- **Category Assignment**: Users can assign categories to events, such as Work, Exercise, Leisure.
- **Filtering**: Easily filter events based on their category for focused analysis.

### 4. Event Analytics
- **Report Generation**: Generate reports on total time spent per category, busiest days, and trends over time.
- **Trend Analysis**: Understand time allocation and discover patterns in event scheduling.

### 5. Command-Line Interface
- **User-Friendly CLI**: Intuitive commands for adding events, viewing schedules, filtering by category, and generating reports.
---
### Usage

Run the tool using the provided shell script:

```bash
./run.sh
```

#### Commands

- **Add an event**:
  ```bash
  ./run.sh --add "Event Name" --category "Category" --start "YYYY-MM-DD HH:MM" --duration "Minutes"
  ```

- **Update an event**:
  ```bash
  ./run.sh --update "Event Start Time" --name "New Event Name" --start "New Start Time" --duration "New Duration"
  ```

- **Delete an event**:
  ```bash
  ./run.sh --delete "Start Time"
  ```

- **View events**:
  ```bash
  ./run.sh --view
  ```

- **Filter events by category**:
  ```bash
  ./run.sh --filter "Category"
  ```

- **Generate a report**:
  ```bash
  ./run.sh --report
  ```
---
## Examples

Here are some example commands to demonstrate the tool's capabilities:

- Adding an event:
  ```bash
  ./run.sh --add "Team Meeting" --category "Work" --start "2024-09-01 09:00" --duration "60"
  ```

- Generating a report:
  ```bash
  ./run.sh --report
  ```
---
## Files

- `main.py`: The main script to run the application.
- `events.json`: The file where events are stored.
- `run.sh`: A shell script to simplify running the tool.
- `report_log.log`: Log file for report generation.
- `unit_testing.py`: Contains unit tests for the application.

## Testing

Unit tests are provided to ensure the functionality of the tool. To run the tests:

```bash
pytest unit_testing.py
```

---
