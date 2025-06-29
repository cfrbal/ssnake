# No context imports or boilerplate needed for this!

def task_complete():
    """
    TOOL: Signals that the task is complete.
    Returns a special dictionary to stop the agent's run loop.
    """
    print("--> TOOL 'task_complete' EXECUTED: Returning stop signal.")
    
    # Return a structured response instead of just a string
    return {
        "content": "Task has been marked as complete. The agent will now shut down.",
        "control_signal": "STOP"  # This is the special signal
    }