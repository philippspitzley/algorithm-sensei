from sqlmodel import SQLModel


class Code(SQLModel):
    signal: str | None = None
    stdout: str = ""
    stderr: str = ""
    code: int | None = 0
    output: str = ""
    memory: int = 0
    message: str | None = None
    status: str | None = None
    cpu_time: int = 0
    wall_time: int = 0


class Files(SQLModel):
    name: str
    content: str


class CodeError(SQLModel):
    type: str | None = None
    status_code: int | None = None
    message: str | None = None
    error_snippet: str | None = None
    pointer: str | None = None
    location: str | None = None
    line: str | None = None
    column: str | None = None


class CodeResponse(SQLModel):
    compile: Code | None = None
    run: Code | None = None
    error: CodeError | None = None


class CodeRequest(SQLModel):
    language: str
    version: str
    files: list[Files]
