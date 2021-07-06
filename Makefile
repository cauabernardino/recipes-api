SHELL=/bin/bash

buildup:
	source .env && docker-compose up -d
builddown:
	docker-compose down -v

.PHONY: buildup builddown