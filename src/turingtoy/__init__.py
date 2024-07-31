from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

import poetry_version
__version__ = poetry_version.extract(source_file=__file__)

def run_turing_machine(
    machine: Dict,
    input_: str,
    steps: Optional[int] = None,
) -> Tuple[str, List, bool]:
    memory = list(input_)
    state = machine["start state"]
    position = 0
    reading = memory[position]
    transition = machine["table"][state][reading]
    stopped = False
    history = [
        {
            "state": state,
            "position": position,
            "transition": transition,
            "reading": memory[position],
            "memory": "".join(memory),
        }
    ]

    while machine["final states"] and state not in machine["final states"]:
        trace = {}
        # If current state is not in the machine table
        if state not in machine["table"]:
            stopped = True
            memory = list(f"Invalid state: {state}")
            break
        trace["state"] = state

        # Read the current symbol
        try:
            reading = memory[position]
        except IndexError:
            reading = machine["blank"]
            memory.append(reading)
        trace["reading"] = reading

        # If symbol is not in the machine table
        if reading not in machine["table"][state]:
            stopped = True
            memory = list(f"Invalid symbol: `{reading}` @(p:{position})")
            break

        # Get the transition from the table
        transition = machine["table"][state][reading]
        trace["position"] = position
        trace["memory"] = "".join(memory)
        trace["transition"] = transition

        # Update Turing machine state
        memory, state, position = state_update(
            state, transition, position, memory, machine["blank"]
        )
        # Add current state to machine history
        history.append(trace)

    memory = clean_ribbon(memory, machine["blank"])
    return "".join(memory), history, not stopped

def clean_ribbon(memory: List[str], blank: str = " ") -> List[str]:
    while memory and memory[0] == blank:
        memory.pop(0)

    while memory and memory[-1] == blank:
        memory.pop()

    return memory

def state_update(
    state: str,
    transition: Dict | str,
    position: int,
    memory: List[str],
    blank: str = " ",
) -> Tuple[List[str], str, int]:
    # If transition contain a write operation -> ribbon is updated
    if "write" in transition and position < len(memory):
        memory[position] = transition["write"]

    if isinstance(transition, dict):
        position = position + 1 if "R" in transition else position - 1
        state = transition.get("R") if "R" in transition else transition.get("L")

    if isinstance(transition, str):
        position = position + 1 if transition == "R" else position - 1

    if position < 0:
        memory.insert(0, blank)
        position = 0

    return memory, state, position