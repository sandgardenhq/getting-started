from typing import Any, Dict
from pydantic import BaseModel
from sandgarden import Sandgarden

class InputSchema(BaseModel):
    """Input schema for the function"""
    # Add your input fields here
    pass

class OutputSchema(BaseModel):
    """Output schema for the function"""
    # Add your output fields here
    pass

def handler(input: Dict[str, Any], sandgarden: Sandgarden) -> Dict[str, Any]:
    """
    Handler function for the Sandgarden function.
    
    Args:
        input: The input data for the function
        sandgarden: The Sandgarden runtime object
        
    Returns:
        Dict[str, Any]: The output data from the function
    """
    # Validate input
    input_data = InputSchema(**input)
    
    # Your function logic here
    
    # Return output
    output = OutputSchema()
    return sandgarden.out(output.dict()) 