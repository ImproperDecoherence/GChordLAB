"""
Module Debug
"""


__author__ = "https://github.com/ImproperDecoherence"


import inspect

_debug_on = False
_debug_filter = set()


def debugIsOn() -> bool:
    global _debug_on

    return _debug_on


def debugFilter() -> list[str]:
    global _debug_filter
    return _debug_filter


def debugOn(on: bool, filter: list[str]):
    global _debug_on
    global _debug_filter

    old = _debug_on

    _debug_on = on
    _debug_filter = set(filter)

    if old != _debug_on:
        if _debug_on:
            print(f"Debug: ON | Filter: {_debug_filter}")
        else:
            print("Debug: OFF")



class _CallerAnalysis:

    def __init__(self):
        caller_frame = inspect.stack()[2]

        self.caller_locals = caller_frame[0].f_locals
        self.caller_instance = self.caller_locals.get('self')
        self.caller_module_name = inspect.getmodule(caller_frame[0]).__name__
        self.caller_function_name =  inspect.currentframe().f_back.f_back.f_code.co_name


    def callerVariables(self) -> dict:
        caller_variables = {name: value for name, value in self.caller_locals.items()}        

        if self.caller_instance:
            caller_class_attributes = {name: value for name, value in self.caller_instance.__class__.__dict__.items()}
            caller_variables.update(caller_class_attributes)

        return caller_variables
    

    def callerModuleName(self):
        return self.caller_module_name


    def callerClassName(self):
        if self.caller_instance:
            caller_class = self.caller_instance.__class__
            return caller_class.__name__
        else:
            return ""


    def callerFunctionName(self):
        return self.caller_function_name
    

    def context(self) -> set[str]:
        class_name = self.callerClassName()
        context = {self.callerModuleName(), self.callerFunctionName()}
        if len(class_name) > 0:
            context.update([class_name])
        return context


    def contextStr(self) -> str:
        class_str = self.callerClassName()
        module_str = self.callerModuleName() + " | "

        if len(class_str) > 0:
            class_str = class_str + "."
            module_str = ""

        return f"{module_str}{class_str}{self.callerFunctionName()}"


    def variableValue(self, variable_name: str):
        return self.callerVariables()[variable_name]


    def matchFilter(self, filter: list[str]) -> bool:
        return any(self.context() & filter)


    def __str__(self):
        return [self.context(), self.callerVariables().keys()].__str__()



def debugPrint(to_print: str, condition: bool = True):

    if debugIsOn() and condition:
        caller_analysis = _CallerAnalysis()
        if caller_analysis.matchFilter(debugFilter()):
            print(caller_analysis.contextStr() + " : " + to_print)


def debugVariable(variable_name: str, condition: bool = True):
    
    if debugIsOn() and condition:
        caller_analysis = _CallerAnalysis()
        if caller_analysis.matchFilter(debugFilter()):
            print(caller_analysis.contextStr() + " : " + variable_name + " = " + str(caller_analysis.variableValue(variable_name)))
            
        
