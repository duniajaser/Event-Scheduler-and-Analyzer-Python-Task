import pytest
from datetime import datetime
from freezegun import freeze_time
from main import (
    validate_date, add_event, update_event, delete_event, view_events,
    find_free_times, filter_events_by_category, events, save_events, load_events
)
from unittest.mock import patch

# Mock the events dictionary to start with known data
@pytest.fixture(autouse=True)
def setup_events():
    # Used `global` keyword to modify the global `events` dictionary directly
    global events
    events.clear()
    events.update({
        datetime.strptime("2024-09-15 11:00", "%Y-%m-%d %H:%M"): ("Sprint Review", "Work", 60),
        datetime.strptime("2024-09-15 17:00", "%Y-%m-%d %H:%M"): ("Park Picnic", "Leisure", 120)
    })

# Testing validate_date with different scenarios using freezegun to freeze time
@pytest.mark.parametrize("date_str, expected_exception, expected_message, is_future", [
    ("2024-09-05 12:00", None, None, True),  # Future date with time
    ("2024-09-03 12:00", ValueError, "The date '2024-09-03 12:00' must be in the future.", False),  # Past date with time
    ("2024-09-04", ValueError, "The date '2024-09-04' must be in the future.", False),  # Today's date without time, should fail
    ("2024-09-06", None, None, True),  # Future date without time
    ("2024-09-02", ValueError, "The date '2024-09-02' must be in the future.", False),  # Past date without time
    ("invalid-date", ValueError, "Invalid date format. Please use 'YYYY-MM-DD HH:MM'. Provided date: invalid-date", None),  # Invalid format
    ("2024-09-04 12:00", ValueError, "The date '2024-09-04 12:00' must be in the future.", False)  # Exact current moment
])
@freeze_time("2024-09-04 12:00")
def test_validate_date(date_str, expected_exception, expected_message, is_future):
    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            validate_date(date_str)
        assert expected_message in str(exc_info.value)
    elif is_future:
        # Expect the function to return a datetime object
        result = validate_date(date_str)
        assert isinstance(result, datetime)
    else:
        # Test should pass without raising an exception for current or ambiguous cases
        result = validate_date(date_str)
        assert isinstance(result, datetime)

# Testing add_event functionality with different scenarios
@pytest.mark.parametrize("start_time, is_future, has_conflict, expected_result", [
    ("2025-01-01 12:00", True, False, True),  # Future date, no conflict
    ("2023-01-01 12:00", False, False, False), # Past date, should raise error
    ("2025-01-01 12:00", True, True, False),  # Future date, but with conflict
])
def test_add_event(mocker, start_time, is_future, has_conflict, expected_result):
    mocker.patch('main.validate_date', side_effect=ValueError("Date must be in the future") if not is_future else lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M"))
    mocker.patch('main.is_time_conflict', return_value=has_conflict)
    mocker.patch('main.save_events')
    result = add_event("Meeting", "Work", start_time, 60)
    assert result == expected_result
    if result:
        assert datetime.strptime(start_time, "%Y-%m-%d %H:%M") in events

# Testing update_event with conflict detection
def test_update_event_with_conflict():
    with patch('main.is_time_conflict', return_value=True) as mock_conflict:
        result = update_event("2024-09-15 11:00", "Urgent Client Meeting", "Work", 120)
        assert not result
        assert mock_conflict.called, "Conflict check should have been called"

# Testing update_event when no conflict exists
def test_update_event_without_conflict():
    with patch('main.is_time_conflict', return_value=False) as mock_conflict:
        with patch('main.save_events', return_value=None):
            result = update_event("2024-09-15 11:00", "Updated Meeting", "Work", 90)
            assert result
            assert mock_conflict.called, "Conflict check should have been called"
            assert events[datetime.strptime("2024-09-15 11:00", "%Y-%m-%d %H:%M")] == ("Updated Meeting", "work", 90)


# Test delete_event functionality
def test_delete_event_existing():
    # Ensure an event exists before deleting
    delete_event("2024-09-15 11:00")
    assert datetime.strptime("2024-09-15 11:00", "%Y-%m-%d %H:%M") not in events

def test_delete_event_non_existing():
    with patch('builtins.print') as mocked_print:
        delete_event("2025-01-01 12:00")
        mocked_print.assert_called_with("No event found starting at 2025-01-01 12:00.")

def test_delete_event_invalid_format():
    with patch('builtins.print') as mocked_print:
        delete_event("invalid-date")
        mocked_print.assert_called_with("Error: Invalid date format. Please use 'YYYY-MM-DD HH:MM'. Provided date: invalid-date")

# Test view_events functionality
def test_view_events_no_events():
    events.clear()
    with patch('builtins.print') as mocked_print:
        view_events()
        mocked_print.assert_called_with("No scheduled events.")

def test_view_events_with_events():
    with patch('builtins.print') as mocked_print:
        view_events()
        assert mocked_print.call_count > 1  # More than one print statement for listing events

# Test find_free_times functionality
def test_find_free_times_fully_booked_day():
    fully_booked_date = datetime.strptime("2024-09-15", "%Y-%m-%d")
    events.clear()
    events.update({
        datetime.strptime("2024-09-15 08:00", "%Y-%m-%d %H:%M"): ("Morning Meeting", "Work", 180),  # 8:00 - 11:00
        datetime.strptime("2024-09-15 11:00", "%Y-%m-%d %H:%M"): ("Lunch", "Leisure", 60),  # 11:00 - 12:00
        datetime.strptime("2024-09-15 12:00", "%Y-%m-%d %H:%M"): ("Afternoon Workshop", "Work", 300),  # 12:00 - 17:00
    })
    free_times = find_free_times(fully_booked_date)
    assert len(free_times) == 2  # Expected free time slots: before 8:00 and after 17:00

def test_find_free_times_no_events():
    date = datetime.strptime("2024-09-16", "%Y-%m-%d")
    free_times = find_free_times(date)
    assert free_times == [(datetime.combine(date, datetime.min.time()), datetime.combine(date, datetime.max.time().replace(second=0, microsecond=0)))]

# Test filter_events_by_category functionality
def test_filter_events_by_category_with_events():
    with patch('builtins.print') as mocked_print:
        filter_events_by_category('Work')
        assert mocked_print.call_count > 1  # Events are printed

def test_filter_events_by_category_no_events():
    with patch('builtins.print') as mocked_print:
        filter_events_by_category('NonExistentCategory')
        mocked_print.assert_called_with("No events found in category 'NonExistentCategory'.")