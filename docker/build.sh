#!/usr/bin/env bash
# author: Daniel Rode


# Build container
cd "$(dirname "$0")"
podman build --tag silvimetric .
