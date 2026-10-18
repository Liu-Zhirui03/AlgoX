"""Activity selection and unweighted interval scheduling snapshots."""

from inspect import getsource
from pydantic import BaseModel, Field, model_validator
from backend.algorithms.greedy import Label, Nonnegative, Positive, Recorder
from backend.schemas import AlgorithmResult
from examples.activity_selection import activity_selection

ALGORITHM_ID = "activity-selection"
TITLE = "Activity Selection and Interval Scheduling"
CATEGORY = "Greedy Algorithms"
RENDERER = "activity-timeline"
PLAYGROUND_FILE = "activity-selection.html"
DEFAULT_INPUT = {"activities": [{"name": name, "start": start, "finish": finish} for name, start, finish in [("A", 1, 4), ("B", 3, 5), ("C", 0, 6), ("D", 5, 7), ("E", 3, 9), ("F", 8, 11), ("G", 12, 16)]]}


class Activity(BaseModel):
    name: Label
    start: Nonnegative
    finish: Positive

    @model_validator(mode="after")
    def valid_interval(self):
        if self.start >= self.finish:
            raise ValueError("Each activity must start before it finishes.")
        return self


class ActivityInput(BaseModel):
    activities: list[Activity] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def unique_names(self):
        if len({item.name for item in self.activities}) != len(self.activities):
            raise ValueError("Activity names must be unique.")
        return self


def activity_steps(payload: ActivityInput):
    recorder = Recorder({"activities": [item.model_dump() for item in payload.activities], "order": list(range(len(payload.activities))), "selected": [], "rejected": [], "current": None, "lastFinish": None})
    state = recorder.state
    recorder.record("initial", "Find a maximum-size set of non-overlapping activities. Adjacent intervals can share an endpoint.")
    state["order"] = sorted(state["order"], key=lambda index: (payload.activities[index].finish, index))
    recorder.record("sort", "Order activities by earliest finishing time. Equal finishes keep input order.")
    for index in state["order"]:
        item = payload.activities[index]
        state["current"] = index
        recorder.record("consider", f"Consider {item.name}: [{item.start}, {item.finish}). Previous chosen finish: {state['lastFinish'] if state['lastFinish'] is not None else 'none'}.", [index])
        if state["lastFinish"] is None or item.start >= state["lastFinish"]:
            state["selected"].append(index)
            state["lastFinish"] = item.finish
            recorder.record("accept", f"Accept {item.name}: it starts after or exactly when the previous selected activity finishes.", [index])
        else:
            state["rejected"].append(index)
            recorder.record("reject", f"Reject {item.name}: it overlaps the selected schedule.", [index])
    state["current"] = None
    recorder.record("complete", f"Maximum-size schedule complete: {len(state['selected'])} activities selected.")
    return recorder.steps


def run(payload: ActivityInput) -> AlgorithmResult:
    output = activity_selection([(item.name, item.start, item.finish) for item in payload.activities])
    return AlgorithmResult(algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(activity_selection), input=payload.model_dump(),
        output={**output, "names": [payload.activities[index].name for index in output["selected"]]}, steps=activity_steps(payload))
