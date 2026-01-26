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
            current_deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # Try parsing YYYY-MM-DDTHH:MM format (datetime-local input format)
                current_deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
            except ValueError:
                # Try parsing YYYY-MM-DDTHH:MM:SS format
                current_deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
        
        now = datetime.now()
        next_time = current_deadline
        
        # Calculate next occurrence based on recurrence type
        if recurrence_type == 'yearly':
            # 计算下一次出现时间，确保大于当前截止时间
            next_year = current_deadline.year
            while next_time <= current_deadline:
                next_year += recurrence_interval
                try:
                    next_time = current_deadline.replace(year=next_year)
                except ValueError:
                    # 处理2月29日的情况
                    next_time = current_deadline.replace(year=next_year, day=28)
        elif recurrence_type == 'monthly':
            # 计算下一次出现时间，确保大于当前截止时间
            next_month = current_deadline.month
            next_year = current_deadline.year
            while next_time <= current_deadline:
                next_month += recurrence_interval
                year_increment = next_month // 12
                if year_increment > 0:
                    next_month = next_month % 12
                    next_year += year_increment
                if next_month == 0:
                    next_month = 12
                    next_year -= 1
                try:
                    next_time = current_deadline.replace(year=next_year, month=next_month)
                except ValueError:
                    # 处理月末日期的情况
                    if next_month == 2:
                        # 处理2月29日的情况
                        is_leap = (next_year % 4 == 0 and next_year % 100 != 0) or (next_year % 400 == 0)
                        next_time = current_deadline.replace(year=next_year, month=next_month, day=29 if is_leap else 28)
                    else:
                        # 处理其他月份的情况
                        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                        day = days_in_month[next_month - 1]
                        next_time = current_deadline.replace(year=next_year, month=next_month, day=day)
        elif recurrence_type == 'daily':
            # 计算下一次出现时间，确保大于当前截止时间
            while next_time <= current_deadline:
                next_time += timedelta(days=recurrence_interval)
        elif recurrence_type == 'hourly':
            # 计算下一次出现时间，确保大于当前截止时间
            while next_time <= current_deadline:
                next_time += timedelta(hours=recurrence_interval)
        elif recurrence_type == 'minutely':
            # 计算下一次出现时间，确保大于当前截止时间
            while next_time <= current_deadline:
                next_time += timedelta(minutes=recurrence_interval)
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
                
                # 如果没有设置特定日期，使用原始截止日期的星期几作为默认值
                if not days_of_week:
                    days_of_week = [current_deadline.weekday()]
                
                # Make sure days_of_week is a list of integers
                days_of_week = [int(day) for day in days_of_week if isinstance(day, (int, float, str))]
                days_of_week = sorted(days_of_week)
                
                # Get current deadline weekday (0-6, Monday is 0, Sunday is 6)
                current_weekday = current_deadline.weekday()
                
                # 找到下一个匹配的星期几，确保下一次出现时间大于当前截止时间
                found = False
                # 首先检查本周剩余的星期几
                for day in days_of_week:
                    if day > current_weekday:
                        # 计算距离下一个匹配日的天数
                        days_diff = day - current_weekday
                        # 设置下一个出现时间为当前截止时间 + 天数差
                        next_time = current_deadline + timedelta(days=days_diff)
                        found = True
                        break
                
                if not found:
                    # 本周没有匹配的星期几，找到下周第一个匹配的星期几
                    days_diff = 7 - current_weekday + days_of_week[0]
                    next_time = current_deadline + timedelta(days=days_diff)
            except Exception as e:
                if logger:
                    logger.error(f"Error calculating next occurrence: {e}")
                # 出错时，默认递增一周
                next_time = current_deadline + timedelta(weeks=recurrence_interval)
        else:
            # Default weekly recurrence
            next_time = current_deadline + timedelta(weeks=recurrence_interval)
        
        # Format and return
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        if logger:
            logger.error(f"Error calculating next occurrence: {e}")
        return None


def generate_all_occurrences(deadline, recurrence_type, recurrence_interval, recurrence_days, logger=None, limit=20):
    """Generate all occurrences of a recurring todo from creation time to next occurrence after now
    
    Args:
        deadline: Creation deadline
        recurrence_type: Recurrence type (yearly, monthly, weekly, daily, hourly, minutely)
        recurrence_interval: Recurrence interval
        recurrence_days: Weekly specific days in JSON format
        logger: Optional logger for error logging
        limit: Maximum number of occurrences to generate
    
    Returns:
        List of occurrence times in ISO format string or empty list if calculation fails
    """
    try:
        # Parse deadline with multiple format support
        try:
            # Try parsing YYYY-MM-DD HH:MM:SS format
            creation_deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # Try parsing YYYY-MM-DDTHH:MM format (datetime-local input format)
                creation_deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
            except ValueError:
                # Try parsing YYYY-MM-DDTHH:MM:SS format
                creation_deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
        
        now = datetime.now()
        occurrences = []
        current_occurrence = creation_deadline
        
        # 生成指定数量的实例
        for _ in range(limit):
            # 确保当前实例是有效的日期时间
            try:
                # Add to occurrences list
                occurrences.append(current_occurrence.strftime("%Y-%m-%d %H:%M:%S"))
                
                # Calculate next occurrence
                if recurrence_type == 'yearly':
                    next_year = current_occurrence.year + recurrence_interval
                    try:
                        current_occurrence = current_occurrence.replace(year=next_year)
                    except ValueError:
                        # 处理2月29日的情况
                        current_occurrence = current_occurrence.replace(year=next_year, day=28)
                elif recurrence_type == 'monthly':
                    next_month = current_occurrence.month + recurrence_interval
                    next_year = current_occurrence.year
                    year_increment = next_month // 12
                    if year_increment > 0:
                        next_month = next_month % 12
                        next_year += year_increment
                    if next_month == 0:
                        next_month = 12
                        next_year -= 1
                    try:
                        current_occurrence = current_occurrence.replace(year=next_year, month=next_month)
                    except ValueError:
                        # 处理月末日期的情况
                        if next_month == 2:
                            # 处理2月29日的情况
                            is_leap = (next_year % 4 == 0 and next_year % 100 != 0) or (next_year % 400 == 0)
                            current_occurrence = current_occurrence.replace(year=next_year, month=next_month, day=29 if is_leap else 28)
                        else:
                            # 处理其他月份的情况
                            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                            day = days_in_month[next_month - 1]
                            current_occurrence = current_occurrence.replace(year=next_year, month=next_month, day=day)
                elif recurrence_type == 'daily':
                    current_occurrence += timedelta(days=recurrence_interval)
                elif recurrence_type == 'hourly':
                    current_occurrence += timedelta(hours=recurrence_interval)
                elif recurrence_type == 'minutely':
                    current_occurrence += timedelta(minutes=recurrence_interval)
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
                        
                        # 如果没有设置特定日期，使用原始截止日期的星期几作为默认值
                        if not days_of_week:
                            days_of_week = [creation_deadline.weekday()]
                        
                        # Make sure days_of_week is a list of integers
                        days_of_week = [int(day) for day in days_of_week if isinstance(day, (int, float, str))]
                        days_of_week = sorted(days_of_week)
                        
                        # Get current weekday (0-6, Monday is 0, Sunday is 6)
                        current_weekday = current_occurrence.weekday()
                        
                        # 找到下一个匹配的星期几
                        found = False
                        # 首先检查本周剩余的星期几
                        for day in days_of_week:
                            if day > current_weekday:
                                # 计算距离下一个匹配日的天数
                                days_diff = day - current_weekday
                                # 设置下一个出现时间为当前时间 + 天数差
                                current_occurrence = current_occurrence + timedelta(days=days_diff)
                                found = True
                                break
                        
                        if not found:
                            # 本周没有匹配的星期几，找到下周第一个匹配的星期几
                            days_diff = 7 - current_weekday + days_of_week[0]
                            current_occurrence = current_occurrence + timedelta(days=days_diff)
                    except Exception as e:
                        if logger:
                            logger.error(f"Error parsing recurrence_days: {e}")
                        # 出错时，默认递增一周
                        current_occurrence += timedelta(weeks=recurrence_interval)
                else:
                    # Default weekly recurrence
                    current_occurrence += timedelta(weeks=recurrence_interval)
            except Exception as e:
                if logger:
                    logger.error(f"Error generating next occurrence: {e}")
                break
        
        return occurrences
    except Exception as e:
        if logger:
            logger.error(f"Error generating all occurrences: {e}")
        return []