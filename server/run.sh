#!/bin/bash

echo "Attempting to build router"
python3 go-builder.py
echo "Starting server"
go run main.go
