# peer-review-data
Extract LMS peer review data for analysis by external applications.

## Running

### Development

Use Docker compose to run in a local development environment.

1. Copy `config/.env.sample` to `.env` in the root directory of the project.  Edit the file to replace the values contained therein with valid ones for the test environment.  Refer to comments in the file as guides to the appropriate values.

    ```sh
    cp config/.env.sample .env
    vim .env
    ```

1. Use Docker's `compose` tool to build the application, run it, and produce an output file.

    ```sh
    docker compose up --build
    ```

1. Examine the data in the output file, `assessments.json`. 

## Resources

### Canvas API functions

1. `/api/v1/courses/<course_id>` — canvasapi.canvas.Canvas.get_course()
2. `/api/v1/courses/<course_id>/assignments/<assignment_id>` — canvasapi.course.Course.get_assignment()
3. `/api/v1/courses/<course_id>/rubrics/<rubric_id>` — canvasapi.course.Course.get_rubric()
4. `/api/v1/courses/545451/assignments/1747535/submissions` — canvasapi.assignment.Assignment.get_submissions()
5. `/api/v1/courses/<course_id>/search_users` — canvasapi.course.Course.get_users()
