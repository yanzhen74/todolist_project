import json


def fromjson_filter(value):
    """JSON string to Python object filter for templates
    
    Args:
        value: JSON string, integer, list, or None
    
    Returns:
        List or empty list if parsing fails
    """
    if value is not None:
        try:
            if isinstance(value, str):
                # 如果是字符串，尝试解析为JSON
                result = json.loads(value)
                # 如果结果不是列表，将其包装为列表
                if not isinstance(result, list):
                    result = [result]
                return result
            elif isinstance(value, (int, float)):
                # 如果是数字，返回包含该数字的列表
                return [int(value)]
            elif isinstance(value, list):
                # 如果已经是列表，直接返回
                return value
            elif isinstance(value, dict):
                # 如果是字典，返回空列表（我们只处理列表）
                return []
            else:
                # 其他情况，尝试转换为字符串并解析
                result = json.loads(str(value))
                # 如果结果不是列表，将其包装为列表
                if not isinstance(result, list):
                    result = [result]
                return result
        except (json.JSONDecodeError, TypeError, ValueError):
            # 如果解析失败，返回空列表
            return []
    return []
