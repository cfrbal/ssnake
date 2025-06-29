import utils

def validate_response(response):
    if not response.candidates:
        utils.log_error("AGENT STOPPING: Model returned no response.")
        return False

    candidate = response.candidates[0]

    if not candidate.content or not candidate.content.parts:
        if candidate.finish_reason.name != "TOOL_CALLS":
            utils.log_error(f"AGENT STOPPING: Model returned empty content. Finish Reason: {candidate.finish_reason.name}")
            return False
    return candidate
