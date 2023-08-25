.PHONY: controller worker run-controller run-worker setup clean prune

VENV = .env
MOUNT_PATH = logs
IP = 127.0.0.1

no-default:
	@echo "Please choose to build/run either controller or worker"
	@echo "make [choice] or make run-[choice] respectively"
	@exit 2

controller:
	docker build -f controller/Dockerfile -t clistribute/controller:latest .

worker:
	docker build -f worker/Dockerfile -t clistribute/worker:latest .

run-controller: controller
	mkdir -p $(MOUNT_PATH)
	docker run -v $(MOUNT_PATH):/var/log/clistribute -v $(MOUNT_PATH):/var/clistribute -p 9600:9600 -p 9601:9601 -p 9602:9602/udp clistribute/controller:latest

run-worker: worker
	mkdir -p $(MOUNT_PATH)
	docker run -v $(MOUNT_PATH):/var/log/clistribute -e CONTROLLER_IP=$(IP) clistribute/worker:latest

setup: requirements.txt
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate

	$(VENV)/bin/pip3 install -r requirements.txt

	ln -s ../shared controller
	ln -s ../shared worker


clean:
	rm -rf $(VENV)
	rm -rf logs
	rm -rf controller/shared
	rm -rf worker/shared
	rm -rf __pycache__

prune:
	docker system prune