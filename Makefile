#
# Commands to start the application and perform source code checks
#

## Start the application
start:
	FLASK_APP=application FLASK_ENV=development flask run

## Apply black linter to the source tree
black:
	black --exclude ".venv*|.vscode*" .

## Apply mypy type checking, using the rules in mypy.ini
mypy:
	mypy

## Run unit and integration tests and calculate coverage, with the rules defined in pytest.ini
test:
	pytest tests/unit

## List available commands
help:
	@printf "${COLOR_TITLE_BLOCK}${PROJECT} Makefile${COLOR_RESET}\n"
	@printf "\n"
	@printf "${COLOR_COMMENT}Usage:${COLOR_RESET}\n"
	@printf " make [target] [arg=\"val\"...]\n\n"
	@printf "${COLOR_COMMENT}Available targets:${COLOR_RESET}\n"
	@awk '/^[a-zA-Z\-\_0-9\@]+:/ { \
		helpLine = match(lastLine, /^## (.*)/); \
		helpCommand = substr($$1, 0, index($$1, ":")); \
		helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
		printf " ${COLOR_INFO}%-20s${COLOR_RESET} %s\n", helpCommand, helpMessage; \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
