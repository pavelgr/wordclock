#!/bin/bash

_child() {
    run() {
        greet $(_greet)
    }

    _greet() {
        echo "hello"
    }

    run
}

boy() {
    greet() {
        echo "$1 boy!"    
    }

    _child
}

world() {
    greet() {
        echo "$1 world!"    
    }

    _child
}

boy
world
