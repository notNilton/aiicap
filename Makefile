.PHONY: help setup init-db generate correct gui clean test

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

SIZE ?= 1024x1024
TARGET_SIZE ?= 64x64
PALETTE_SIZE ?= 16
ALPHA_THRESHOLD ?= 128

help:
	@echo "AIICAP Simplified Makefile"
	@echo "--------------------------"
	@echo "make setup    - Create virtual environment and install dependencies"
	@echo "make init-db  - Initialize the SQLite database (data.db)"
	@echo "make generate - Generate an image. Usage: make generate PROMPT='a cat' [SIZE=1024x1024]"
	@echo "make correct  - Restore an image. Usage: make correct INPUT=in.png OUTPUT=out.png [TARGET_SIZE=64x64] [PALETTE_SIZE=16] [ALPHA_THRESHOLD=128]"
	@echo "make gui      - Launch the Gradio web interface"
	@echo "make clean    - Remove the virtual environment, database, and cached files"

setup: $(VENV)/bin/activate init-db

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

init-db: $(VENV)/bin/activate
	$(PYTHON) -c "from database import init_db; init_db()"

generate: $(VENV)/bin/activate
	@if [ -z "$(PROMPT)" ]; then \
		echo "Error: PROMPT is not set. Usage: make generate PROMPT='a pixel art cat'"; \
		exit 1; \
	fi
	$(PYTHON) generate.py "$(PROMPT)" --size $(SIZE)

correct: $(VENV)/bin/activate
	@if [ -z "$(INPUT)" ] || [ -z "$(OUTPUT)" ]; then \
		echo "Error: INPUT or OUTPUT is not set. Usage: make correct INPUT=in.png OUTPUT=out.png"; \
		exit 1; \
	fi
	$(PYTHON) correct.py "$(INPUT)" "$(OUTPUT)" --target-size $(TARGET_SIZE) --palette-size $(PALETTE_SIZE) --alpha-threshold $(ALPHA_THRESHOLD)

gui: $(VENV)/bin/activate
	$(PYTHON) gui_corrector.py

test: $(VENV)/bin/activate
	$(PYTHON) test_setup.py

clean:
	rm -rf $(VENV)
	rm -f data.db
	rm -rf data/uploads
	find . -type d -name __pycache__ -exec rm -r {} +
	@echo "Cleaned environment."
