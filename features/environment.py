#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE
from unittest import TestCase

TEST_FILENAME = "truss.json"

def before_all(context):
    context.conapp = CliManager("./truss_calculator.py", "> ")
    context.test = TestCase()

def after_all(context):
    context.conapp.close()
    os.remove(TEST_FILENAME)

def before_feature(context, feature):
    pass

def before_scenario(context, scenario):
    if "skip" in scenario.effective_tags:
        scenario.skip("Marked with @skip")
        return

class CliManager:
    """
    Provides interface for interacting with command line application.
    """

    def __init__(self, command, prompt):
        self.prompt = prompt
        self.process = Popen([command], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    def readline(self):
        return self.process.stdout.readline().decode("utf-8").strip()

    def writeline(self, message):
        self.read_prompt()
        self.process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
        self.process.stdin.flush()

    def read_prompt(self):
        prompt = self.process.stdout.read(len(self.prompt)).decode("utf-8")
        if prompt != self.prompt:
            print(f"|{prompt}|", flush=True)
            raise BrokenPipeError(" ".join(self.process.args))

    def close(self):
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)
