.PHONY: all build clean clean-frontend package install test

all: node_modules
	npm run build --prefix editor/frontend
	@echo "Cleaning frontend source files..."
	@if [ -d "editor/frontend" ]; then \
		find editor/frontend -mindepth 1 -maxdepth 1 ! -name 'dist' -exec rm -rf {} + 2>/dev/null || true; \
	fi
	@echo "Frontend build complete. Only dist/ remains."

node_modules: editor/frontend/package.json
	npm install -C editor/frontend/

editor/frontend/package.json: editor/frontend/
	git submodule update --remote

editor/frontend/: 
	mkdir -p editor/frontend

clean-frontend:
	@echo "Cleaning frontend source files (keeping dist/)..."
	@if [ -d "editor/frontend" ]; then \
		find editor/frontend -mindepth 1 -maxdepth 1 ! -name 'dist' -exec rm -rf {} +; \
	fi

clean:
	@echo "Cleaning all build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf editor/frontend/node_modules/
	rm -rf editor/frontend/dist/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: all
	@echo "Checking for build module..."
	@python -c "import build" 2>/dev/null || pip install build
	@echo "Building Python package..."
	python -m build

install: build
	pip install -e .

install-cli: build
	pip install -e ".[cli]"

install-shell: build
	pip install -e ".[shell]"

install-editor: build
	pip install -e ".[editor]"

install-all: build
	pip install -e ".[all]"

publish: build
	@echo "Checking for twine..."
	@python -c "import twine" 2>/dev/null || pip install twine
	@echo "Publishing to PyPI..."
	twine upload dist/*

publish-test: build
	@echo "Checking for twine..."
	@python -c "import twine" 2>/dev/null || pip install twine
	@echo "Publishing to TestPyPI..."
	twine upload --repository testpypi dist/*
