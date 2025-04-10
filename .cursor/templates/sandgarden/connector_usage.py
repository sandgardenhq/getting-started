from typing import Any, Dict
from sandgarden import Sandgarden

def use_connector(input: Dict[str, Any], sandgarden: Sandgarden) -> Dict[str, Any]:
    """
    Example of using a Sandgarden connector.
    
    Args:
        input: The input data
        sandgarden: The Sandgarden runtime object
        
    Returns:
        Dict[str, Any]: The output data
    """
    try:
        # Get connector
        connector = sandgarden.get_connector('connector-name')
        
        # Use connector
        result = connector.some_method(input)
        
        return sandgarden.out(result)
        
    except Exception as e:
        # Log error
        sandgarden.log.error(f"Error using connector: {str(e)}")
        raise 