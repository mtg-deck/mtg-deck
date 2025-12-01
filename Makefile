.PHONY: all build clean clean-frontend package install test

all: node_modules
	npm run build --prefix edhelper/editor/frontend
	@echo "Cleaning frontend source files..."
	@if [ -d "edhelper/editor/frontend" ]; then \
		find edhelper/editor/frontend -mindepth 1 -maxdepth 1 ! -name 'dist' -exec rm -rf {} + 2>/dev/null || true; \
	fi
	@echo "Frontend build complete. Only dist/ remains."

node_modules: edhelper/editor/frontend/package.json
	npm install -C edhelper/editor/frontend/

edhelper/editor/frontend/package.json: edhelper/editor/frontend/
	git submodule update --remote

edhelper/editor/frontend/: 
	mkdir -p edhelper/editor/frontend

clean-frontend:
	@echo "Cleaning frontend source files (keeping dist/)..."
	@if [ -d "edhelper/editor/frontend" ]; then \
		find edhelper/editor/frontend -mindepth 1 -maxdepth 1 ! -name 'dist' -exec rm -rf {} +; \
	fi

clean:
	@echo "Cleaning all build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf edhelper/editor/frontend/node_modules/
	rm -rf edhelper/editor/frontend/dist/
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
