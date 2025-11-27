#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .Stylesheet.Styling import sd, bc
from .Validity import Validation

class Console:
    def __init__(self):
        self.Validator = Validation()

    def Success(self, Message: str) -> None:
        if (self.Validator.NotEmpty(Message)):
            print(f"{sd.sBan} {Message.strip()}{bc.BC}\n")

    def Info(self, Message: str) -> None:
        if (self.Validator.NotEmpty(Message)):
            print(f"{sd.iBan} {Message.strip()}{bc.BC}\n")

    def Error(self, Message: str) -> None:
        if (self.Validator.NotEmpty(Message)):
            print(f"{sd.eBan} {Message.strip()}{bc.BC}\n")

    def Raw(self, Message: str, AppendNewLine: bool = True, IndentMessage = False, End: str = None, Flush: bool = True) -> None:
        if (self.Validator.NotEmpty(Message)):
            RawString = f" {bc.BC}{Message.strip()}{bc.BC}"

            if (IndentMessage):
                RawString = f"\t {RawString}"

            if End is None:
                End = "\n" if AppendNewLine else ""

            print(RawString, end=End, flush=Flush)