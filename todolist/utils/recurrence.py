import json
from datetime import datetime, timedelta


def calculate_next_occurrence(deadline, recurrence_type, recurrence_interval, recurrence_days, logger=None):
    """Calculate next occurrence time based on recurrence settings
    
    Args:
        deadline: Current deadline
        recurrence_type: Recurrence type (yearly, monthly, weekly, daily, hourly, minutely)
        recurrence_interval: Recurrence interval
        recurrence_days: Weekly specific days in JSON format
        logger: Optional logger for error logging
    
    Returns:
        Next occurrence time in ISO format string or None if calculation fails
    """
    try:
        # Parse deadline with multiple format support
        try:
            # Try parsing YYYY-MM-DD HH:MM:SS format
            current_time = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # Try parsing YYYY-MM-DDTHH:MM format (datetime-local input format)
                current_time = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
            except ValueError:
                # Try parsing YYYY-MM-DDTHH:MM:SS format
                current_time = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
        
        next_time = current_time
        
        # Calculate next occurrence based on recurrence type
        if recurrence_type == 'yearly':
            next_time = current_time.replace(year=current_time.year + recurrence_interval)
        elif recurrence_type == 'monthly':
            # Handle month boundary cases
            next_month = current_time.month + recurrence_interval
            year_increment = next_month // 12
            month = next_month % 12 if next_month % 12 != 0 else 12
            year = current_time.year + year_increment
            
            # Handle end-of-month cases
            try:
                next_time = current_time.replace(year=year, month=month)
            except ValueError:
                # Invalid date (e.g., 31st in a short month), adjust to end of month
                if month == 2:
                    # Handle February special case
                    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                    day = 29 if is_leap else 28
                    next_time = current_time.replace(year=year, month=month, day=day)
                else:
                    # Other short months, adjust to end of month
                    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    # Calculate actual month index (January is 0)
                    month_idx = month - 1
                    day = days_in_month[month_idx]
                    next_time = current_time.replace(year=year, month=month, day=day)
        elif recurrence_type == 'daily':
            next_time = current_time + timedelta(days=recurrence_interval)
        elif recurrence_type == 'hourly':
            next_time = current_time + timedelta(hours=recurrence_interval)
        elif recurrence_type == 'minutely':
            next_time = current_time + timedelta(minutes=recurrence_interval)
        elif recurrence_type == 'weekly':
            try:
                # Parse weekly specific days
                days_of_week = []
                
                # Handle different types of recurrence_days values
                if recurrence_days is not None:
                    try:
                        if isinstance(recurrence_days, str):
                            # If it's a string, try to parse as JSON
                            days_of_week = json.loads(recurrence_days)
                        elif isinstance(recurrence_days, int):
                            # If it's an integer, treat it as a single day
                            days_of_week = [recurrence_days]
                        else:
                            # Otherwise, try to convert to a list
                            days_of_week = list(recurrence_days)
                    except (TypeError, json.JSONDecodeError, Exception) as e:
                        # If any error occurs, use default value
                        days_of_week = []
                
                if days_of_week:
                    # Get current weekday (0-6, Monday is 0, Sunday is 6)
                    current_weekday = current_time.weekday()
                    
                    # Make sure days_of_week is a list of integers
                    days_of_week = [int(day) for day in days_of_week if isinstance(day, (int, float, str))]
                    days_of_week = sorted(days_of_week)
                    
                    if days_of_week:
                        # Find next matching weekday
                        found = False
                        for day in days_of_week:
                            if day > current_weekday:
                                # Found in this week
                                next_time = current_time + timedelta(days=(day - current_weekday))
                                found = True
                                break
                        
                        if not found:
                            # Not found in this week, find first matching next week
                            next_time = current_time + timedelta(days=(7 - current_weekday + days_of_week[0]))
                    else:
                        # Default weekly recurrence
                        next_time = current_time + timedelta(weeks=recurrence_interval)
                else:
                    # Default weekly recurrence
                    next_time = current_time + timedelta(weeks=recurrence_interval)
            except Exception as e:
                if logger:
                    logger.error(f"Error parsing recurrence_days: {e}")
                next_time = current_time + timedelta(weeks=recurrence_interval)
        else:
            # Default weekly recurrence
            next_time = current_time + timedelta(weeks=recurrence_interval)
        
        # Format and return
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        if logger:
            logger.error(f"Error calculating next occurrence: {e}")
        return None
