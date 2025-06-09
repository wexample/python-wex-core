from typing import Optional, Union, Literal

from pydantic import BaseModel, Field


class Middleware(BaseModel):
    """Middleware configuration for command execution.
    
    Middlewares can modify the behavior of commands, such as by iterating over
    multiple values for a single option, running in parallel, etc.
    """
    name: str = Field(
    )
    option_name: Optional[str] = Field(
        default=None,
    )
    continue_on_error: bool = Field(
        default=False,
        description="Whether to continue command execution in cas of multiple command runs"
    )
    aggregation_mode: Literal['list', 'last'] = Field(
        default='list',
        description="How to aggregate results from multiple iterations"
    )
    parallel: bool = Field(
        default=False,
        description="Whether to process iterations in parallel"
    )
    limit: Union[int, bool] = Field(
        default=False,
        description="Maximum number of iterations to process, or False for no limit"
    )
    show_progress: bool = Field(
        default=True,
        description="Whether to show a progress indicator during processing"
    )

