You are generating synthetic training data for an AI system that learns how to convert general life goals into realistic, structured action plans.

Generate one scenario at a time.

The scenario must reflect real human complexity, including competing priorities, emotional factors, environmental constraints, and imperfect motivation.

Output MUST be valid JSON using this schema:

{
"goal": string,
"goal_category": "one_time" or "habit",
"goal_type": string,
"time_horizon": integer (days),
"description": string,
,"tasks": [
{
"index": integer,
"task": string,
"description": string,
"is_repeatable": boolean,
"repeat_frequency": integer,
"gap_flag": boolean,
"estimated_duration_minutes": {
"min": number,
"max": number
}
}
]
}

Requirements:

* Goals may include improving relationships, managing stress, organizing life, building routines, financial discipline, personal growth, moving homes, improving sleep, or life transitions.
* Include emotional or practical challenges such as low motivation, stress, lack of clarity, time pressure, or conflicting responsibilities.
* Plans should balance effort with recovery or reflection where appropriate.
* Tasks must be concrete and actionable.
* Tasks must be more than 3,
* Include gradual progress rather than extreme changes.
* Ensure realism — avoid overly optimized schedules.
* Vary life situations widely across samples.
* Sometimes include setbacks or uncertainty.