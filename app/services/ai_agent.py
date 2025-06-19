import logfire
from pydantic_ai import Agent

from app.models.ai_models import HintRequest, HintResponse
from app.services.ai_config import AIConfig

# Initialize the hint agent
code_tutor_agent = Agent(
    model=AIConfig.get_gemini_model(),
    output_type=HintResponse,
    system_prompt="""You are an expert JavaScript algorithms tutor helping students learn data structures and algorithms.

Your role:
- Analyze the user's code and automatically determine what type of help they need
- Provide helpful hints without giving away the complete solution
- Explain concepts clearly for beginners
- Guide students through problem-solving step by step
- Focus on JavaScript syntax and best practices

Analysis Guidelines:
- If code is empty/minimal: Focus on concepts and getting started
- If syntax errors exist: Help with JavaScript syntax
- If structure exists but logic is wrong: Guide through algorithmic thinking
- If code runs but fails tests: Help with debugging and edge cases
- If code is close to correct: Provide final optimization hints

Response Guidelines:
- Keep hints concise but informative
- Provide code snippets only when necessary for understanding
- Always include next steps to guide the student forward
- Adjust your language based on the difficulty level
- Set confidence_score between 0.1-1.0 based on how helpful you think your hint is
- Set detected_issue_type to describe what problem you identified (e.g., "missing base case", "syntax error", "wrong approach", "concept understanding")
""",
)


async def generate_hint(request: HintRequest) -> HintResponse:
    """Generate a contextual hint based on the request."""
    with logfire.span("generate_hint"):
        try:
            # Convert previous hints to JSON strings
            previous_hints_str = (
                [hint.model_dump_json() for hint in request.previous_hints]
                if request.previous_hints
                else []
            )

            # Create the prompt with context
            prompt = f"""
            Exercise: {request.exercise_description}
            
            User's current code:
            ```javascript
            {request.user_code}
            ```
            
            Test cases that need to pass:
            ```javascript
            {request.test_cases}
            ```
            
            Student difficulty level: {request.difficulty_level}
            Previous hints given: {len(request.previous_hints)}
            {f"Previous hints were: {'; '.join(previous_hints_str)}" if request.previous_hints else ""}

            {f"Running the user code resulted in an error: {request.error}" if request.error else ""}

            Please provide a helpful hint that guides the student without giving away the complete solution.
            """

            result = await code_tutor_agent.run(prompt)

            logfire.info(
                "Hint generated successfully",
                # detected_issue_type=result.output.detected_issue_type,
                # confidence=result.output.confidence_score,
                output=result.output,
            )

            return result.output

        except Exception as e:
            logfire.error("Error generating hint", error=str(e))
            # Return a fallback response
            return HintResponse(
                hint="I'm having trouble generating a hint right now. Try reviewing the exercise description and your current approach.",
                explanation="Technical issue occurred while processing your request.",
                next_steps=[
                    "Review the problem statement",
                    "Check your code syntax",
                    "Try a different approach",
                ],
                confidence_score=0.1,
                detected_issue_type="technical_error",
            )
