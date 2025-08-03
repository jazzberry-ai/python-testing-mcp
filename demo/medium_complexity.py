def validate_user_data(user_data: dict) -> dict:
    """A moderately complex function with branches, loops, and exception handling."""
    if not isinstance(user_data, dict):
        raise TypeError("User data must be a dictionary")
    
    result = {"valid": True, "errors": []}
    
    # Check required fields
    required_fields = ["name", "email", "age"]
    for field in required_fields:
        if field not in user_data:
            result["errors"].append(f"Missing required field: {field}")
            result["valid"] = False
        elif not user_data[field]:
            result["errors"].append(f"Empty value for field: {field}")
            result["valid"] = False
    
    # Validate email format
    if "email" in user_data and user_data["email"]:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, user_data["email"]):
            result["errors"].append("Invalid email format")
            result["valid"] = False
    
    # Validate age
    if "age" in user_data and user_data["age"]:
        try:
            age = int(user_data["age"])
            if age < 0:
                result["errors"].append("Age cannot be negative")
                result["valid"] = False
            elif age > 150:
                result["errors"].append("Age seems unrealistic")
                result["valid"] = False
        except (ValueError, TypeError):
            result["errors"].append("Age must be a valid number")
            result["valid"] = False
    
    return result